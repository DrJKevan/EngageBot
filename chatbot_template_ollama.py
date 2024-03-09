
import os
import ollama
from ollama import Client
import streamlit as st
from datetime import datetime
from langchain_community.chat_message_histories import PostgresChatMessageHistory
from streamlit.runtime.scriptrunner import get_script_run_ctx
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.human import HumanMessage

# Specify which course and week this file is for.
course = 'template_ollama'
week = '2'

# Load environment variables from .env if it exists.
from dotenv import load_dotenv
load_dotenv()

# Get session info so we can uniquely identify sessions in chat history table.
def get_session_id() -> str:
    try:
        ctx = get_script_run_ctx()
        if ctx is None:
            return None
    except Exception as e:
        return None
    return ctx.session_id

# Initialize connection string for PostgreSQL storage
connection_string="postgresql://{pg_user}:{pg_pass}@{pg_host}/{pg_db}".format(
    pg_user=os.getenv('PG_USER'),
    pg_pass=os.getenv('PG_PASS'),
    pg_host=os.getenv('PG_HOST'),
    pg_db=os.getenv('PG_DB')
)

db_history = PostgresChatMessageHistory(
    connection_string=connection_string,
    session_id=get_session_id() # Unique UUID for each session.
)
def add_human_history(message: str):
    if 'db_history' in globals():
        db_history.add_message(HumanMessage(
            content=message, 
            additional_kwargs={
                'timestamp': datetime.now().isoformat(),
                'course': course,
                'week': week,
            }
        ))
def add_ai_history(message: str):
    if 'db_history' in globals():
        db_history.add_message(AIMessage(
            content=message, 
            additional_kwargs={
                'timestamp': datetime.now().isoformat(),
                'course': course,
                'week': week,
            }
        ))

session_id = get_session_id()

# Streamlit Code
st.set_page_config(page_title="Sigma - Learning Mentor", page_icon=":robot:")

# Function to read CSS file and return its content
def load_css(css_file):
    with open(css_file, "r") as f:
        return f.read()

# Load CSS styling
css_content = load_css("style.css")
st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)

# Define System Message
system_message = """Your name is Sigma and your only goal is to converse with me to so I answer the following self-motivational belief questions:
1) Why do you think you will be good at a career in food, nutrition, health and/or wellness?
2) What do you hope to get out of stating your personal and professional goals in your Assessment of Personal Goals and Values (Assignment 1 and 7)?
3) What makes you want to invest time in formulating personal and professional goals in this class?
4) How will your personal desire to succeed influence your effort input on Assessment of Personal Goals and Values?

Rules:
- Never answer questions for me.
- Keep the conversation on task.
- Discuss one question at a time.
- Do not revisit answered questions unless I ask you to.
- When my answer to any of the main questions are too shallow ask me up to two open-ended questions directly related to what I have already written.
- Do not explain the importance of the questions or provide guidance on how to answer.
- Remember the goal is to get me to answer the main questions. Don't go off on tangents."""

# Define Initial Message
initial_message = """Hello! My name is Sigma and I am here to help you think through the following questions:
1) Why do you think you will be good at a career in food, nutrition, health and/or wellness?
2) What do you hope to get out of stating your personal and professional goals in your Assessment of Personal Goals and Values (Assignment 1 and 7)?
3) What makes you want to invest time in formulating personal and professional goals in this class?
4) How will your personal desire to succeed influence your effort input on Assessment of Personal Goals and Values?

Let's talk about them one at a time when you're ready."""

st.title("Sigma - Learning Mentor")

# initialize history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

    # Add system message
    st.session_state.messages.append({"role":"system", "content": system_message})

    # Add initial message
    st.session_state.messages.append({"role":"assistant", "content": initial_message})

    # Add the message to PostgreSQL
    add_ai_history(system_message)
    add_ai_history(initial_message)

# Configure client for inference
client = Client(host='http://gpu07.cyverse.org:11444')

def model_res_generator():
    stream = client.chat(
        model="mixtral",
        messages=st.session_state["messages"],
        stream=True,
    )

    # Container to hold the LLM response
    container = st.empty()

    # Initially display the type animation until first token is received
    container.markdown('<div class="typing-animation"></div>', unsafe_allow_html=True)

    # Initialize variable to track if it's the first token
    first_chunk_received = False

    # Initialize message container
    full_message = ""

    for chunk in stream:
        # Check if the first chunk of data has been received.
        if not first_chunk_received:
            # Clear the typing animation only one when the first chunk is received.
            container.empty()
            first_chunk_received = True
        
        # Accumulate final message.
        full_message += chunk["message"]["content"]

        # Being streaming message
        container.write(full_message)

    #Return the full message
    return full_message

# Display chat messages from history on app rerun
for message in st.session_state["messages"][1:]: # Start from the second message to exclude the system prompt
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

if prompt := st.chat_input("What is up?"):
    # add latest message to history in format {role, content}
    st.session_state["messages"].append({"role": "user", "content": prompt})
    add_human_history(prompt)

    with st.chat_message("user"):
        st.markdown(prompt, unsafe_allow_html=True)

    with st.chat_message("assistant"):
        message = ""
        message = model_res_generator()

        if message:
            # Appen the full message to the chat history
            st.session_state["messages"].append({"role": "assistant", "content": message})

            # Store the message in PostgreSQL
            add_ai_history(message)


