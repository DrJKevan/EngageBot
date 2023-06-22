import os
from langchain.chains import SequentialChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
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
prompt_templates = [
    PromptTemplate(template={"role": "system", "content": "Hello {student_name}, my name is Charles! Today, let's review what you learned last week about {topic_name}. Are you ready to dive in?"}, input_variables=["student_name", "topic_name"]),
    PromptTemplate(template={"role": "user", "content": "Yes, I'm ready."}, input_variables=[]),
    PromptTemplate(template={"role": "system", "content": "Awesome! Can you try to summarize what you learned last week about {topic_name}? I'm here to help make sure you’ve got all the key concepts!"}, input_variables=["topic_name"]),
    PromptTemplate(template={"role": "user", "content": "Quantum mechanics is about the behavior of particles at the atomic level."}, input_variables=[]),
    PromptTemplate(template={"role": "system", "content": "Great job summarizing! Now, for a quick follow-up: Can you think of a real-life application of this concept?"}, input_variables=[]),
    PromptTemplate(template={"role": "user", "content": "Quantum mechanics is used in MRI machines in hospitals."}, input_variables=[]),
    PromptTemplate(template={"role": "system", "content": "That's an excellent example! You're really getting the hang of this material. Before we wrap up, here's the instructor's summary for comparison: [Instructor's summary]. You did fantastic today! Keep up the great work, and good luck with your studies this week. If you want to continue chatting or have any questions, feel free to stick around!"}, input_variables=[])
]

# Initialize the Sequential Chain
chain = SequentialChain(chains=prompt_templates, input_variables=input_variables, llm=llm)

# Execute the chain and log errors
try:
    responses = chain.execute()
    
    # Print the responses
    for response in responses:
        print(response)
except Exception as e:
    logging.error("Exception occurred", exc_info=True)
    print("An error occurred.")
