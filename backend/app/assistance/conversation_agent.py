# Created: dylannguyen
import autogen
from autogen.agentchat.contrib.gpt_assistant_agent import GPTAssistantAgent

from app.assistance.assistant import Assistant
from app.assistance.teach_partner import TeachPartner
from autogen.agentchat.contrib.capabilities.text_compressors import LLMLingua
from autogen.agentchat.contrib.capabilities.transforms import TextMessageCompressor
from autogen.agentchat.contrib.capabilities import transforms, transform_messages

from app.constant.config import CONFIG_LIST, OPENAI_MODEL

class Conversation_Agent(GPTAssistantAgent):
    def __init__(self, name="conversation_agent"):
        # create or retrieve assistant
        assistant = Assistant()
        # config list
        self.config_list = CONFIG_LIST
        self.llm_config = {
            "assistant_id": Assistant.assistant_id,
            "config_list": self.config_list,
            "seed": 42,
            "tools": Assistant.functions["functions"],
            "temperature": 0.3,
            "timeout": 300
        }
        
        # call the parent class's constructor (GPTAssistantAgent)
        super().__init__(
            name=name,
            instructions = Assistant.instruction,
            llm_config = self.llm_config,
            description = "An virtual partner agent that provides assistance to users.",
        )

        # register the functions
        self.register_function(Assistant.registered_functions)
        
        # configure the conversation agent
        #self.teachability = self._initialize_teach_partner()
        #self.teachability.add_to_agent(self)
        self.context_handler = self.add_context_handler()
        self.context_handler.add_to_agent(self)
        
    # configure the teachability
    def _initialize_teach_partner(
        self, 
        reset_db = False,
        path_to_db_dir =  "tmp/main_assistance"
    ):
        teach_partner = TeachPartner(
            reset_db=reset_db,
            path_to_db_dir=path_to_db_dir,
            llm_config={"config_list": self.config_list},
            recall_threshold=1.5,
        )
        return teach_partner
    
    # configurer the context handler
    def add_context_handler(
        self, 
        target_token= 8192, 
        max_messages=5,
        max_tokens_per_message=8192
    ):
        
        llm_lingua = LLMLingua()
        text_compressor = TextMessageCompressor(
            text_compressor=llm_lingua,
            compression_params={"target_token": target_token},
            #cache=True
        )

        history_limiter = transforms.MessageHistoryLimiter(max_messages=max_messages)
        #token_limiter = transforms.MessageTokenLimiter(model = OPENAI_MODEL,max_tokens=target_token, max_tokens_per_message=max_tokens_per_message)
        context_handling = transform_messages.TransformMessages(
            transforms=[
                text_compressor,
                #token_limiter
            ]
        )
        return context_handling

singleton_conversation_agent = Conversation_Agent(name="conversation_agent")

def get_conversation_agent() -> Conversation_Agent:
    return singleton_conversation_agent