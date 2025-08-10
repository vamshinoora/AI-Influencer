import os
import openai
from dotenv import find_dotenv, load_dotenv
from langchain_community.llms import OpenAI

load_dotenv(find_dotenv())

client = openai.OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

response = client.responses.create(
    model="llama-3.3-70b-versatile",
    input=input("Enter your prompt: "),
)

print(response.output_text)