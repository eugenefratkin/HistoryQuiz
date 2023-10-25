from llama_index import ServiceContext, VectorStoreIndex
from llama_index.vector_stores import PineconeVectorStore
from llama_index.llms import OpenAI
import pinecone
import random
import os
import json
import openai
import time
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
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"User answer:{user_answer}\n\nCorrect Answer:{correct_answer}\n\nRespond in a very short way - is the user answer fully correct or partially correct or incorrect in comparison to the correct answer?"},
                ]
            )
                # Extract and store response
        print(response['choices'][0]['message']['content'])

    except Exception as e:
        print(f"Error processing text: {response.choices[0].text.strip()}. Error: {str(e)}")

    print("The correct answer: " + correct_answer.lower())

def get_all_chunks_text(directory):
    # Load and parse the JSON file
    with open(directory + "/nodes.json", 'r') as file:
        nodes = json.load(file)
    
    # Collect the text of each node into a list
    all_chunks_text = [node['text'] for node in nodes]
    
    # Return the list of all chunks text
    return all_chunks_text


def Test():
    text = get_random_chunk_text()
    question_answer = None

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{text}\n\nGiven the text come-up with a question and answer pair. Must format the response as a JSON object with 'question' and 'answer' fields."},
                ]
            )
                # Extract and store response
        question_answer = response['choices'][0]['message']['content']  # Assume each bullet point is on a new line

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
            check_answer(user_answer, correct_answer)
            
        except json.JSONDecodeError:
            print(f"Error parsing the question and answer JSON: {question_answer}")

    else:
        print("No question and answer generated.")


def Answer(index, question):
    query_engine = index.as_query_engine(
        similarity_top_k=8, 
        response_mode='refine',
        verbose=True)
    response = query_engine.query(question)
    print(response)

def Summarize():
    all_chunks_text = get_all_chunks_text(directory)
    chunk_count = 1
    import time

    for chunk in all_chunks_text:
        success = False  # Variable to track if processing the chunk succeeded
        retries = 0  # Variable to track the number of retries

        while not success and retries < 3:  # Assuming a maximum of 3 retries per chunk
            try:
                # Make API call
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": f"{chunk}\n\nProvide bullet points only of the main hisotrical insights and key facts, such as names, locations, dates, numbers. Do not include citations. Must be no more than 6 points, but can be less if no important information"},
                    ]
                )
                # Extract and store response
                bullet_points = response['choices'][0]['message']['content']  # Assume each bullet point is on a new line
                
                print(f"processing chunk {chunk_count}")
                
                # Append the bullet_text to the file called 'Summary.txt'
                with open(directory + '/Summary.txt', 'a') as file:
                    file.write(bullet_points + '\n')  # Add a newline character at the end for separation
                
                success = True  # Set success to True if the above code executes without throwing an exception

            except Exception as e:
                print(f"Error processing text chunk: {chunk}. Error: {str(e)}. Retrying in 5 seconds...")
                retries += 1  # Increment the retries count
                time.sleep(5)  # Wait for 5 seconds before retrying

            chunk_count += 1

        if not success:
            print(f"Failed to process chunk {chunk} after {retries} retries.")

    # Optionally, you can still return all_bullet_points if needed
    with open(directory + '/Summary.txt', 'r') as file:
        all_bullet_points = file.read().splitlines()
    
    return all_bullet_points  # Return the concatenated list of all bullet points


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
        print("Summarize - S")
        print("Quit - Q")
        choice = input("Enter your choice: ").upper()

        if choice == 'T':
            Test()
        elif choice == 'S':
            Summarize()
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
