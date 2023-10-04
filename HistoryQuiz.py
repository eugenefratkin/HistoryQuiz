import openai
import os
from PDFtoTEXT import pdf_image_to_text

os.environ["OPENAI_API_KEY"] = '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'

def read_file(file_path):
    """Reads a file and returns its content as a string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return 'File not found.'
    except IOError:
        return 'Error reading the file.'
    
    
def split_into_paragraphs(large_text):
    """
    Splits a large text into logical paragraphs using GPT-3.5.
    
    Parameters:
        large_text (str): A large text to be split into paragraphs.
        
    Returns:
        list of str: A list containing the split paragraphs.
    """
    # This is a hypothetical approach and might need a lot of tuning and adjustment
    # to work for specific use-cases.
    
    paragraphs = []
    remaining_text = large_text
    
    while remaining_text:
        # Truncate or otherwise preprocess the remaining_text to fit within API limits
        # Note: You need to ensure that the text being sent to the API is under the token limit.
        snippet = remaining_text[:4096]  # Example limit, adjust as per actual token count
        
        try:
            # Make API call
            response = openai.Completion.create(
              engine="text-davinci-003",  # Use "davinci" or other available engines
              prompt=f"Identify a logical paragraph: {snippet}",
              max_tokens=100  # Adjust as needed
            )
            
            # Extract and store response
            paragraph = response.choices[0].text.strip()
            paragraphs.append(paragraph)
            
            # Update remaining_text by removing the identified paragraph
            # This is a simplified approach and might not work perfectly
            remaining_text = remaining_text[len(paragraph):]
        
        except Exception as e:
            print(f"Error processing text: {snippet}. Error: {str(e)}")
            break
    
    return paragraphs

def split_into_chunks(text, max_tokens=3000):
    """
    Splits a text string into chunks, each containing fewer than max_tokens characters.
    Note: This function does not ensure that the chunks have fewer than max_tokens OpenAI API tokens.
    
    Parameters:
        text (str): The input text.
        max_tokens (int): The maximum number of characters for each chunk.
        
    Returns:
        list: A list of text chunks.
    """
    chunks = []
    start_index = 0
    
    while start_index < len(text):
        # Get a chunk of text with max_tokens
        end_index = start_index + max_tokens
        
        # If the chunk is smaller than max_tokens, we're at the end
        if end_index >= len(text):
            chunks.append(text[start_index:])
            break
        
        # Find the last space in the chunk and adjust end_index
        last_space_index = text.rfind(' ', start_index, end_index)
        if last_space_index != -1:
            end_index = last_space_index
        
        chunks.append(text[start_index:end_index])
        start_index = end_index
        
    return chunks


# Ensure your OpenAI API key is set as an environment variable
# export OPENAI_API_KEY='your-api-key'

def query_gpt(chunks):
    """
    Sends a series of strings to GPT-3.5 and returns the results.
    
    Parameters:
        texts (list of str): Text strings to be processed by GPT-3.5
    
    Returns:
        list of str: GPT-3.5 responses for each input string
    """
    responses = []
    
    # Ensure API key is available
    if "OPENAI_API_KEY" not in os.environ:
        raise ValueError("API key for OpenAI is missing. Ensure OPENAI_API_KEY is set.")
    
    # Set up OpenAI API client
    openai.api_key = os.environ["OPENAI_API_KEY"]
    
    # Loop through texts and query GPT-3.5
    for chunk in chunks:
        try:
            # Make API call
            # Note: You might need to adjust the model and other parameters as per your use case
            response = openai.Completion.create(
              engine="text-davinci-003",  # Use "davinci" or other available engines
              prompt=f"{chunk}\n\nSummarize in as many bullet points as you need to capture the main ideas:",
              max_tokens=3500  # Adjust as needed
            )
            
            # Extract and store response
            responses.append(response.choices[0].text.strip())
        
        except Exception as e:
            print(f"Error processing text: {chunk}. Error: {str(e)}")
            responses.append(None)
    
    return responses

def summarize_file():
    """
    Summarizes the content of a file by breaking it into chunks and summarizing each chunk using GPT-3.5.
    
    Returns:
        str: A concatenated string of all the summarized chunks.
    """
    # Prompt the user for a file path
    file_path = input("Please enter the path to the file you want to summarize: ")
    
    # Read the file content
    #file_content = pdf_image_to_text(file_path)
    file_content = read_file(file_path)
    
    # Check if file reading was successful
    if file_content in ['File not found.', 'Error reading the file.']:
        return file_content
    
    # Split the content into chunks
    chunks = split_into_chunks(file_content)
    
    # Get summaries for each chunk
    summaries = query_gpt(chunks)
    
    # Concatenate summaries into a single string
    full_summary = ' '.join([summary for summary in summaries if summary])
    
    return full_summary

# Example usage:
print(summarize_file())







