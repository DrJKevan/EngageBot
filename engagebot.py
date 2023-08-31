import os
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain import PromptTemplate
from dotenv import load_dotenv
from langchain.agents import initialize_agent
from langchain.schema import (
    SystemMessage,
    HumanMessage
)

# Hack to get multi-input tools working again.
# See: https://github.com/langchain-ai/langchain/issues/3700#issuecomment-1568735481
from langchain.agents.conversational_chat.base import ConversationalChatAgent
ConversationalChatAgent._validate_tools = lambda *_, **__: ...

# Specify the path to the .env file
#dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

# Load the .env file
#load_dotenv(dotenv_path)

# Set the OpenAI API Key
# Use this line when working with Streamlit
os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']

# Use next line when pull from local .env file
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI Class
llm = ChatOpenAI(openai_api_key=api_key, temperature=0.2)

# Initialize chatbot memory
from langchain.memory import ConversationBufferMemory
conversational_memory = ConversationBufferMemory(
    memory_key = "chat_history",
    return_messages = True,
)

# Define the input variables
input_variables = {
    "student_name": "Alice",
    "topic_name": "Self-regulated learning"
}

# Define the prompt templates
# This is not currently being used as I was having issues importing it.
# prompt_template = ChatPromptTemplate.from_messages([
#    ("system", "Your name is Sigma and you are an expert mentor for students who values self-regulated learning and its benefits for education. Your goal is to assist the student with reflecting on what they learned last week. Start by asking the student to summarize on what they learned last week on {topic_name} then provide helpful feedback on what they got right, what they might misunderstand, and what they missed. "),
#    ("ai", "Hello {student_name}, it's a pleasure to talk to you. My name is Sigma! Today, let's review what you learned last week about {topic_name}. Are you ready to dive in?"),
#])

# Prepare tools for bot
# "Exemplar" - Ideal summary of last week's content provided by instructor. The bot should use this as a comparator for the student's reflection.
from langchain.tools import BaseTool

class Exemplar (BaseTool):
    name="Exemplar"
    description="Use this tool to receive the instructors example summary of last week's learning materials to compare against student reflections"

    def _run(args, kwargs):
        return "Self-regulated learning (SRL) is a multifaceted process that empowers learners to proactively control and manage their cognitive, metacognitive, and motivational processes in pursuit of learning objectives. Rooted in social-cognitive theory, SRL emphasizes the active role of learners in constructing knowledge, setting and monitoring goals, and employing strategies to optimize understanding. It posits that successful learners are not merely passive recipients of information but are actively involved in the learning process, making decisions about which strategies to employ, monitoring their understanding, and adjusting their efforts in response to feedback. Metacognition, a central component of SRL, involves awareness and regulation of one's own cognitive processes. Successful self-regulated learners are adept at planning their learning, employing effective strategies, monitoring their progress, and adjusting their approaches when necessary. These skills are crucial not only in formal educational settings but also in lifelong learning, as they enable individuals to adapt to evolving challenges and continuously acquire new knowledge and skills throughout their lives."

# "Learning Materials" - DB of vectorized learning materials from the prior week. The bot should reference these materials when providing feedback on the student reflection, referencing what content was covered in the learning materials, or what materials to review again to improve understanding.

# Define tools
tools = [Exemplar()]

# Initialize Agent
engagebot = initialize_agent(
    agent='chat-conversational-react-description',
    tools=tools,
    llm=llm,
    verbose=True,
    memory=conversational_memory,
    handle_parsing_errors = True,
)

# Create template for system message to provide direction for the agent
template = """Your name is Sigma and you are an expert mentor for students who values self-regulated learning and its benefits for education. Your goal is to assist the student with reflecting on what they learned last week by taking the following steps:
    1) Ask the student to summarize what they learned last week.
    2) Identify any content that is missing, misunderstood or inaccurate.
    3) Respond to the student with a positive mentoring tone and outline what they summarized correctly what they could approve on.

    Explain your thinking as you go.
    """

# Update the agent's system instructions
engagebot.agent.llm_chain.prompt.messages[0] = SystemMessagePromptTemplate(
                prompt=PromptTemplate(
                    input_variables=[],
                    output_parser=None,
                    partial_variables={},
                    template= template,
                    template_format='f-string',
                    validate_template=True
                ),
                additional_kwargs={}
            )

# Streamlit Code
st.set_page_config(page_title="Sigma - Learning Mentor", page_icon=":robot:")

# Use consistent styling and layout
background_color = "#f4f4f6"
font_color = "#333"

st.markdown(
    f"""
    <style>
        body {{
            background-color: {background_color};
            color: {font_color};
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Sigma - Learning Mentor")

# Chat Window Styling
chat_window_style = """
    border-radius: 10px;
    border: 1px solid #ddd;
    background-color: #fff;
    padding: 10px;
    height: 400px;
    overflow-y: auto;
    font-size: 16px;
    font-family: Arial, sans-serif;
"""

response_style = """
    border-radius: 5px;
    background-color: #e1f3fd;
    padding: 10px;
    margin: 10px 0;
    display: inline-block;
"""

# Set a default model
if "openai_model" not in st.session_state:
  st.session_state["openai_model"] = "gpt-3.5-turbo"
  
# Initialize chat history
if "messages" not in st.session_state:
  st.session_state.messages = [{"role": "assistant", "content": "Hello! My name is Sigma and I am here to help you reflect on what you learned last week. Do the best you can to summarize all of the learning materials you completed last week, and I will provide feedback."}]
  
# Display chat messages from history on app rerun
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
  # Add user message to chat history
  st.session_state.messages.append({"role":"user", "content":prompt})
  # Display user message in chat message container
  with st.chat_message("user"):
    st.markdown(prompt)
  # Display assistant response in chat message container
  with st.chat_message("assistant"):
    message_placeholder = st.empty()
    response = engagebot.run(prompt)
    message_placeholder.markdown(response)
  st.session_state.messages.append({"role": "assistant", "content": response})

# TODO 
# Serialization for better user experience: https://python.langchain.com/docs/modules/model_io/models/llms/streaming_llm
# LLM inference quality, peformance, and token usage tracking through langsmith: https://docs.smith.langchain.com/
# Guardrails for the conversation to keep it focused and safe for students. Some optionsinclude NVidia's - https://github.com/NVIDIA/NeMo-Guardrails and Guardrails.ai - https://docs.getguardrails.ai/
# Maintain chat history throughout the session
# Fix 'Could not parse LLM Output' error that is curently being handled automatically on via parameter in agent initialization. This appears to slightly impact performance, but not quality of inference. Some potential conversation to help find the solution:
# https://github.com/langchain-ai/langchain/pull/1707
# https://github.com/langchain-ai/langchain/issues/1358

# Notes for improving inference
# The more text in the context, the more likely the LLM will forget the instructions