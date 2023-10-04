import pinecone
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

# Delete the index
#pinecone.deinit()
#pinecone.delete_index(index_name)