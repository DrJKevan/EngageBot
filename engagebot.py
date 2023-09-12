import os
import streamlit as st
import pinecone
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.chains import RetrievalQA, LLMChain, ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate
from langchain import PromptTemplate
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.agents import initialize_agent, load_tools, AgentExecutor
from langchain.schema import (
    SystemMessage,
    HumanMessage
)
from langchain.callbacks import get_openai_callback
from langchain.tools import BaseTool, Tool

# Hack to get multi-input tools working again.
# See: https://github.com/langchain-ai/langchain/issues/3700#issuecomment-1568735481
from langchain.agents.conversational_chat.base import ConversationalChatAgent
ConversationalChatAgent._validate_tools = lambda *_, **__: ...

# Set the OpenAI API Key
# cli command = streamlit run engagebot.py
os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']

# Use next line when pull from local .env file
api_key = os.getenv("OPENAI_API_KEY")

# Define available OpenAI models
models = ["gpt-3.5-turbo", "gpt-3.5-turbo-0301", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-16k-0613", "gpt-4", "gpt-4-0314", "gpt-4-0613"]

# Initialize the OpenAI Class
llm = ChatOpenAI(openai_api_key=api_key, temperature=0, model=models[2])

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

# Prepare tools for bot
# "Exemplar" - Ideal summary of last week's content provided by instructor. The bot should use this as a comparator for the student's reflection.

class Exemplar (BaseTool):
    name="Exemplar"
    description="Use this tool to receive the instructors example summary of last week's learning materials to compare against student reflections"

    def _run(args, kwargs):
        return "Self-regulated learning (SRL) is a multifaceted process that empowers learners to proactively control and manage their cognitive, metacognitive, and motivational processes in pursuit of learning objectives. Rooted in social-cognitive theory, SRL emphasizes the active role of learners in constructing knowledge, setting and monitoring goals, and employing strategies to optimize understanding. It posits that successful learners are not merely passive recipients of information but are actively involved in the learning process, making decisions about which strategies to employ, monitoring their understanding, and adjusting their efforts in response to feedback. Metacognition, a central component of SRL, involves awareness and regulation of one's own cognitive processes. Successful self-regulated learners are adept at planning their learning, employing effective strategies, monitoring their progress, and adjusting their approaches when necessary. These skills are crucial not only in formal educational settings but also in lifelong learning, as they enable individuals to adapt to evolving challenges and continuously acquire new knowledge and skills throughout their lives."

class Assignment (BaseTool):
    name="Assignment"
    description="Use this tool to obtain the student's assignment"

    def _run(args, kwargs):
        return """Your assignments is to carefully read the two articles provided to you: "Models of Self-regulated Learning: A review" and "Self-Regulated Learning: Beliefs, Techniques, and Illusions.\n"
        Based on your understanding, prepare the following answers in 500 words or less:\n
        a) Definition of SRL: In your own words, provide a definition of self-regulated learning.\n
        b) Model Description: Describe one of the SRL models that you found most interesting. Explain why it resonated with you.\n
        c) Learning Activity Proposal: Suggest an example learning activity or experience that could be integrated into an academic course. This activity should scaffold self-regulated learning for students.\n\n
        Go ahead and submit when you're ready!
        """
    
# "Learning Materials" - DB of vectorized learning materials from the prior week. The bot should reference these materials when providing feedback on the student reflection, referencing what content was covered in the learning materials, or what materials to review again to improve understanding.
embeddings = OpenAIEmbeddings()
# Connect to our Pinecone vector database of PDF readings.
pinecone.init(
    api_key  = st.secrets['PINECONE_API_KEY'], # find at app.pinecone.io
    environment = st.secrets['PINECONE_ENVIRONMENT']
)
index_name = st.secrets['PINECONE_INDEX']
if index_name not in pinecone.list_indexes():
    # Create the Pinecone index from the source PDFs if it doesn't exist.
    pinecone.create_index(name=index_name, dimension=1536, metric="cosine")
index = pinecone.Index(index_name)
# print(index.describe_index_stats())
if index.describe_index_stats().total_vector_count < 1:
    # Load course data with PDFPlumber: $ python3 -m pip install pdfplumber
    from langchain.document_loaders import PDFPlumberLoader
    loader = PDFPlumberLoader("srlpaper.pdf")
    pages = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 200,
        length_function = len,
    )
    docs = text_splitter.split_documents(pages)
    vectorstore = Pinecone.from_documents(docs, embeddings, index_name=st.secrets['PINECONE_INDEX'])
