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

# Example usage:
pdf_path = "/Users/eugenefratkin/Downloads/Copy of Chapter 6.pdf"
extracted_text = pdf_image_to_text(pdf_path)

# Output or use the extracted text
print(extracted_text)