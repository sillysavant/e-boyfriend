# Created: dylannguyen
import json
import autogen
from autogen.agentchat.contrib.gpt_assistant_agent import GPTAssistantAgent
from fastapi import Depends, HTTPException, status
from app.assistance.agents import IntentClassifier, Reformulate_agent, Relationship_Consulting_agent, UserProxy
from app.assistance.conversation_agent import Conversation_Agent
from app.assistance.documents_reading_agent import DocumentReadingAgent
from app.assistance.scrape_agent import WebSearchAgent, get_current_date_time
from app.constant.config import CONFIG_LIST
from app.database.query import db_message
from autogen.agentchat.contrib.capabilities.text_compressors import LLMLingua
from autogen.agentchat.contrib.capabilities.transforms import TextMessageCompressor
from sqlalchemy.ext.asyncio import AsyncSession
import re

from app.services.azure_ai_search_service import get_results_vector_search
async def add_assistant_message(db:AsyncSession, session_id: str, response):
    try:
        response_json = json.loads(response[-1].chat_history[-1]['content'])
        message = ""
        try:
            mess_list = response_json['messages']
        except KeyError:
            mess_list = response_json['responses']
        except KeyError:
            mess_list = response_json["response"]
        for mess in mess_list:
            message += mess['text'] + "\n"
        if message:
            await db_message.add_messages(db=db, session_id=session_id, role="assistant", content=message)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to decode the response from the assistant"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

async def add_user_message(db:AsyncSession, session_id: str, message: str):
    await db_message.add_messages(db=db, session_id=session_id, role="user", content=message)
    
    
async def get_context(db:AsyncSession, session_id: str, query: str, target_token: int = 4096):
    # get recent chat history
    messages_history = await db_message.load_session_history(db=db,session_id=session_id, limit=10)
    
    recent_context = ""
    for i in range(len(messages_history)-1,-1,-1):
        mess = messages_history[i]
        recent_context += (f"[{mess.created_at}] \'{mess.role}\': {mess.content}\n")
    
    # get similar messages
    similar_messages = await db_message.retrieve_similar_messages(db=db, session_id=session_id, query=query)
    similar_context = ""
    for mess in similar_messages:
        similar_context += (f"[{mess['created_at']}] \'{mess['role']}\': {mess['content']}\n")
    
    llm_lingua = LLMLingua()
    text_compressor = TextMessageCompressor(
        text_compressor=llm_lingua,
        compression_params={"target_token": target_token},
        #cache=True
    )
    
    compressed_rec_text = text_compressor.apply_transform([{"content": recent_context}])
    rec_context = compressed_rec_text[0]["content"]
    #print(f"recent_context before: {recent_context}")
    #print(f"rec_context after: {rec_context}")
    compressed_sim_text = text_compressor.apply_transform([{"content": similar_context}])
    sim_context = compressed_sim_text[0]["content"]
    #print(f"sim_context before: {similar_context}")
    #print(f"sim_context after: {sim_context}")
    
    return rec_context, sim_context

async def get_contextualize_q_system_prompt(problem: str, rec_context: str):
    contextualize_q_system_prompt = f"""
    User: \"{problem}\" \n
    Given the most recent messages in the chat history as context, reformulate the user's message to be a standalone message that can be understood without the chat history. Ensure that the original meaning is preserved. Do NOT answer the message, just reformulate it if needed and otherwise return it as is. \n
    <context>{rec_context}<context>
    """
    return contextualize_q_system_prompt

async def get_qa_system_prompt(problem: str, rec_context: str, sim_context: str, relevant_info: str,reformulated_message: str):
    qa_system_prompt = f"""
    Current time: {await get_current_date_time()} \n
    Use the following pieces of retrieved context and its time to answer the message. \n
    
    User's orginal message: \"{problem}\" \n
    Reformulated message: \"{reformulated_message}\" \n
    <Recent Context>{rec_context}<Recent Context> \n
    <Similar Context>{sim_context}<Similar Context> \n
    <Relevant User Information>{relevant_info}<Relevant User Information>
    """
    return qa_system_prompt

