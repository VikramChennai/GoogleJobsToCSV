import os
from dotenv import load_dotenv
from openai import AzureOpenAI, AsyncAzureOpenAI

load_dotenv()

api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

syncAzureOpenAIClient = AzureOpenAI(
    api_key=api_key, api_version=api_version, azure_endpoint=azure_endpoint
)

asyncAzureOpenAIClient = AsyncAzureOpenAI(
    api_key=api_key, api_version=api_version, azure_endpoint=azure_endpoint
)
