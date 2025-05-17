from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_migrate import Migrate
import os
import nltk
import fitz  # PyMuPDF
import docx
from flashtext import KeywordProcessor

# === Step 1: Flask App Setup ===
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ats.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# === Step 2: NLTK Download (Run once) ===
nltk.download('punkt')

# === Step 3: Skills List ===
keyword_list = ['python', 'flask', 'sql', 'django', 'api', 'machine learning', 'data', 'analysis']
keyword_processor = KeywordProcessor()
keyword_processor.add_keywords_from_list(keyword_list)

# === Step 4: Database Model ===
class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    resume_filename = db.Column(db.String(255))
    skills = db.Column(db.Text)
    score = db.Column(db.Integer)
    parsed = db.Column(db.Boolean, default=False)

# === Step 5: WTForm for Upload ===
class ResumeUploadForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    resume = FileField('Resume', validators=[DataRequired()])
    submit = SubmitField('Upload Resume')

# === Step 6: Resume Parsing Logic (Updated to remove textract) ===
def extract_text_from_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".pdf":
        text = ""
        doc = fitz.open(filepath)
        for page in doc:
            text += page.get_text()
        return text
    elif ext == ".docx":
        doc = docx.Document(filepath)
        return "\n".join([para.text for para in doc.paragraphs])
    elif ext == ".txt":
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return ""

def parse_resume(filepath):
    try:
        text = extract_text_from_file(filepath)
        found_keywords = keyword_processor.extract_keywords(text.lower())
        unique_skills = list(set(found_keywords))
        score = int((len(unique_skills) / len(keyword_list)) * 100)
        return ', '.join(unique_skills), score
    except Exception as e:
        print(f"Error parsing resume: {e}")
        return '', 0

# === Step 7: Routes ===
@app.route('/', methods=['GET', 'POST'])
def homepage():
    form = ResumeUploadForm()
    if form.validate_on_submit():
        file = form.resume.data
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        skills, score = parse_resume(filepath)

        candidate = Candidate(
            full_name=form.full_name.data,
            email=form.email.data,
            phone=form.phone.data,
            resume_filename=filename,
            skills=skills,
            score=score,
            parsed=True
        )
        db.session.add(candidate)
        db.session.commit()

        return redirect(url_for('roleplay'))

    return render_template('homepage.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Dummy login check (replace with real logic)
        if email == 'admin@example.com' and password == 'admin123':
            session['user'] = email
            flash('Login successful', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/roleplay')
def roleplay():
    return render_template('roleplay.html')

@app.route('/HR')
def HR():
    return render_template('HR.html')

@app.route('/dashbord3', methods=['POST'])
def dashbord3():
    # Handle form data here
    return redirect(url_for('dsahbord3.html'))  # or any appropriate page




# === Step 8: Run Server ===
if __name__ == '__main__':
    app.run(debug=True)