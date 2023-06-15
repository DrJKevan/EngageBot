from langchain import HuggingFacePipeline, PromptTemplate, LLMChain

# Load the GPT-4 model
llm = HuggingFacePipeline.from_model_id(
    model_id="gpt-4-model-id",  # Replace with the actual GPT-4 model ID
    task="text-generation",
    model_kwargs={"temperature": 0.8, "max_length": 200}
)

# Define a basic prompt template
template = "Question: {question} Answer: Let's think step by step."
prompt = PromptTemplate(template=template, input_variables=["question"])

# Create an LLM chain with the prompt and the model
llm_chain = LLMChain(prompt=prompt, llm=llm)

# Test the chatbot with a sample question
question = "What did you learn last week?"
print(llm_chain.run(question))
