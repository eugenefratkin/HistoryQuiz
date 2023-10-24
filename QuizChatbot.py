from llama_index import ServiceContext, VectorStoreIndex
from llama_index.vector_stores import PineconeVectorStore
from llama_index.llms import OpenAI
import pinecone
import random
import os
import json
import openai
import keyring
from llama_index import (
    VectorStoreIndex,
)
from llama_index.retrievers import VectorIndexRetriever
from llama_index.query_engine import RetrieverQueryEngine

index_name = "history-chunks"
total_vector_count = 0
directory = "/Users/efratkin/Code Projects/HistoryQuiz/output"

import keyring
import os

# Get the API key from the system's keyring
api_key = keyring.get_password("openai", "api_key")

# Check if the API key was retrieved successfully
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key
else:
    print("Failed to retrieve the API key.")

pinecone.init(api_key="9e656193-e394-43af-8147-5dcc62a22ef2", environment="asia-southeast1-gcp-free")
openai.api_key = os.environ["OPENAI_API_KEY"]

def connect_to_DB():
    # Use LLamaIndex to break up the text into chunks
    pinecone_index = pinecone.Index(index_name=index_name)
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    service_context = ServiceContext.from_defaults(llm=OpenAI())
    return VectorStoreIndex.from_vector_store(vector_store=vector_store, service_context=service_context)

def get_random_chunk_text():
    # Load and parse the JSON file
    with open(directory+"/nodes.json", 'r') as file:
        nodes = json.load(file)
    
    # Randomly select one of the serialized nodes
    random_node = random.choice(nodes)
    
    # Extract and return the text of the randomly selected node
    return random_node['text']

def check_answer(user_answer, correct_answer):
    # Implement your answer checking logic here
    return user_answer.lower() == correct_answer.lower()


def Test():
    text = get_random_chunk_text()
    question_answer = None

    try:
        # Make API call
        # Note: You might need to adjust the model and other parameters as per your use case
        response = openai.Completion.create(
            engine="text-davinci-003",  # Use "davinci" or other available engines
            prompt=f"{text}\n\nGiven the text come-up with a question and answer pair. Put it in JSON format with question and answer fields:",
            max_tokens=3500  # Adjust as needed
        )
                # Extract and store response
        question_answer = response.choices[0].text.strip()

    except Exception as e:
        print(f"Error processing text: {text}. Error: {str(e)}")
        question_answer.append(None)

    # Parse the question and answer from the API response
    if question_answer:
        try:
            qa_json = json.loads(question_answer)
            question = qa_json.get('question', '')
            correct_answer = qa_json.get('answer', '')
            
            # Print the question part
            print(f"Question: {question}")
            
            # Wait for the human to provide an answer
            user_answer = input("Your answer: ")
            
            # Check the provided answer
            is_correct = check_answer(user_answer, correct_answer)
            
            if is_correct:
                print("Correct!")
            else:
                print(f"Incorrect. The correct answer is: {correct_answer}")
                
        except json.JSONDecodeError:
            print("Error parsing the question and answer JSON.")

    else:
        print("No question and answer generated.")


def Answer(index, question):
    query_engine = index.as_query_engine(
        similarity_top_k=17, 
        response_mode='refine',
        verbose=True)
    response = query_engine.query(question)
    print(response)

def get_chunk_count(index):
    # Fetch all ids from the Pinecone index
    index = pinecone.Index(index_name)
    global total_vector_count
    total_vector_count = index.describe_index_stats()['total_vector_count']
    print(total_vector_count)

def main():
    index = connect_to_DB()
    get_chunk_count(index)

    while True:
        print("\nMenu:")
        print("Test - T")
        print("Answer - A")
        print("Quit - Q")
        choice = input("Enter your choice: ").upper()

        if choice == 'T':
            Test()
        elif choice == 'A':
            question = input("Enter your question: ")
            Answer(index, question)
        elif choice == 'Q':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
