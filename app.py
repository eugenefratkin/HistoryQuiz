from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from QuizChatbot import check_answer, Question_and_Image
import json
import threading
import time
import datetime
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # This gets the directory of the current script
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'output')
PDF_FOLDER = os.path.join(BASE_DIR, 'test')  # Assuming 'output' is a sub-directory of the script's directory
BASE_FOLDER = os.path.join(BASE_DIR, 'templates')  # Assuming 'output' is a sub-directory of the script's directory
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PDF_FOLDER'] = PDF_FOLDER
app.config['BASE_FOLDER'] = BASE_FOLDER
app.config['SECRET_KEY'] = 'tjhsoiw;lks'

# Buffer for question-answer objects
question_answer_buffer = []

# Lock for thread-safe buffer operations
buffer_lock = threading.Lock()

# Condition object to control access to the buffer
buffer_condition = threading.Condition(buffer_lock)
buffer_size = 3

def fill_buffer():
    while True:
        with buffer_condition:
            if len(question_answer_buffer) < buffer_size:
                try:
                    question_answer = Question_and_Image()
                    question_answer_buffer.append(json.loads(question_answer))
                    print(f"Add new images: {len(question_answer_buffer)}")
                except Exception as e:
                    print(f"Error while processing Question_and_Image: {e}")
                else:  # Only notify if there was no exception
                    buffer_condition.notify()
            else:
                # If buffer is full, wait for a short duration before checking again
                time.sleep(2)

def fill_buffer_from_dir(directory_path):
    # List all files in the specified directory
    all_files = os.listdir(directory_path)

    # Filter out files that match the naming pattern
    qa_files = [f for f in all_files if f.startswith('QA_') and f.endswith('.JSON')]

    for qa_file in qa_files:
        # Construct the full path to the file
        file_path = os.path.join(directory_path, qa_file)
        
        with open(file_path, 'r') as file:
            try:
                # Load the JSON content of the file
                qa_data = json.load(file)
                
                # Append the JSON content to the buffer
                question_answer_buffer.append(qa_data)

            except json.JSONDecodeError:
                print(f"Error parsing the JSON content of {qa_file}")

    print(f"Added {len(qa_files)} questions and answers from directory {directory_path} to the buffer.")

#load previously created Q&A questions into a buffer
fill_buffer_from_dir(UPLOAD_FOLDER)

#run a thread that filles new question into a buffer
threading.Thread(target=fill_buffer).start()

@app.route('/', methods=['GET', 'POST'])
def index(): 
    # Default description
    session.setdefault('description', "")
    session.setdefault('file_location', "placeholder.png")
    session.setdefault('question', "")
    session.setdefault('verdict', "")
    session.setdefault('answer', "")
    session.setdefault('right_answer', "")
    session.setdefault('pdf_filename', "")
    session.setdefault('page_number', 1)
    session.setdefault('icon_filename', "history.ico")

    if request.method == 'POST':
        if 'next' in request.form:  # Check if the "press" button was clicked
            print("Next")
            session['verdict'] = ""
            session['right_answer'] = ""
            old_file_names = session['file_location']
            print(f"file to delete { old_file_names }")

            print(f"DEBUG 1: Current time is {datetime.datetime.now()}")

            # Pop the first item from the buffer
            while not question_answer_buffer:  # Wait until the buffer is not empty
                 time.sleep(2)

            # Use the first item from the buffer and remove it
            current_question_answer = question_answer_buffer.pop(0)

            print(f"DEBUG 2: Current time is {datetime.datetime.now()}")

            session['description'] = current_question_answer.get('description', '')
            session['file_location'] = current_question_answer.get('file_location', '')
            session['question'] = current_question_answer.get('question', '')
            session['answer'] = current_question_answer.get('answer', '')  # Store the description in session
            session['fly_in'] = True  # Set a flag
            session['pdf_filename'] = current_question_answer.get('pdf_file', '')
            session['page_number'] = current_question_answer.get('page', '')

            # If there's a description in the session, it means the "Next" button was clicked and we should display the specific image.
            if session['description']:
                image_filename = session['file_location']  # This is the specific image you want to display after "Next". Change to your image's name.
                image_url = url_for('uploaded_file', filename=image_filename)

            # Replenish the buffer in a separate thread
            threading.Thread(target=fill_buffer).start()

            # Delete the first file
            old_image = os.path.join(UPLOAD_FOLDER, old_file_names)
            if os.path.exists(old_image):
                os.remove(old_image)
                print(f"'{old_image}' has been deleted.")
            else:
                print(f"'{old_image}' does not exist.")

            # Delete the second file
            old_description = os.path.join(UPLOAD_FOLDER, f"QA_{ old_file_names }.JSON")
            if os.path.exists(old_description):
                os.remove(old_description)
                print(f"'{old_description}' has been deleted.")
            else:
                print(f"'{old_description}' does not exist.")
        
            return redirect(url_for('index'))
        else:
            session['fly_in'] = False  # Clear the flag

        
        if 'test' in request.form:  # Check if the "press" button was clicked
            print("Test")
            user_answer = request.form['user_answer']  # Retrieve the user's answer from the form
            session['verdict'] = check_answer(user_answer, session['answer'])
            session['right_answer'] = session['answer']
            return redirect(url_for('index'))
        
        else:
            return "Invalid choice. Please try again.", 400

    # Generate the image URL dynamically if needed
    print("current file location: " + session['file_location'])
    image_url = url_for('uploaded_file', filename=session['file_location'])
    pdf_url = url_for('pdf_file', filename=session['pdf_filename'])
    icon_url = url_for('icon_file', filename=session['icon_filename'])

    return render_template('index.html', icon_url=icon_url, image_url=image_url, page_number=session['page_number'], description=session['description'], question=session['question'], right_answer=session['right_answer'], verdict=session['verdict'], fly_in=session.get('fly_in', False), pdf_url=pdf_url)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/pdf/<filename>')
def pdf_file(filename):
    return send_from_directory(app.config['PDF_FOLDER'], filename)

@app.route('/base/<filename>')
def icon_file(filename):
    return send_from_directory(app.config['BASE_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
