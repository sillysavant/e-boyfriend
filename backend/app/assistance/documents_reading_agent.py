# Created: dylannguyen
from autogen import AssistantAgent
from app.constant.config import CONFIG_LIST
from app.services.azure_ai_search_service import get_results_vector_search

class DocumentReadingAgent(AssistantAgent):
    def __init__(self):
        super().__init__(
            name="document_reading_agent",
            llm_config={"config_list": CONFIG_LIST},
            description="An agent that retrieve relevant information to user's message using *semanic search* on the documents.",
            system_message = """
                Your role is to retrieve relevant documents used to answer user's message using *semanic search* on the documents.
                If there is any conflict in the information, you should provide the most recent information based on the createdat field.
                Respond with the relevant information from the documents. If there is no relevant information, respond with "No relevant information found."
                Keep the answer concise. 
                """
        )
        #self.register_for_llm(name="get_results_vector_search", description="Search relevant information, either user information (index_name=user_info) or uploaded docs (index_name=user_docs), and return the content.")(get_results_vector_search)
        
    async def get_relevant_information(self, message: str, index_name: str) -> str:
        search_result = await get_results_vector_search(query=message, index_name=index_name)
        doc_message = f"""
        Provide user information and ensure the information is relevant to the user's message. Do NOT answer the message, just provide user relevant information if it exists. \n

        Retrieved relevant information: {search_result}\n
        User's message: {message}
        """
        response = await self.a_generate_reply(messages = [{"role": "user", "content": doc_message}])
        return response.strip()
        
        
singleton_document_reading_agent = DocumentReadingAgent()

def get_document_reading_agent() -> DocumentReadingAgent:
    return singleton_document_reading_agent