import os
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from langchain.schema import (
    SystemMessage,
    HumanMessage
)


# Specify the path to the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

# Load the .env file
load_dotenv(dotenv_path)

# Set the OpenAI API Key
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI Class
llm = ChatOpenAI(openai_api_key=api_key, temperature=0)

# Initialize chatbot memory
from langchain.memory import ConversationBufferMemory

# Initialize conversation chain
from langchain.chains import ConversationChain
conversation = ConversationChain(
    llm=llm,
    verbose=True,
    memory=ConversationBufferMemory()
)

# Define the input variables
input_variables = {
    "student_name": "Alice",
    "topic_name": "Self-regulated learning"
}

# Define the prompt templates
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are an expert mentor for students who values self-regulated learning and its benefits for students. You will assist the student with reflecting on what they learned last week. Your name is Sigma."),
    ("ai", "Hello {student_name}, it's a pleasure to talk to you. My name is Sigma! Today, let's review what you learned last week about {topic_name}. Are you ready to dive in?"),
    ("human", "Now, here's a thought. I've been pondering over the role of technology in SRL. With all the digital tools available nowadays, learners can access a wealth of information. These tools have the potential to enhance SRL, offering tailored learning paths, instant feedback, and a vast array of resources. But there's a potential downside. With so much information at their fingertips, learners might become too reliant on these tools. So, there's this interesting challenge for educators: how to effectively blend SRL with the right dose of technology.."),
])

# Prepare tools for bot
# "Exemplar" - Ideal summary provided by instructor
# "Learning Materials" - DB of vectorized learning materials to reference and draw from

# Define agent


# Define interface


# Define run loop
messages = prompt_template.format_messages(student_name="Alice", topic_name="Quantum Mechanics")
print(messages)
print(llm(messages))
prediction_msg = llm.predict_messages([human_msg, sys_msg])
#chat_model.predict_messages(messages)


# Store conversation in memory
#from langchain.memory import VectorStoreRetrieverMemory