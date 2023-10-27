from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from QuizChatbot import Test, Answer, Image, check_answer, Question_and_Image
import json

app = Flask(__name__)

UPLOAD_FOLDER = '/Users/efratkin/Code Projects/HistoryQuiz/output'  # e.g., 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'tjhsoiw;lks'

@app.route('/', methods=['GET', 'POST'])
def index():
    # Default description
    session.setdefault('description', "")
    session.setdefault('question', "")
    session.setdefault('verdict', "")
    session.setdefault('answer', "")
    session.setdefault('right_answer', "")

    if request.method == 'POST':
        if 'next' in request.form:  # Check if the "press" button was clicked
            print("Next")
            question_answer = Question_and_Image()
            session['description'] = json.loads(question_answer).get('description', '') 
            session['question'] = json.loads(question_answer).get('question', '')
            session['answer'] = json.loads(question_answer).get('answer', '')  # Store the description in session
            return redirect(url_for('index'))
        
        if 'test' in request.form:  # Check if the "press" button was clicked
            print("Test")
            user_answer = request.form['user_answer']  # Retrieve the user's answer from the form
            session['verdict'] = check_answer(user_answer, session['answer'])
            session['right_answer'] = session['answer']
            return redirect(url_for('index'))
        
        else:
            return "Invalid choice. Please try again.", 400

    # Generate the image URL dynamically if needed
    image_url = url_for('uploaded_file', filename='local_image.jpg')

    return render_template('index.html', image_url=image_url, description=session['description'], question=session['question'], right_answer=session['right_answer'], verdict=session['verdict'])


# ... (previous code) ...

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ... (rest of the code) ...


if __name__ == '__main__':
    app.run(debug=True)
