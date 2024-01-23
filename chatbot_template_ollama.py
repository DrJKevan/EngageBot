import os
import streamlit as st
from langchain.chains.llm import LLMChain
from langchain.chains import ConversationChain
from langchain.memory.buffer import ConversationBufferMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain.memory import PostgresChatMessageHistory
from streamlit.runtime.scriptrunner import get_script_run_ctx
from langchain.agents.conversational_chat.base import ConversationalChatAgent
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain_core.messages import SystemMessage

from langchain.callbacks.base import BaseCallbackHandler
class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)

#from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama

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

#db_history = PostgresChatMessageHistory(
#   connection_string=connection_string,
#   session_id=get_session_id() # Unique UUID for each session.
# )

session_id = get_session_id()

# Create template for system message to provide direction for the agent
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
- Ask me follow-up questions when my answers are too shallow.
- If we have been talking about 1 question for awhile, ask me if I want to move on to the next question.
"""

# Prompt
prompt_template = ChatPromptTemplate(
    messages=[
        SystemMessage(content=system_message),
        # The `variable_name` here is what must align with memory
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{input}"),
    ]
)

# Optionally, specify your own session_state key for storing messages
msgs = StreamlitChatMessageHistory(key="special_app_key")

# Initialize chatbot memory
conversational_memory = ConversationBufferMemory(
    memory_key = "chat_history",
    chat_memory = msgs,
    input_key="input",
    return_messages = True,
    ai_prefix="AI",
    human_prefix="Human",
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
1) Why do you think you will be good at a career in food, nutrition, health and/or wellness?
2) What do you hope to get out of stating your personal and professional goals in your Assessment of Personal Goals and Values (Assignment 1 and 7)?
3) What makes you want to invest time in formulating personal and professional goals in this class?
4) How will your personal desire to succeed influence your effort input on Assessment of Personal Goals and Values?

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
        
        stream_handler = StreamHandler(message_placeholder)
        ollama = ChatOllama(base_url='http://gpu06.cyverse.org:11444', model="mixtral", streaming=True, callbacks=[stream_handler], system=system_message,)

        conversation = ConversationChain(llm=ollama, prompt=prompt_template, verbose=True, memory=conversational_memory, input_key="input",)

        # Get the response from the chatbot
        response = conversation.invoke(prompt)
        print(response)

        # Replace the "thinking" animation with the chatbot's response
        message_placeholder.markdown(response['response'])
        st.session_state.messages.append({"role": "assistant", "content": response['response']})

        # db_history.add_message(AIMessage(
        #     content=response, 
        #     additional_kwargs={'timestamp': datetime.datetime.now().isoformat()}
        # ))
