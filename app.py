import os
from langchain.llms import OpenAI

# Step 2: Set the OpenAI API Key
os.environ["OPENAI_API_KEY"] = "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"

# Step 3: Initialize the OpenAI Class
llm = OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))

# Step 4: Build a Language Model Application
text = "What would be a good company name for a company that makes colorful socks?"
response = llm(text)

print(response)
