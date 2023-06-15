import os
from langchain.llms import OpenAI
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

# Specify the path to the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

# Load the .env file
load_dotenv(dotenv_path)

# Set the OpenAI API Key
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI Class
llm = OpenAI(openai_api_key=api_key)

# Build a Language Model Application
text = "What would be a good company name for a company that makes colorful socks?"
try:
    response = llm(text)
    print(response)
except Exception as e:
    logging.error("Exception occurred", exc_info=True)
