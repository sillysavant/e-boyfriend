import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_MODEL = "gpt-4o-mini"
OPENAPI_KEY = os.getenv("OPEN_API_KEY")
ELEVENLABS_API_KEY=os.getenv("ELEVENLABS_API_KEY")
SECRET_KEY=os.getenv("SECRET_KEY")
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_REGION_SERVICE =  os.getenv("AZURE_REGION_SERVICE")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
#API_KEY = os.getenv("AZURE_API_KEY")
# AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_ENDPOINT")
# DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_COMPLETIONS_NAME")
#API_KEY="8JQjqWEYNJTezeAkqzzqhqIC6LB6P916KgOZ6k9dN6sES1gT7jLUJQQJ99AKACHYHv6XJ3w3AAABACOGZMCi"
#AZURE_OPENAI_ENDPOINT="https://ai-assistant-pre.openai.azure.com/"
# client = AzureOpenAI(
#     api_key = API_KEY,  
#     api_version="2024-07-18",
#     azure_endpoint = AZURE_OPENAI_ENDPOINT
# )