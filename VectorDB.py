import pinecone
import numpy as np

# Initialize Pinecone
pinecone.init(api_key="9e656193-e394-43af-8147-5dcc62a22ef2", environment="asia-southeast1-gcp-free")

# Check your Pinecone version
print("Using Pinecone version: " + pinecone.__version__)

# Create an index
pinecone.create_index(name="history", dimension=2, metric="cosine", shards=1)

# Connect to the index
index = pinecone.Index(index_name="history")

# Insert some vectors
vectors = {"id1": np.array([1, 1]), "id2": np.array([2, 2])}
index.upsert(vectors=vectors)

# Query the index
query_vector = np.array([1, 1])
results = index.query(queries=query_vector, top_k=2)

# Display results
print(results)

# Delete the index
#pinecone.deinit()
#pinecone.delete_index("my_index")