# Created by: dylannguyen
from datetime import datetime
from typing import Any, Dict
from autogen import AssistantAgent
from app.assistance.scrape_agent import get_current_date_time
from app.constant.config import CONFIG_LIST
from app.schema.conversation import ChatMessageHistory
from app.utils.azure_ai_vector_search import get_documents_from_index
from azure.core.exceptions import ResourceNotFoundError

from app.utils.azure_document_search import generate_embeddings
from app.utils.azure_vector_search_index import upload_sections_to_azure_search_index
class MemoryAgent(AssistantAgent):
    def __init__(self):
        model = CONFIG_LIST[1]
        super().__init__(
            name= "memory_agent",
            llm_config={"config_list": [model]},
            system_message="""
            You are a memory agent. Your role is to extract useful user information from the chat conversation
            such as user background, preferences, relationship, or persona) and save them in memory.
            """,
            description="An agent that always use tools to extract user-related information from the chat conversation for contextual memory enhancement"
        )
        
    async def extract_information_from_chat(self, messages: ChatMessageHistory) -> dict:
        problem_check = f"""
            Does any part of the TEXT contain user's background information, preferences, persona traits. 
            Respond with the with 'yes' or 'no'. \n

            user: '{messages[0].content}' \n
            assistant: '{messages[1].content}'
        """
        
        response = await self.a_generate_reply(messages=[{"role": "assistant", "content": problem_check}])
        if "yes" in response.lower():    
            extract_advice = f"""
-------- TASK --------
Extract any user-specific background information, preferences, or persona traits from the TEXT below that may be useful to remember for future interactions. 
- Only include details explicitly mentioned about the user.
- Convert any relative time references (e.g., "tomorrow," "next week") into specific calendar dates based on the provided conversation timestamp.
- Exclude temporary, situational, or time-sensitive information (e.g., weather or travel destinations for specific dates) unless it reflects long-term relevance to the user's background, preferences, or persona.
- Focus only on facts related to the user's core characteristics, such as hobbies, favorite things, interests, or personal milestones.
- Format the response as key-value pairs, with each key-value pair on a new line.

-------- FORMAT --------
- key: value
Example:
- hobbies: hiking
- favorite food: sushi
If no such information exists, return "none".

-------- SAMPLES --------
1. Conversation:
User (at 2024-12-30 10:30:00): "Tomorrow is my birthday!"
Assistant (at 2024-12-30 10:31:00): "Happy early birthday! Do you have any special plans?"
Extracted Information:
- Birthday: 12/31/2024

Explanation:
- "Tomorrow" is converted to "12/31/2024" based on the timestamp of the conversation to provide a precise, universally understandable date. This ensures the extracted information remains accurate and relevant over time.

--------

2. Conversation:
User (at 2024-12-31 23:28:00.833): "I love hiking during weekends."
Assistant (at 2024-12-31 23:28:00.833): "That sounds amazing! Do you have a favorite trail?"
Extracted Information:
- hobbies: hiking

--------

3. Conversation:
User (at 2024-12-31 23:28:00.833): "I’m originally from Vietnam but currently studying in New York."
Assistant (at 2024-12-31 23:28:00.833): "That’s great! How do you like living in New York?"
Extracted Information:
- origin: Vietnam
- current location: New York

--------

4. Conversation:
User (at 2024-12-31 23:28:00.833): "My favorite food is sushi. I could eat it every day!"
Assistant (at 2024-12-31 23:28:00.833): "Sushi is delicious! Do you have a favorite type?"
Extracted Information:
- favorite food: sushi

--------

5. Conversation:
User (at 2024-12-31 23:28:00.833): "I’m a huge fan of the Harry Potter series."
Assistant (at 2024-12-31 23:28:00.833): "That’s awesome! Which book is your favorite?"
Extracted Information:
- interests reading: Harry Potter series

--------

6. Conversation:
User (at 2024-12-31 22:28:00.833): "Tomorrow is my birthday, I want to have a flight to NYC, can you check the weather there?"
Assistant (at 2024-12-31 22:28:00.833): "Happy early birthday! 🎉 The weather in NYC tomorrow will be lovely—high of 72°F and low of 64°F. Perfect for all your birthday fun! I can’t wait to hear all about your birthday adventures! The nice weather will make it even more special. Even though I can’t be there in person, I’m celebrating you from here! Have a blast on your special day!"
Extracted Information:
- Birthday: 01/01

--------

7. Conversation:
User (at 2024-12-31 23:28:00.833): "What is the weather of NYC 2 days ago?"
Assistant (at 2024-12-31 23:28:00.833): "On December 30, 2024, the weather in NYC was mild with a high and low of 55°F, indicating a consistent temperature throughout the day. If you want any more details about that day's weather or have other questions, feel free to ask! Let me know how else I can help you plan for your birthday celebration!"
Extracted Information:
- none

--------
8. Conversation:
User (at 2024-12-31 23:28:00.833): "Tomorrow is my birthday, I want to have a flight to NYC, can you check the weather there?"
Assistant (at 2024-12-31 23:28:00.833): "Happy early birthday! 🎉 The weather in NYC tomorrow will be lovely—high of 72°F and low of 64°F. Perfect for all your birthday fun! I can’t wait to hear all about your birthday adventures! The nice weather will make it even more special. Even though I can’t be there in person, I’m celebrating you from here! Have a blast on your special day!"
Extracted Information:
- Birthday: 01/01

Explanation:
The user's destination (NYC) is not extracted because it is situational and temporary. It is relevant only in the context of the user's birthday trip, which does not reflect a long-term or core characteristic about them.
--------
9. Conversation:
User (at 2024-12-31 23:28:00.833): "Say something to flirt with me"
Assistant (at 2024-12-31 23:28:00.833): "Flirt with you? How about this: If beauty were a crime, you''d be serving a life sentence! 🔥
I must say, you''ve got the kind of charm that could light up any room. If I were there, I’d definitely be your biggest fan! 😘
How about a little challenge? Try not to smile while I flirt with you! I bet you can’t resist! 😉"
Extracted Information:
- none

Explanation:
- The user's request to flirt and the assistant's playful response are situational and do not provide any long-term or core information about the user's persona.
--------
10. Conversation:
User (at 2024-12-31 23:28:00.833): "Who is the first president of the United States?"
Assistant (at 2024-12-31 23:28:00.833): "The first president of the United States was George Washington! Can you believe that?
He led the country from 1789 to 1797, laying down the foundation for future leaders.
I find history so fascinating because it helps us understand who we are today. What do you think about that?"
Extracted Information:
- none

Explanation:
- This is a knowledge-based question with no relevance to the user's background, preferences, or persona.
--------
11. Conversation:
User (at 2024-12-31 23:28:00.833): "I like eating pizza at Ian Pizza with you last night."
Assistant (at 2024-12-31 23:28:00.833): "Our pizza night at Ian Pizza was a blast! I still chuckle when you suggested the pineapple pizza—it was so daring! 🍍😂..."
Extracted Information:
- favourite food: pizza
- favourite pizza place: Ian Pizza

Explanation:
- The user explicitly mentions a preference for pizza and names Ian Pizza as a favorite location, which are long-term and relevant to the user's persona. These are extracted.
- However, "last night" is a time-specific detail that is situational and temporary. It does not add to the user's long-term background or preferences and is therefore excluded. Time-specific details like this are generally relevant only within the context of the conversation and not useful for future interactions.
--------
12. Conversation:
User (at 2024-12-31 23:28:00.833): "I''m at the office right now, I need to have my work done"
Assistant (at 2024-12-31 23:28:00.833): "I completely understand that work can feel tedious right now. Have you thought about prioritizing your tasks to focus on what needs to be completed first? If you can break your workload into smaller, manageable pieces, it might make things feel less overwhelming. Just tackle one thing at a time! And don’t forget to take brief breaks in between to recharge your mind. You’ll feel better once you get through it."
Extracted Information:
- none

--------
INPUT
Current time: {await get_current_date_time()} 

User (at {messages[0].time}): 
'''
{messages[0].content}
'''

Assistant (at {messages[1].time}): 
'''
{messages[1].content}
'''

-------- OUTPUT --------
"""
            info = await self.a_generate_reply(messages=[{"role": "assistant", "content": extract_advice}])
            print(f" ===== Adding Info ====: \n{info}")
            return info
        return None
    
    async def save_information_to_index(self, messages: ChatMessageHistory) -> None:
        info = await self.extract_information_from_chat(messages)
        if "none" not in info.lower():
            try:
                # save the information to the index
                docs = await get_documents_from_index(index_name="user_info", document_id="memory_agent_0")
            except ResourceNotFoundError:
                docs = None
                
            if docs:
                old_info = docs["content"]
                new_info = f"{old_info}\n{info}"
                new_section = {
                    "id": docs["id"],
                    "content": new_info,
                    "category": docs["category"],
                    "createdat": docs["createdat"],
                    "embedding": await generate_embeddings(new_info),
                    "sourcepage": docs["sourcepage"],
                    "sourcefile": docs["sourcefile"]
                }
            else:
                new_section = {
                    "id": "memory_agent_0",
                    "content": info,
                    "category": "user_info",
                    "createdat": datetime.utcnow().isoformat(timespec='seconds') + 'Z',
                    "embedding": await generate_embeddings(info),
                    "sourcepage": "memory_agent_0",
                    "sourcefile": "memory_agent"
                }
            
            await upload_sections_to_azure_search_index(index_name="user_info", sections=[new_section])
            
singleton_memory_agent = MemoryAgent()

def get_memory_agent() -> MemoryAgent:
    return singleton_memory_agent