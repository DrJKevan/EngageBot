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

# Define available OpenAI models
models = ["gpt-3.5-turbo", "gpt-3.5-turbo-0301", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-16k-0613"]

# Initialize the OpenAI Class
llm = ChatOpenAI(openai_api_key=api_key, temperature=0.2, model=models[4])

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

# Prepare tools for bot
# "Exemplar" - Ideal summary of last week's content provided by instructor. The bot should use this as a comparator for the student's reflection.
from langchain.tools import BaseTool

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

# Define tools
tools = [Exemplar(), Assignment()]

FORMAT_INSTRUCTIONS = """To use a tool, please use the following format:

\```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
\```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the following format(the prefix of "Thought: " and "{ai_prefix}: " are must be included):

\```
Thought: Do I need to use a tool? No
{ai_prefix}: [your response here]
\```"""

# Initialize Agent
engagebot = initialize_agent(
    agent='chat-conversational-react-description',
    tools=tools,
    llm=llm,
    verbose=True,
    memory=conversational_memory,
    handle_parsing_errors = True,
    agent_kwargs={"format_instructions": FORMAT_INSTRUCTIONS},
    max_execution_time=10, #limits length of agent running, in seconds.
)

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

#template = role_description + analysis_instructions  # Getting an error when it attempts to do 'analysis'. I think it's creating its own header in the llm response which is causing a parsing error.
template = role_description + rules

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
  # Display assistant response in chat message container
  with st.chat_message("assistant"):
    message_placeholder = st.empty()
    response = engagebot.run(prompt)
    print(response)
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