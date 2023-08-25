import os
import pinecone
from dotenv  import load_dotenv
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.chains import RetrievalQA
from langchain import OpenAI


## GENERAL CONFIGURATION
# Specify the path to the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

# Load the .env file
load_dotenv(dotenv_path)

# Set the OpenAI API Key
api_key = os.getenv("OPENAI_API_KEY")

## PREPARE DATASTORES
# Initialize Pinecone
# Dimensions = 1536
# Metric - Cosine
pinecone.init(
    api_key  = "7efbb05b-6bb7-4e89-bd90-116a7c06f679", # find at app.pinecone.io
    environment = "us-west4-gcp-free" # next to api key in console 
)

# Load course data
loader = PyPDFLoader("srlpaper.pdf")
pages = loader.load_and_split()

# TODO Review best practices on splitting parameters, explore text splitting options (specifically MarkdownHeaderTextSplitter)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap = 200,
    length_function = len,
)

docs = text_splitter.split_documents(pages)

# Create embeddings
embeddings = OpenAIEmbeddings()

# Create a vectorstore 
index_name = "engagebot2"

# Create a new index and search
# docsearch = Pinecone.from_documents(docs, embeddings, index_name=index_name)

# Search from a new index
docsearch = Pinecone.from_existing_index(index_name,embeddings)

# Vectorstore using transient memory via Chroma
# from langchain.vectorstores import Chroma
# docsearch = Chroma.from_documents(docs, embeddings)

# Vector DB query example
query = "What is self-regulated learning?"
docs = docsearch.similarity_search(query)
print(len(docs))
print(docs[0])
print(docs[0].page_content)

# Need to compartmentalize the creation of the index.. or, create it here then comment out that line and use the existing index.
# Multiple calls will create duplicate data in the index.

# define LLM
llm = OpenAI(temperature = 0.2)

qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=docsearch.as_retriever(search_kwargs={"k":2}))

query = "What is self-regulated learning?"
print(qa.run(query))