def reflection_message(recipient, messages, sender, config):
        print(f"Relationship Consulting Agent Reflecting ...", "yellow")
        message = """
            Reflect and provide critique on the above response from a partner to user's message below. \
            Your feedback MUST be based solely on the related context provided below and should not include general feedback or suggestions unrelated to context. \
            Tailor your feedback specifically based on these criteria: use daily life, concise, informal language. \
            Ask the partner to revise the response again based on your feedback, ensuring it relevant to their lover's question or statement, and the provided context. \
        """
        try:
            last_message = recipient.chat_messages_for_summary(sender)[-1]['content']
            last_message = json.loads(last_message)
            last_message_json = last_message['messages']
        except KeyError:
            last_message_json = last_message['responses']
        except KeyError:
            last_message_json = last_message["response"]
        
        response = " ".join(item['text'] for item in last_message_json)
        
        user_said = recipient.chat_messages_for_summary(sender)[0]['content']
        match = re.search(r"User:\s\"(.*?)\"", user_said)
        if match:
            user_said = match.group(1)
            
        return f"""
        Partner response: {response} \n
        {message} \n
        User: {user_said} \n
        
        """
        
def generate_request_to_recipient(
    agent,
    message: str,
    clear_history: bool = True,
    summary_method: str = "last_msg",
    max_turns: int = 1,
    carry_over: str = None,
):
    return {
            "recipient": agent, 
            "message": message, 
            "clear_history": clear_history, 
            "carry_over": carry_over,
            "summary_method": summary_method, 
            "max_turns": max_turns
        }
    
async def reset_agent(agents: list):
    for agent in agents:
        agent.reset()

async def chat(
    db: AsyncSession, 
    message: str, 
    session_id: str,
    user_proxy: UserProxy,
    relationship_consulting: Relationship_Consulting_agent,
    reformulate_agent: Reformulate_agent,
    conversation_agent: Conversation_Agent,
    web_search_agent: WebSearchAgent,
    intent_classifier: IntentClassifier,
    document_reading_agent: DocumentReadingAgent
):
    # get context from db
    rec_context, sim_context = await get_context(db=db, session_id=session_id, query=message)
    contextualize_q_system_prompt = await get_contextualize_q_system_prompt(problem=message, rec_context=rec_context)
    
    # reformulate user's input, classify intent
    print(f"Contextualize Q System Prompt: {contextualize_q_system_prompt}")
    reformulated_message = await reformulate_agent.reformulate(message=contextualize_q_system_prompt)
    print(f"Reformulated message: {reformulated_message}")
    
    classification_message = f"Original message: '{message}'. Message with context: '{reformulated_message}'"
    classification_result = await intent_classifier.classify(message=classification_message)
    print(f"Intent Classification Result: {classification_result}")
    
    # Document reading or User Info seach
    if "documents_reading" in classification_result:
        relevant_info = await document_reading_agent.get_relevant_information(message=reformulated_message, index_name="user_docs")
    else:
        relevant_info = await document_reading_agent.get_relevant_information(message=reformulated_message, index_name="user_info")
    print(f"Relevant Information: {relevant_info}")
    
    # Sequential chat configuration
    user_proxy.register_nested_chats(
        chat_queue= [
            {
                "recipient": relationship_consulting, 
                "clear_history": True,
                "message": reflection_message,
                "summary_method": "last_msg", 
                "max_turns": 1
            }
            ],
        trigger=conversation_agent
    )
    
    chat_queue = []
    if "web_search" in classification_result:
        web_search_message = f"""
        Current time: {await get_current_date_time()}. 
        Original message: '{message}'. 
        Message with context: '{reformulated_message}'
        Relevant information from knowledge base: '{relevant_info}'
        """
        chat_queue.append(generate_request_to_recipient(agent=web_search_agent, message=web_search_message, max_turns=2))
    
    qa_system_prompt = await get_qa_system_prompt(problem=message, rec_context=rec_context, sim_context=sim_context, relevant_info = relevant_info, reformulated_message=reformulated_message)
    chat_queue.append(generate_request_to_recipient(agent=conversation_agent, message=qa_system_prompt, max_turns=2))
        
    # chat with agents
    res = user_proxy.initiate_chats(chat_queue=chat_queue)
    return res
