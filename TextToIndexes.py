from llama_index import ServiceContext, VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores import PineconeVectorStore
from llama_index.llms import OpenAI
import pinecone
import openai
import os

os.environ["OPENAI_API_KEY"] = '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'

# Define the chunk and overlap sizes
CHUNK_SIZE = 1000  # Adjust this value to your needs
OVERLAP = 100  # Adjust this value to your needs
DIMENSION_VALUE = 1536 # Number of dimentions used for embedding

# Initialize Pinecone
pinecone.init(api_key="9e656193-e394-43af-8147-5dcc62a22ef2", environment="asia-southeast1-gcp-free")

directory = "/Users/efratkin/Code Projects/HistoryQuiz/output"

# Create or connect to a Pinecone index
# This function creates a Pinecone index with the given name and dimension, using a single shard.
def create_index(index_name, index_dimension):
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(name=index_name, dimension=index_dimension)
    else:
        print(f"Index {index_name} already exists.")

def get_index(index_name, index_dimention):
    create_index(index_name, index_dimention)
    return pinecone.Index(index_name=index_name)

def chunk_and_vectorize(directory):
    documents = SimpleDirectoryReader(directory).load_data()

    pinecone_index = get_index("history-chunks", DIMENSION_VALUE)
    # Use LLamaIndex to break up the text into chunks
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    service_context = ServiceContext.from_defaults(chunk_size=CHUNK_SIZE, chunk_overlap=OVERLAP, llm=OpenAI())
    index = VectorStoreIndex.from_documents(
        documents,
        service_context=service_context,
        storage_context=storage_context,
        show_progress=True
    )
    index.set_index_id("vector_index")
    index.storage_context.persist("/Users/efratkin/Code Projects/HistoryQuiz/index")

# Call the function with your text
chunk_and_vectorize(directory)

# Don't forget to cleanup
#pinecone.deinit()
