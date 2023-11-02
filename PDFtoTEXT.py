import pytesseract
from pdf2image import convert_from_path
import os
import json

def pdf_image_to_text(pdf_path):
    """
    Converts a PDF image into text using OCR.
    
    Parameters:
        pdf_path (str): Path to the PDF file.
        
    Returns:
        tuple: Extracted text from the PDF and its number of pages.
    """
    # Convert PDF to list of images
    images = convert_from_path(pdf_path)
    
    # Initialize text string
    extracted_text = ""
    
    # Iterate through images and perform OCR
    for i, image in enumerate(images):
        extracted_text += pytesseract.image_to_string(image)
        extracted_text += "\n--- End of Page {} ---\n".format(i+1)
    
    # Return the extracted text and the number of pages
    return extracted_text, len(images)

def convert_pdfs_in_directory(directory_path):
    # Get all PDF files in the specified directory
    pdf_files = [f for f in os.listdir(directory_path) if f.endswith('.pdf')]
    
    # Ensure there are PDF files in the directory
    if not pdf_files:
        print("No PDF files found in the specified directory.")
        return
    
    # Sort the PDF files to ensure a consistent order
    pdf_files.sort()
    
    # Iterate through each PDF file, convert to text, and save to separate txt and json files
    for pdf_file in pdf_files:
        pdf_path = os.path.join(directory_path, pdf_file)
        extracted_text, num_pages = pdf_image_to_text(pdf_path)
        
        # Create the text file name based on the PDF file
        txt_file_name = pdf_file.replace('.pdf', '.txt')
        txt_file_path = os.path.join(directory_path, txt_file_name)
        
        # Write the extracted text to the text file
        with open(txt_file_path, 'w') as txt_file:
            txt_file.write(extracted_text)
        
        # Create the JSON metadata file name based on the PDF file
        json_file_name = pdf_file.replace('.pdf', '.json')
        json_file_path = os.path.join(directory_path, json_file_name)
        
        # Write the metadata to the JSON file
        with open(json_file_path, 'w') as json_file:
            json.dump({"page_number": num_pages}, json_file, indent=4)
        
        print(f'Text from {pdf_file} has been written to {txt_file_name}. Metadata saved to {json_file_name}.')

# Example usage:
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # This gets the directory of the current script
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'test')
convert_pdfs_in_directory(UPLOAD_FOLDER)
