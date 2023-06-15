import os
from langchain.llms import OpenAI
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env

# Initialize the OpenAI Class
llm = OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))

# Build a Language Model Application
text = "What would be a good company name for a company that makes colorful socks?"
response = llm(text)

print(response)
