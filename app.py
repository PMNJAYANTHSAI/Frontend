from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from deep_translator import GoogleTranslator
import speech_recognition as sr
from gtts import gTTS
import os
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management
app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder to store uploaded files
app.config['ALLOWED_EXTENSIONS'] = {'mp3'}  # Allowed file extensions

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # Database file will be created in the project directory
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define User model for the database
class User(db.Model):
    __tablename__ = 'users'  # Explicitly set the table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Create the database and tables (run this only once)
with app.app_context():
    db.create_all()

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = username  # Store username in session
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if the username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different username.')
        else:
            # Create a new user
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
    return render_template('register.html')

# Dashboard route (after login)
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))

# Audio translation route
@app.route('/translate_audio', methods=['POST'])
def translate_audio():
    if 'username' not in session:
        return jsonify({'message': 'Please login to use this feature.'}), 403

    # Check if the file is uploaded
    if 'file' not in request.files:
        return jsonify({'message': 'No file uploaded.'}), 400
    file = request.files['file']

    # Check if the file is allowed
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'message': 'Invalid file. Please upload an MP3 file.'}), 400

    # Save the uploaded file
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Get the target language
    target_language = request.form.get('language', 'en')  # Default to English if not provided

    # Transcribe the audio to text
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
    except Exception as e:
        return jsonify({'message': 'Failed to transcribe audio. Please try again.', 'error': str(e)}), 500

    # Translate the text
    try:
        translation = GoogleTranslator(source='auto', target=target_language).translate(text)
    except Exception as e:
        return jsonify({'message': 'Translation failed. Please try again.', 'error': str(e)}), 500

    # Convert translated text to audio
    try:
        tts = gTTS(translation, lang=target_language)
        translated_audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'translated_' + filename)
        tts.save(translated_audio_path)
    except Exception as e:
        return jsonify({'message': 'Failed to generate translated audio. Please try again.', 'error': str(e)}), 500

    # Return the translated audio file
    return send_file(translated_audio_path, as_attachment=True)

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove username from session
    return redirect(url_for('index'))

# Run the application
if __name__ == '__main__':
    app.run(debug=True)