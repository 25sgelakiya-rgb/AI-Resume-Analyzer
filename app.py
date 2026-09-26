from flask import Flask, render_template, request
from pypdf import PdfReader
from docx import Document
import os
import re

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -----------------------------
# Skills database
# -----------------------------
SKILLS = [
    "python", "java", "javascript", "html", "css", "react",
    "angular", "node.js", "flask", "django", "fastapi",
    "sql", "mysql", "postgresql", "mongodb",
    "git", "github", "docker",
    "machine learning", "deep learning",
    "data science", "pandas", "numpy",
    "scikit-learn", "tensorflow", "pytorch",
    "nlp", "natural language processing",
    "rest api", "api", "aws", "azure",
    "communication", "leadership", "teamwork",
    "problem solving", "data analysis", "excel"
]


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# -----------------------------
# Extract text from PDF
# -----------------------------
def extract_pdf_text(filepath):
    text = ""

    reader = PdfReader(filepath)

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# -----------------------------
# Extract text from DOCX
# -----------------------------
def extract_docx_text(filepath):
    document = Document(filepath)

    paragraphs = []

    for paragraph in document.paragraphs:
        paragraphs.append(paragraph.text)

    return "\n".join(paragraphs)


# -----------------------------
# Extract skills
# -----------------------------
def find_skills(text):
    text_lower = text.lower()

    found = []

    for skill in SKILLS:
        if skill.lower() in text_lower:
            found.append(skill.title())

    return sorted(set(found))


# -----------------------------
# Job description matching
# -----------------------------
def analyze_job_match(resume_text, job_description):
    resume_lower = resume_text.lower()
    job_lower = job_description.lower()

    job_words = set(
        re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#.-]{2,}\b", job_lower)
    )

    stop_words = {
        "the", "and", "for", "with", "that", "this",
        "from", "your", "you", "are", "our", "will",
        "have", "has", "job", "role", "work", "using",
        "years", "year", "required", "skills"
    }

    important_words = {
        word for word in job_words
        if word not in stop_words
    }

    matched = []
    missing = []

    for word in sorted(important_words):
        if word in resume_lower:
            matched.append(word)
        else:
            missing.append(word)

    if important_words:
        match_percentage = round(
            (len(matched) / len(important_words)) * 100
        )
    else:
        match_percentage = 0

    return matched[:30], missing[:30], match_percentage


# -----------------------------
# Generate recommendations
# -----------------------------
def recommendations(skills, missing_skills, match_score):
    recommendations_list = []

    if not skills:
        recommendations_list.append(
            "Add a clear technical skills section to your resume."
        )

    if match_score < 50:
        recommendations_list.append(
            "Customize your resume keywords according to the job description."
        )

    if match_score >= 50:
        recommendations_list.append(
            "Your resume contains several keywords from the job description."
        )

    if not any("project" in item.lower() for item in missing_skills):
        recommendations_list.append(
            "Include relevant projects with technologies and measurable results."
        )

    recommendations_list.append(
        "Use action verbs and measurable achievements where possible."
    )

    recommendations_list.append(
        "Keep formatting simple and easy for applicant tracking systems to read."
    )

    return recommendations_list


# -----------------------------
# Home page
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# Analyze resume
# -----------------------------
@app.route("/analyze", methods=["POST"])
def analyze():

    if "resume" not in request.files:
        return "No resume uploaded.", 400

    file = request.files["resume"]

    if file.filename == "":
        return "Please select a resume.", 400

    if not allowed_file(file.filename):
        return "Only PDF and DOCX files are allowed.", 400

    filename = file.filename.replace(" ", "_")
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    file.save(filepath)

    extension = filename.rsplit(".", 1)[1].lower()

    try:
        if extension == "pdf":
            resume_text = extract_pdf_text(filepath)
        else:
            resume_text = extract_docx_text(filepath)

    except Exception as error:
        return f"Could not read the resume: {error}", 500

    job_description = request.form.get("job_description", "")

    skills = find_skills(resume_text)

    matched_keywords, missing_keywords, match_score = analyze_job_match(
        resume_text,
        job_description
    )

    # Basic resume score
    score = 0

    if len(resume_text) > 500:
        score += 25

    if skills:
        score += 25

    if "education" in resume_text.lower():
        score += 10

    if "experience" in resume_text.lower():
        score += 15

    if "project" in resume_text.lower():
        score += 15

    if "contact" in resume_text.lower() or "email" in resume_text.lower():
        score += 10

    score = min(score, 100)

    recommendations_list = recommendations(
        skills,
        missing_keywords,
        match_score
    )

    return render_template(
        "result.html",
        filename=filename,
        score=score,
        skills=skills,
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
        match_score=match_score,
        recommendations=recommendations_list
    )


if __name__ == "__main__":
    app.run(debug=True)