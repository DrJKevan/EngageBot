import os
import streamlit as st
import psycopg2
import datetime

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.memory import PostgresChatMessageHistory
from langchain.agents import AgentExecutor
from langchain.callbacks import get_openai_callback
from langchain.tools import BaseTool, Tool
from langchain.vectorstores.pgvector import PGVector
from langchain.schema.messages import HumanMessage, AIMessage
from streamlit.runtime.scriptrunner import get_script_run_ctx

# Load environment variables from .env if it exists.
from dotenv import load_dotenv
load_dotenv()

#os.environ['LANGCHAIN_PROJECT']="MED810_p2"  # if not specified, defaults to "default"

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

#db_history = PostgresChatMessageHistory(
#   connection_string=connection_string,
#   session_id=get_session_id() # Unique UUID for each session.
# )


# Define available OpenAI models.
models = [
    "gpt-3.5-turbo", 
    "gpt-3.5-turbo-0301", 
    "gpt-3.5-turbo-0613", 
    "gpt-3.5-turbo-16k", 
    "gpt-3.5-turbo-16k-0613", 
    "gpt-4", 
    "gpt-4-0314", 
    "gpt-4-0613",
]

session_id = get_session_id()

# Initialize the OpenAI Class
llm = ChatOpenAI(temperature=0, model=models[4], tags=[session_id])

# Optionally, specify your own session_state key for storing messages
msgs = StreamlitChatMessageHistory(key="special_app_key")

# Initialize chatbot memory
conversational_memory = ConversationBufferMemory(
    memory_key = "chat_history",
    chat_memory = msgs,
    input_key="input",
    return_messages = True,
    ai_prefix="AI Assistant",
)




# Create template for system message to provide direction for the agent
role_description = """Your name is Sigma and your goal is to converse with me to get my answers to the following task analysis questions:
1) What percent correct would you like to achieve on the final clinical reasoning case and why?
2) How would you like to prepare your clinical reasoning skills for the final clinical case?
3) When will you start doing each of your preparation tasks?
"""

context = """Context:
I am a medical student in a clinical reasoning course at the University of Arizona.
"""

rules = """Rules:
- Never answer questions for me
- Keep the conversation on task
- For each task analysis question, always follow-up my first response with one open-ended question
"""

system_message = role_description + context + rules


# Add a callback to count the number of tokens used for each response.
# This callback is not necessary for the agent to function, but it is useful for tracking token usage.
def run_query_and_count_tokens(chain, query):
    with get_openai_callback() as cb:
        print('query \n')
        print(query)
        print('query end \n')
        result = chain.run(query)
        print(cb)
    return result

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
    @keyframes typing {{
        0% {{ content: '.'; }}
        25% {{ content: '..'; }}
        50% {{ content: '...'; }}
        75% {{ content: '..'; }}
        100% {{ content: '.'; }}
    }}

    .typing-animation::before {{
        content: '...';
        animation: typing 1s steps(5, end) infinite;
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
    welcome_message = """Hello! My name is Sigma and I am here to help you think through the following questions:
1) What percent correct would you like to achieve on the final clinical reasoning case and why?
2) How would you like to prepare your clinical reasoning skills for the final clinical case?
3) When will you start doing each of your preparation tasks?

Let's talk about them one at a time when you're ready.
"""
    st.session_state.messages = [{"role": "assistant", "content": welcome_message}]
    # db_history.add_message(AIMessage(
    #     content=welcome_message, 
    #     additional_kwargs={'timestamp': datetime.datetime.now().isoformat()}
    # ))
  
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role":"user", "content":prompt})
    # db_history.add_message(HumanMessage(
    #     content=prompt,
    #     additional_kwargs={'timestamp': datetime.datetime.now().isoformat()}
    # )
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant thinking animation in chat message container
    with st.chat_message("assistant"):
        # This placeholder will initially show the "thinking" animation
        message_placeholder = st.empty()
        message_placeholder.markdown('<div class="typing-animation"></div>', unsafe_allow_html=True) # Simple 3 dots "thinking" animation
        
        # Get the response from the chatbot
        #response = executor.run(prompt)
        #print(conversational_memory.buffer_as_messages) - Uncomment to see message log
        response = run_query_and_count_tokens(executor, prompt)

        # Replace the "thinking" animation with the chatbot's response
        message_placeholder.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        # db_history.add_message(AIMessage(
        #     content=response, 
        #     additional_kwargs={'timestamp': datetime.datetime.now().isoformat()}
        # ))
