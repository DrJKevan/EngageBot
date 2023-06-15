import os
from langchain.llms import OpenAI
from dotenv import load_dotenv

# Specify the path to the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

# Load the .env file
load_dotenv(dotenv_path)

api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key: {api_key}")  # print the API key to check if it's correctly loaded

# Initialize the OpenAI Class
llm = OpenAI(openai_api_key=api_key)

# Build a Language Model Application
text = "What would be a good company name for a company that makes colorful socks?"
response = llm(text)

print(response)
