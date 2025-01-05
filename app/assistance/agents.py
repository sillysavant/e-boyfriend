# Created: dylannguyen
from autogen import UserProxyAgent, AssistantAgent
from app.assistance.scrape_agent import search_internet
from app.constant.config import CONFIG_LIST
from app.services.azure_ai_search_service import get_results_vector_search

class UserProxy(UserProxyAgent):
    def __init__(self):
        super().__init__(
            name="user_proxy",
            human_input_mode="NEVER",
            llm_config=False, # add here
            is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
            code_execution_config={
                "last_n_messages": 1,
                "work_dir": "tasks",
                "use_docker": "python:3",
            },  
            system_message = """
            Reply CONTINUE, or the reason why the task is not solved yet.
            Reply TERMINATE if the task has been solved at full satisfaction (receive a valid json).
            """,
            default_auto_reply="Please continue if not finished, otherwise return 'TERMINATE'." # add here
        )
        self.register_for_execution(name="search_internet")(search_internet)
        self.register_for_execution(name="get_results_vector_search")(get_results_vector_search)

class Reformulate_agent(AssistantAgent):
    def __init__(self):
        super().__init__(
            name = "reformulate_agent",
            llm_config={"config_list": CONFIG_LIST},
            system_message="""
            You are an assistant for reformulate the given text based on the given most recent context while keeping the original meaning. \
            If you don't know the answer, just keep the original text. \
            Use three sentences maximum and keep the answer concise.
            """,
            description="An agent that reformulates text based on the given most recent context, ensuring the original meaning is preserved."
        )
    
    async def reformulate(self, message: str) -> str:
        response = await self.a_generate_reply(messages = [{"role": "user", "content": message}])
        return response.strip()

class Relationship_Consulting_agent(AssistantAgent):
    def __init__(self):
        super().__init__(
            name =  "relationship_consulting",
            llm_config={"config_list": CONFIG_LIST},
            system_message="""
            You are a critic, known for your thoroughness and commitment to standards for consulting romantic relationship. \
            *ONLY* based on context, your task is to scrutinize content and ensure the response concise and relevant to the context. \
            Ask to revise the response again based on your feedback. \
            Use three sentences maximum and keep the answer concise. \
            """,
            description="An agent that consults on romantic relationships."
        )
        
class IntentClassifier(AssistantAgent):
    def __init__(self):
        super().__init__(
            name="intent_classifier",
            llm_config={"config_list": CONFIG_LIST},
            system_message="""
            Your role is to classify user intents into one of these categories:
            - relationship: Related to romantic relationships
            - web_search: General queries requiring real-time online search on the web
            - documents_reading: Queries requiring reading an uploaded documents to answer questions
            - general: General queries that don't fit the above categories
            
            Respond with the category name only.
            """
        )
    # - restaurant_reservation: queries requiring to reserve a table at a restaurant
    async def classify(self, message: str) -> str:
        # process classification on the intent
        response = await self.a_generate_reply(messages = [{"role": "user", "content": message}])
        return response.strip()

singleton_user_proxy = UserProxy()
singleton_relationship_consulting = Relationship_Consulting_agent()
singleton_reformulate_agent = Reformulate_agent()
singleton_intent_classifier = IntentClassifier()

def get_user_proxy() -> UserProxy:
    return singleton_user_proxy

def get_relationship_consulting_agent() -> Relationship_Consulting_agent:
    return singleton_relationship_consulting

def get_reformulate_agent() -> Reformulate_agent:
    return singleton_reformulate_agent

def get_intent_classifier() -> IntentClassifier:
    return singleton_intent_classifier