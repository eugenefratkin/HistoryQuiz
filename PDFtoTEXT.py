import pytesseract
from pdf2image import convert_from_path
import os

def pdf_image_to_text(pdf_path):
    """
    Converts a PDF image into text using OCR.
    
    Parameters:
        pdf_path (str): Path to the PDF file.
        
    Returns:
        str: Extracted text from the PDF.
    """
    # Convert PDF to list of images
    images = convert_from_path(pdf_path)
    
    # Initialize text string
    extracted_text = ""
    
    # Iterate through images and perform OCR
    for i, image in enumerate(images):
        extracted_text += pytesseract.image_to_string(image)
        extracted_text += "\n--- End of Page {} ---\n".format(i+1)
    
    return extracted_text

def convert_pdfs_in_directory(directory_path):
    # Get all PDF files in the specified directory
    pdf_files = [f for f in os.listdir(directory_path+"/test") if f.endswith('.pdf')]
    
    # Ensure there are PDF files in the directory
    if not pdf_files:
        print("No PDF files found in the specified directory.")
        return
    
    # Sort the PDF files to ensure a consistent order
    pdf_files.sort()
    
    # Initialize an empty string to store the concatenated text
    concatenated_text = ""
    
    # Iterate through each PDF file and convert to text
    for pdf_file in pdf_files:
        pdf_path = os.path.join(directory_path+"/test", pdf_file)
        concatenated_text += pdf_image_to_text(pdf_path)
    
    # Create the text file name based on the first PDF file
    txt_file_name = pdf_files[0].replace('.pdf', '.txt')
    txt_file_path = os.path.join(directory_path+"/output", txt_file_name)
    
    # Write the concatenated text to the text file
    with open(txt_file_path, 'w') as txt_file:
        txt_file.write(concatenated_text)
    
    print(f'Text has been written to {txt_file_path}')

# Example usage:
directory_path = "/Users/efratkin/Code Projects/HistoryQuiz"
convert_pdfs_in_directory(directory_path)
