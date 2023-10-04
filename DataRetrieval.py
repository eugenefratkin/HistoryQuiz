import pinecone
import numpy as np

# Initialize Pinecone
pinecone.init(api_key="9e656193-e394-43af-8147-5dcc62a22ef2", environment="asia-southeast1-gcp-free")

# Check your Pinecone version
print("Using Pinecone version: " + pinecone.__version__)

# Create an index
index_name = "history"
index_dimention = 4

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