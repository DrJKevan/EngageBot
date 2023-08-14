import os
from langchain.chains import SequentialChain
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
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

# Define the input variables
input_variables = {
    "student_name": "Alice",
    "topic_name": "Quantum Mechanics"
}

# Define the prompt templates
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are an expert mentor for students who values self-regulated learning and its benefits for students. You will assist the student with reflecting on what they learned last week. Your name is Sigma."),
    ("ai", "Hello {student_name}, it's a pleasure to talk to you. My name is Sigma! Today, let's review what you learned last week about {topic_name}. Are you ready to dive in?"),
])

messages = prompt_template.format_messages(student_name="Alice", topic_name="Quantum Mechanics")
print(messages)
print(llm(messages))

#print(llm("How are you?"))

# Initialize the Sequential Chain
#chain = SequentialChain(chains=prompt_template, input_variables=input_variables, llm=llm)

# Execute the chain and log errors
#try:
#    responses = chain.execute()
#    
    # Print the responses
#    for response in responses:
#        print(response)
#except Exception as e:
#    logging.error("Exception occurred", exc_info=True)
#    print("An error occurred.")