else:
    vectorstore = Pinecone(index, embeddings, 'text')
# See: https://www.pinecone.io/learn/series/langchain/langchain-retrieval-augmentation/
search_readings_chain = RetrievalQA.from_chain_type(llm, chain_type="stuff", retriever=vectorstore.as_retriever())
search_readings_tool = Tool(
   name="Class Assignment Readings",
   #func=search_readings_chain.run
   func = vectorstore.similarity_search,
   description="useful for when you need to reference class readings from previous weeks that students have already read"
)

# Define tools
#tools = [Exemplar(), Assignment()]
tools = [Exemplar(), Assignment(), search_readings_tool]

# Define the input variables
input_variables = {
    "student_name": "Alice",
    "topic_name": "Self-regulated learning"
}


# Create template for system message to provide direction for the agent
role_description = """Your name is Sigma and you are a mentor for higher education students. Your goal to provide feedback to students on their assignments. Using the tools available to you, provide feedback to the user's assignment submission considering the assignment instructions and the exemplar available to you.\n\n"""

analysis_instructions = """Once the student has subitted part or all of the assignment take the following steps:\n
1) Compare the submission against the assignment and note what was missing.\n
2) Compare the quality and depth of the submission against the exemplar.\n
3) Produce feedback for overall quality, what was correct, and where it could be improved.\n
4) In an encouraging and conversation tone share the results of the previous three steps in an integrated summary.\n\n"""

rules = """Rules:\n
- If the student did not submit all parts of the assignment, encourage them to do so\n
- Keep the conversation on task to complete the assignment\n
"""

history = """
\nCurrent conversation:\n
{chat_history}\n
Human: {input}\n
AI Assistant: """

system_message = role_description + rules + history

# Trying different agent constructor
newAgentPrompt = ConversationalChatAgent.create_prompt(tools=tools, system_message=system_message, input_variables=["chat_history", "input", "agent_scratchpad"])
llm_chain = LLMChain(llm=llm, prompt=newAgentPrompt)
agent = ConversationalChatAgent(llm_chain=llm_chain, tools=tools, verbose=True)
executor = AgentExecutor.from_agent_and_tools(
   agent = agent,
   tools = tools,
   memory = conversational_memory,
   early_stopping_method = "force",
   handle_parsing_errors = True,
   max_iterations = 4,
   #return_intermediate_steps = True,
   verbose = True,
)

# Add a callback to count the number of tokens used for each response.
# This callback is not necessary for the agent to function, but it is useful for tracking token usage.
def run_query_and_count_tokens(chain, query):
    with get_openai_callback() as cb:
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
  st.session_state.messages = [{"role": "assistant", "content": """Hello! My name is Sigma and I am here to help you reflect on what you learned last week."""}]
  
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



# TODO 
# Serialization for better user experience: https://python.langchain.com/docs/modules/model_io/models/llms/streaming_llm
# LLM inference quality, peformance, and token usage tracking through langsmith: https://docs.smith.langchain.com/
# Guardrails for the conversation to keep it focused and safe for students. Some optionsinclude NVidia's - https://github.com/NVIDIA/NeMo-Guardrails and Guardrails.ai - https://docs.getguardrails.ai/
# Fix 'Could not parse LLM Output' error that is curently being handled automatically on via parameter in agent initialization. This appears to slightly impact performance, but not quality of inference. Some potential conversation to help find the solution:
# https://github.com/langchain-ai/langchain/pull/1707
# https://github.com/langchain-ai/langchain/issues/1358
# Nice video on the difference between map-reduce, stuff, refine, and map-rank document searches with an example:
# https://www.youtube.com/watch?v=OTL4CvDFlro

# Notes for improving inference
# The more text in the context, the more likely the LLM will forget the instructions