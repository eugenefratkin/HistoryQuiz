import pinecone
import pymongo
import numpy as np
from sentence_transformers import SentenceTransformer, util
import torch

# Initialize Pinecone
pinecone.init(api_key="9e656193-e394-43af-8147-5dcc62a22ef2", environment="asia-southeast1-gcp-free")

# Check your Pinecone version
print("Using Pinecone version: " + pinecone.__version__)

# Create an index
index_name = "history"
index_dimention = 4

def connect_to_documentdb():
    # Connection details
    username = "homework"
    password = "fgu3mgh3dtg_her!EPF"
    cluster_endpoint = "docdb-2023-10-04-23-49-54.cd2f6lgiqcr3.us-east-1.docdb.amazonaws.com"
    port = 27017  # default MongoDB and DocumentDB port
    
    # Connection URI
    connection_uri = f"mongodb://{username}:{password}@{cluster_endpoint}:{port}/?ssl=true&replicaSet=rs0&readpreference=primaryPreferred&retrywrites=false"
    
    # Connect to DocumentDB
    client = pymongo.MongoClient(connection_uri, tlsCAFile='global-bundle.pem')
    
    # Use a database (or create it if it doesn't exist)
    db = client['history']
    
    # Use a collection (or create it if it doesn't exist)
    collection = db['history']
    
    # Insert a document into the collection
    collection.insert_one({"key": "value"})
    
    # Retrieve and print all documents from the collection
    for doc in collection.find():
        print(doc)

def text_to_embedding(text):
    """
    Converts a text to a vector embedding using Sentence Transformers.
    
    Parameters:
        text (str): The text to convert.
        
    Returns:
        torch.Tensor: The vector embedding of the text.
    """
    # Load the model
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    
    # Generate the embedding
    embedding = model.encode(text, convert_to_tensor=True)
    
    return embedding

def store_embedding_in_pinecone(embedding, vector_id, index):
    # Convert the embedding to a list
    if isinstance(embedding, torch.Tensor):
        embedding = embedding.cpu().numpy()
    embedding_list = embedding.tolist()
    
    # Upsert the vector to Pinecone
    index.upsert(vectors={vector_id: embedding_list})


# This function creates a Pinecone index with the given name and dimension, using a single shard.
def create_index(index_name, index_dimension):
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(index_name=index_name, dimension=index_dimension, shard_count=1)
    else:
        print(f"Index {index_name} already exists.")

# This function calls 'create_index' with 'index_name' and 'index_dimension' as parameters. 
# It then returns a Pinecone index object for the specified 'index_name'.
def get_index(index_name, index_dimention):
    create_index(index_name, index_dimention)
    return pinecone.Index(index_name=index_name)

# Connect to the index
index = get_index(index_name, index_dimention)

# Insert some vectors
vectors = [("id1", [1, 0, 1, 0]), ("id2", [0, 2, 1, 0])]
index.upsert(vectors=vectors)

# Query the index
query_vector = [[1, 0, 1, 1]]
results = index.query(queries=query_vector, top_k=2)

# Display results
print(results)

connect_to_documentdb()

# Delete the index
#pinecone.deinit()
#pinecone.delete_index(index_name)