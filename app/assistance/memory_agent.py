# Created by: dylannguyen
from autogen import AssistantAgent

from app.constant.config import CONFIG_LIST
from app.schema.conversation import ChatMessageHistory

class MemoryAgent(AssistantAgent):
    def __init__(self):
        super().__init__(
            name= "memory_agent",
            llm_config={"config_list": CONFIG_LIST},
            system_message="""
            You are a memory agent. Your role is to extract useful user information from the chat conversation
            such as user background, preferences, relationship, or persona) and save them in memory.
            """,
            description="An agent that always use tools to extract user-related information from the chat conversation for contextual memory enhancement"
        )
        
    async def extract_information_from_chat(messages: ChatMessageHistory) -> dict:
        """Extract useful information from the chat conversation"""
        conversation_history = f"""
            Find any part of the conversation that contains. 
            Respond with the . If there is no relevant information, respond with empty list.
        """
        
    
    