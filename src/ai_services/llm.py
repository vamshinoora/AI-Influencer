import os
import openai
from dotenv import find_dotenv, load_dotenv
import base64
import requests

from langchain_openai import AzureChatOpenAI
import traceback
from langchain.schema import HumanMessage
# from langchain_community.prompts import ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables from the .env file
# Get the project root directory (two levels up from this file)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

# Initialize llm variable
llm = None

try:
    # Retrieve Azure OpenAI credentials from environment variables
    client_id = os.getenv("AZURE_OPENAI_CLIENT_ID")
    client_secret = os.getenv("AZURE_OPENAI_CLIENT_SECRET")
    CISCO_OPENAI_APP_KEY = os.getenv("AZURE_OPENAI_APP_KEY")

    # Check if all required credentials are available
    if not all([client_id, client_secret, CISCO_OPENAI_APP_KEY]):
        print("⚠️ Azure OpenAI credentials not found in environment variables")
        print("Required: AZURE_OPENAI_CLIENT_ID, AZURE_OPENAI_CLIENT_SECRET, AZURE_OPENAI_APP_KEY")
        raise ValueError("Missing Azure credentials")
    
    # Check for placeholder values
    if any(cred in ["your_azure_client_id_here", "your_azure_client_secret_here", "your_azure_app_key_here"] 
           for cred in [client_id, client_secret, CISCO_OPENAI_APP_KEY]):
        print("⚠️ Azure OpenAI credentials contain placeholder values")
        raise ValueError("Placeholder Azure credentials detected")

    # Define the URL and payload for obtaining an OAuth token
    url = "https://id.cisco.com/oauth2/default/v1/token"
    payload = "grant_type=client_credentials"

    # Encode client ID and secret for Basic Authentication
    value = base64.b64encode(f'{client_id}:{client_secret}'.encode('utf-8')).decode('utf-8')

    # Define headers for the token request
    headers = {
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {value}"
    }

    # Make a POST request to obtain the OAuth token
    token_response = requests.request("POST", url, headers=headers, data=payload)
    
    if token_response.status_code != 200:
        print(f"⚠️ Azure token request failed: {token_response.status_code}")
        raise ValueError(f"Token request failed with status {token_response.status_code}")

    # Define the user ID for the Azure OpenAI API
    CISCO_BRAIN_USER_ID = 'vnoora'

    # Initialize the AzureChatOpenAI instance with the obtained token and other configurations
    llm = AzureChatOpenAI(
        deployment_name="gpt-4o-mini",
        azure_endpoint='https://chat-ai.cisco.com',
        api_key=token_response.json()["access_token"],
        api_version="2025-01-01-preview",
        model_kwargs=dict(
            user=f'{{"appkey": "{CISCO_OPENAI_APP_KEY}", "user": "{CISCO_BRAIN_USER_ID}"}}'
        )
    )
    
    print("✅ Azure OpenAI LLM initialized successfully")

except Exception as e:
    print(f"❌ Failed to initialize Azure OpenAI LLM: {e}")
    llm = None

# Function to test if LLM is available
def is_llm_available():
    """Check if the LLM is properly initialized"""
    return llm is not None

# Function to get LLM instance
def get_llm():
    """Get the LLM instance if available"""
    return llm

