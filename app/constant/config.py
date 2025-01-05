import os
import autogen
from dotenv import load_dotenv

load_dotenv()

OPENAI_MODEL = "gpt-4o-mini"
OPENAPI_KEY = os.getenv("OPEN_API_KEY")
ELEVENLABS_API_KEY=os.getenv("ELEVENLABS_API_KEY")
SECRET_KEY=os.getenv("SECRET_KEY")
DB_CONNECTION_URL = os.getenv("DB_CONNECTION_URL")
COSMOS_CONNECTION_URL = os.getenv("COSMOS_CONNECTION_URL")
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_REGION_SERVICE =  os.getenv("AZURE_REGION_SERVICE")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
REDIS_URL = os.getenv("REDIS_URL")
CONFIG_LIST = autogen.config_list_from_json('app/constant/OAI_CONFIG_LIST.json')
#TAVILY_KEY = os.getenv("TAVILY_KEY")
APIFY_KEY = os.getenv("APIFY_KEY")
RDS_CERT_PATH = os.getenv("RDS_CERT_PATH")

AZURE_AI_SEARCH_KEY = os.getenv("AZURE_AI_SEARCH_KEY")
AZURE_AI_SEARCH_URI = os.getenv("AZURE_AI_SEARCH_URI")
AZURE_AI_SEARCH_INDEX_NAME = os.getenv("AZURE_AI_SEARCH_INDEX_NAME")
AZURE_EMBEDDING_KEY = os.getenv("AZURE_EMBEDDING_KEY")
AZURE_EMBEDDING_URI = os.getenv("AZURE_EMBEDDING_URI")
AZURE_DOC_INTELL_KEY = os.getenv("AZURE_DOC_INTELL_KEY")
AZURE_DOC_INTELL_URI = os.getenv("AZURE_DOC_INTELL_URI")
AZURE_BLOB_KEY= os.getenv("AZURE_BLOB_KEY")
AZURE_BLOB_URI= os.getenv("AZURE_BLOB_URI")
AZURE_BLOB_CONTAINER_NAME= os.getenv("AZURE_BLOB_CONTAINER_NAME")
AZURE_BLOB_ACCOUNT_NAME = os.getenv("AZURE_BLOB_ACCOUNT_NAME")