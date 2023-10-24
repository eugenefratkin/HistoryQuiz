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
    try:
        # Make API call
        # Note: You might need to adjust the model and other parameters as per your use case
        response = openai.Completion.create(
            engine="text-davinci-003",  # Use "davinci" or other available engines
            prompt=f"User answer:{user_answer}\n\nCorrect Answer:{correct_answer}\n\nRespond in a very short way - is the user answer fully correct or partially correct or incorrect in comparison to the correct answer?",
            max_tokens=3500  # Adjust as needed
        )
                    # Extract and store response
        print(response.choices[0].text.strip())

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
        # Make API call
        # Note: You might need to adjust the model and other parameters as per your use case
        response = openai.Completion.create(
            engine="text-davinci-003",  # Use "davinci" or other available engines
            prompt=(
                f"{text}\n\nGiven the text come-up with a question and answer pair."
                "Format the response as a JSON object with 'question' and 'answer' fields."
            ),
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
    all_bullet_points = []  # Initialize an empty list to hold all bullet points

    chunk_count = 1
    for chunk in all_chunks_text:
        try:
            # Make API call
            response = openai.Completion.create(
                engine="text-davinci-003",  # Use "davinci" or other available engines
                prompt=(
                    f"{chunk}\n\nProvide bullet points of the main ideas and key facts. Only key facts no more than 5-7 points"
                ),
                max_tokens=3500  # Adjust as needed
            )
            # Extract and store response
            bullet_points = response.choices[0].text.strip().split('\n')  # Assume each bullet point is on a new line
            
            print(f"processing chunk {chunk_count}")
            chunk_count+=1
            # Extend the all_bullet_points list with the bullet points from this response
            all_bullet_points.extend(bullet_points)

        except Exception as e:
            print(f"Error processing text chunk: {chunk}. Error: {str(e)}")

    # Convert the list of all bullet points to a single string with one bullet point per line
    summary_text = '\n'.join(all_bullet_points)
    
    # Write the summary_text to a file called 'Summary'
    with open(directory + '/Summary.txt', 'w') as file:
        file.write(summary_text)
    
    return all_bullet_points  # Return the concatenated list of all bullet points

def Summarize_chat():
    all_chunks_text = get_all_chunks_text(directory)
    all_bullet_points = []  # Initialize an empty list to hold all bullet points

    chunk_count = 1
    for chunk in all_chunks_text:
        try:
            # Make API call
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"{chunk}\n\nProvide bullet points of the main ideas and key facts. Only key facts no more than 5-7 points"},
                ]
            )
            # Extract and store response
            bullet_points = response['choices'][0]['message']['content']  # Assume each bullet point is on a new line
            
            print(f"processing chunk {chunk_count}")
            chunk_count+=1
            # Extend the all_bullet_points list with the bullet points from this response
            all_bullet_points.extend(bullet_points)

        except Exception as e:
            print(f"Error processing text chunk: {chunk}. Error: {str(e)}")

    # Convert the list of all bullet points to a single string with one bullet point per line
    summary_text = '\n'.join(all_bullet_points)
    
    # Write the summary_text to a file called 'Summary'
    with open(directory + '/Summary-chat.txt', 'w') as file:
        file.write(summary_text)
    
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
            Summarize_chat()
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
