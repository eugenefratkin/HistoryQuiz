from llama_index import ServiceContext, VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.schema import TextNode, NodeRelationship, RelatedNodeInfo
from llama_index.node_parser import SimpleNodeParser
from llama_index.vector_stores import PineconeVectorStore
from llama_index.llms import OpenAI
import json
import pinecone

import keyring
import os

# Get the API key from the system's keyring
api_key = keyring.get_password("openai", "api_key")

# Check if the API key was retrieved successfully
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key
else:
    print("Failed to retrieve the API key.")

# Define the chunk and overlap sizes
CHUNK_SIZE = 500  # Adjust this value to your needs
OVERLAP = 100  # Adjust this value to your needs
DIMENSION_VALUE = 1536 # Number of dimentions used for embedding

# Initialize Pinecone
pinecone.init(api_key="9e656193-e394-43af-8147-5dcc62a22ef2", environment="asia-southeast1-gcp-free")

directory = "./output"

def parse_docs_to_nodes(documents):
    parser = SimpleNodeParser.from_defaults(chunk_size=CHUNK_SIZE, chunk_overlap=OVERLAP)
    nodes = parser.get_nodes_from_documents(documents)
    # Assuming nodes is your collection of nodes
    previous_node = nodes[0]
    for node in nodes[1:]:
        node.relationships[NodeRelationship.PARENT] = RelatedNodeInfo(node_id=previous_node.node_id, metadata={"key": "val"})
    return nodes

def serialize_text_node(node):
    return {
        "text": node.text,
        "id_": node.id_
    }

def store_nodes_to_json(nodes, directory):
    # Convert to JSON string\
    serialized_nodes = [serialize_text_node(node) for node in nodes]
    json_string = json.dumps(serialized_nodes, indent=4)  # indent=4 for pretty-printing

# Write to file
    with open(directory + "/nodes.json", "w") as file:
     file.write(json_string)

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
    nodes = parse_docs_to_nodes(documents)
    store_nodes_to_json(nodes, directory)

    pinecone_index = get_index("history-chunks", DIMENSION_VALUE)
    # Use LLamaIndex to break up the text into chunks
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    service_context = ServiceContext.from_defaults(chunk_size=CHUNK_SIZE, chunk_overlap=OVERLAP, llm=OpenAI())
    index = VectorStoreIndex(
        nodes, 
        service_context=service_context,
        storage_context=storage_context,
        show_progress=True
        )

    #index = VectorStoreIndex.from_documents(
    #    documents,
    #    service_context=service_context,
    #    storage_context=storage_context,
    #    show_progress=True
    #)
    index.set_index_id("vector_index")
    index.storage_context.persist("./index")

# Call the function with your text
chunk_and_vectorize(directory)

# Don't forget to cleanup
#pinecone.deinit()
