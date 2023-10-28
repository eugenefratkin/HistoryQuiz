from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from QuizChatbot import Test, Answer, Image, check_answer, Question_and_Image
import json
import threading
import time
import datetime
import queue

app = Flask(__name__)

UPLOAD_FOLDER = '/Users/efratkin/Code Projects/HistoryQuiz/output'  # e.g., 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'tjhsoiw;lks'

# Buffer for question-answer objects
question_answer_buffer = []

# Lock for thread-safe buffer operations
buffer_lock = threading.Lock()

# Condition object to control access to the buffer
buffer_condition = threading.Condition(buffer_lock)
buffer_size = 2

def fill_buffer():
    while True:
        # Check if the buffer has less than buffer_size elements
        with buffer_condition:
            if len(question_answer_buffer) < buffer_size:
                question_answer = Question_and_Image()
                question_answer_buffer.append(json.loads(question_answer))
                print(f"After Buffer size is: {len(question_answer_buffer)}")
                buffer_condition.notify()  # Notify any waiting threads
            else:
                # If buffer is full (5 elements), wait for a short duration before checking again
                time.sleep(3)

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

    if request.method == 'POST':
        if 'next' in request.form:  # Check if the "press" button was clicked
            print("Next")
            session['verdict'] = ""
            session['right_answer'] = ""

            print(f"DEBUG 1: Current time is {datetime.datetime.now()}")

            # Pop the first item from the buffer
            with buffer_condition:
                print(f"Current Buffer size is: {len(question_answer_buffer)}")
                while not question_answer_buffer:  # Wait until the buffer is not empty
                    buffer_condition.wait()
                # Use the first item from the buffer and remove it
                current_question_answer = question_answer_buffer.pop(0)

            print(f"DEBUG 2: Current time is {datetime.datetime.now()}")

            session['description'] = current_question_answer.get('description', '')
            session['file_location'] = current_question_answer.get('file_location', '')
            session['question'] = current_question_answer.get('question', '')
            session['answer'] = current_question_answer.get('answer', '')  # Store the description in session
            session['fly_in'] = True  # Set a flag

            # If there's a description in the session, it means the "Next" button was clicked and we should display the specific image.
            if session['description']:
                image_filename = session['file_location']  # This is the specific image you want to display after "Next". Change to your image's name.
                image_url = url_for('uploaded_file', filename=image_filename)

            # Replenish the buffer in a separate thread
            #threading.Thread(target=fill_buffer).start()
        
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

    return render_template('index.html', image_url=image_url, description=session['description'], question=session['question'], right_answer=session['right_answer'], verdict=session['verdict'], fly_in=session.get('fly_in', False))


# ... (previous code) ...

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ... (rest of the code) ...


if __name__ == '__main__':
    app.run(debug=True)
