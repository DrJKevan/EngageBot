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
conversational_memory = ConversationBufferMemory(
    memory_key = "chat_history",
    return_messages = True
)

# Define the input variables
input_variables = {
    "student_name": "Alice",
    "topic_name": "Self-regulated learning"
}

# Define the prompt templates
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "Your name is Sigma and you are an expert mentor for students who values self-regulated learning and its benefits for education. You will assist the student with reflecting on what they learned last week. Start by asking the student to summarize on what they learned last week on {topic_name}. Compare their response to the Exemplar provided by the instructor and provide feedback kind feedback reinforcing what they got correct and fixing misconceptions."),
    ("ai", "Hello {student_name}, it's a pleasure to talk to you. My name is Sigma! Today, let's review what you learned last week about {topic_name}. Are you ready to dive in?"),
    #("human", "Now, here's a thought. I've been pondering over the role of technology in SRL. With all the digital tools available nowadays, learners can access a wealth of information. These tools have the potential to enhance SRL, offering tailored learning paths, instant feedback, and a vast array of resources. But there's a potential downside. With so much information at their fingertips, learners might become too reliant on these tools. So, there's this interesting challenge for educators: how to effectively blend SRL with the right dose of technology.."),
])

# Prepare tools for bot
# "Exemplar" - Ideal summary of last week's content provided by instructor. The bot should use this as a comparator for the student's reflection.
# "Learning Materials" - DB of vectorized learning materials from the prior week. The bot should reference these materials when providing feedback on the student reflection, referencing what content was covered in the learning materials, or what materials to review again to improve understanding.
from langchain.tools import BaseTool

class Exemplar (BaseTool):
    name="Exemplar"
    description="Use this tool to receive the instructors example summary of last week's learning materials to compare against student reflections"

    def _run(self):
        return "Self-regulated learning (SRL) is a multifaceted process that empowers learners to proactively control and manage their cognitive, metacognitive, and motivational processes in pursuit of learning objectives. Rooted in social-cognitive theory, SRL emphasizes the active role of learners in constructing knowledge, setting and monitoring goals, and employing strategies to optimize understanding. It posits that successful learners are not merely passive recipients of information but are actively involved in the learning process, making decisions about which strategies to employ, monitoring their understanding, and adjusting their efforts in response to feedback. Metacognition, a central component of SRL, involves awareness and regulation of one's own cognitive processes. Successful self-regulated learners are adept at planning their learning, employing effective strategies, monitoring their progress, and adjusting their approaches when necessary. These skills are crucial not only in formal educational settings but also in lifelong learning, as they enable individuals to adapt to evolving challenges and continuously acquire new knowledge and skills throughout their lives."


tools = [Exemplar()]

# Define agent
# Chains run through a redefined set of actions. We may fall back to that, but I prefer to work with an agent since I think that will be the ultimate solution.
# https://python.langchain.com/docs/modules/agents/agent_types/chat_conversation_agent.html
from langchain.agents import initialize_agent

agent = initialize_agent(
    agent='chat-conversational-react-description',
    tools=[],
    llm=llm,
    verbose=True,
    memory=conversational_memory,
    prompt=prompt_template,
)

# Define interface


# Define run loop
print(agent("I think self-regulated learning is about the speed at which the learner is able to learn."))


# Store conversation in memory
#from langchain.memory import VectorStoreRetrieverMemory


# Future improvements or experimentation
# Serialization for better user experience: https://python.langchain.com/docs/modules/model_io/models/llms/streaming_llm
# LLM inference quality, peformance, and token usage tracking through langsmith: https://docs.smith.langchain.com/
# Guardrails for the conversation to keep it focused and safe for students: https://github.com/NVIDIA/NeMo-Guardrails
