from flask import Flask, render_template, request
from pypdf import PdfReader
from docx import Document
import os
import re

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Skills used for resume analysis
SKILLS = [
    "python", "java", "javascript", "html", "css",
    "react", "angular", "node.js", "flask", "django",
    "fastapi", "sql", "mysql", "postgresql", "mongodb",
    "git", "github", "docker", "machine learning",
    "deep learning", "data science", "pandas", "numpy",
    "scikit-learn", "tensorflow", "pytorch",
    "nlp", "natural language processing",
    "rest api", "api", "aws", "azure",
    "communication", "leadership", "teamwork",
    "problem solving", "data analysis", "excel"
]


STOP_WORDS = {
    "the", "and", "for", "with", "that", "this", "from",
    "have", "has", "are", "was", "were", "will", "your",
    "you", "our", "their", "they", "job", "role", "work",
    "looking", "candidate", "experience", "years", "good",
    "skills", "skill", "using", "about", "into", "also",
    "should", "would", "must", "required", "requirements"
}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def extract_pdf_text(filepath):
    text = ""

    reader = PdfReader(filepath)

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def extract_docx_text(filepath):
    document = Document(filepath)

    paragraphs = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            paragraphs.append(paragraph.text)

    return "\n".join(paragraphs)


def extract_text(filepath):
    extension = filepath.rsplit(".", 1)[1].lower()

    if extension == "pdf":
        return extract_pdf_text(filepath)

    if extension == "docx":
        return extract_docx_text(filepath)

    return ""


def find_skills(text):
    text_lower = text.lower()
    found_skills = []

    for skill in SKILLS:
        if skill.lower() in text_lower:
            found_skills.append(skill.title())

    return sorted(set(found_skills))


def extract_keywords(text):
    words = re.findall(
        r"\b[a-zA-Z][a-zA-Z+#.-]{2,}\b",
        text.lower()
    )

    keywords = []

    for word in words:
        word = word.strip(".,;:()[]{}")

        if word in STOP_WORDS:
            continue

        if len(word) < 3:
            continue

        if word not in keywords:
            keywords.append(word)

    return keywords


def job_description_match(resume_text, job_description):
    if not job_description.strip():
        return 0, [], []

    resume_lower = resume_text.lower()
    job_keywords = extract_keywords(job_description)

    matched = []
    missing = []

    for keyword in job_keywords:
        if keyword in resume_lower:
            matched.append(keyword)
        else:
            missing.append(keyword)

    if not job_keywords:
        percentage = 0
    else:
        percentage = round(
            (len(matched) / len(job_keywords)) * 100
        )

    return percentage, sorted(matched), sorted(missing)


def calculate_score(text, skills):
    text_lower = text.lower()

    score = 0
    feedback = []

    word_count = len(text.split())

    # Resume length
    if word_count >= 300:
        score += 15
    elif word_count >= 150:
        score += 10
        feedback.append(
            "Consider adding more relevant details to strengthen your resume."
        )
    else:
        score += 5
        feedback.append(
            "Your resume appears short. Add relevant projects, "
            "experience, or achievements."
        )

    # Skills
    if len(skills) >= 8:
        score += 20
    elif len(skills) >= 4:
        score += 15
        feedback.append(
            "Consider adding more relevant technical and professional skills."
        )
    else:
        score += 8
        feedback.append(
            "Add more relevant skills that match your target job."
        )

    # Education
    if any(word in text_lower for word in [
        "education",
        "bachelor",
        "master",
        "degree",
        "university",
        "college"
    ]):
        score += 15
    else:
        feedback.append("Add a clear Education section.")

    # Experience
    if any(word in text_lower for word in [
        "experience",
        "internship",
        "employment",
        "worked"
    ]):
        score += 15
    else:
        feedback.append(
            "Add work experience or internship details if applicable."
        )

    # Projects
    if "project" in text_lower or "projects" in text_lower:
        score += 15
    else:
        feedback.append(
            "Add relevant projects and explain the technologies used."
        )

    # Email
    if re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text):
        score += 10
    else:
        feedback.append(
            "Add a professional email address."
        )

    # Phone number
    digits_only = re.sub(r"\D", "", text)

    if re.search(r"\d{10}", digits_only):
        score += 5
    else:
        feedback.append(
            "Consider adding a professional phone number."
        )

    return min(score, 100), feedback


def generate_recommendations(
    resume_text,
    job_description,
    skills,
    matched_keywords,
    missing_keywords
):
    recommendations = []

    text_lower = resume_text.lower()

    # Job description analysis
    if job_description.strip():

        if missing_keywords:
            important_missing = missing_keywords[:8]

            recommendations.append(
                "Consider naturally including relevant job keywords such as: "
                + ", ".join(important_missing)
                + ". Only include skills you genuinely have."
            )

        if len(matched_keywords) >= 5:
            recommendations.append(
                "Your resume already contains several keywords "
                "related to the target job."
            )

        if len(missing_keywords) > len(matched_keywords):
            recommendations.append(
                "The job description contains many terms that are not "
                "currently visible in your resume. Review the requirements "
                "and add relevant evidence from your actual experience."
            )

    # Projects
    if "project" not in text_lower:
        recommendations.append(
            "Add a Projects section with project names, technologies, "
            "your contribution, and measurable results where possible."
        )

    # Experience
    if "experience" not in text_lower and "internship" not in text_lower:
        recommendations.append(
            "Add relevant internship, work, freelance, or practical experience."
        )

    # Skills
    if len(skills) < 5:
        recommendations.append(
            "Add relevant technical and professional skills that you actually possess."
        )

    # Action verbs
    action_verbs = [
        "developed",
        "created",
        "built",
        "designed",
        "implemented",
        "improved",
        "managed",
        "analyzed"
    ]

    if not any(verb in text_lower for verb in action_verbs):
        recommendations.append(
            "Use strong action verbs such as developed, implemented, "
            "designed, analyzed, or improved when describing your work."
        )

    # Measurable achievements
    if not re.search(
        r"\b\d+%|\b\d+\+|\b\d+\s*(users|projects|clients|records|hours)",
        text_lower
    ):
        recommendations.append(
            "Where possible, add measurable achievements such as "
            "percentages, numbers, users, projects, or performance improvements."
        )

    # ATS formatting
    recommendations.append(
        "Keep formatting simple, clear, and ATS-friendly with "
        "consistent headings and spacing."
    )

    return recommendations


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    if "resume" not in request.files:
        return "No resume file uploaded."

    file = request.files["resume"]

    if file.filename == "":
        return "Please select a resume file."

    if not allowed_file(file.filename):
        return "Only PDF and DOCX files are supported."

    filename = file.filename
    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    file.save(filepath)

    resume_text = extract_text(filepath)

    if not resume_text.strip():
        return "Could not extract text from the resume."

    job_description = request.form.get(
        "job_description",
        ""
    )

    skills = find_skills(resume_text)

    match_percentage, matched_keywords, missing_keywords = (
        job_description_match(
            resume_text,
            job_description
        )
    )

    score, score_feedback = calculate_score(
        resume_text,
        skills
    )

    recommendations = generate_recommendations(
        resume_text,
        job_description,
        skills,
        matched_keywords,
        missing_keywords
    )

    recommendations = score_feedback + recommendations

    # Remove duplicate recommendations
    recommendations = list(
        dict.fromkeys(recommendations)
    )

    summary = (
        f"The analyzer detected {len(skills)} relevant skills "
        f"and matched {match_percentage}% of the provided "
        f"job-description keywords."
    )

    return render_template(
        "result.html",
        score=score,
        match_percentage=match_percentage,
        skills=skills,
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
        recommendations=recommendations,
        summary=summary
    )


if __name__ == "__main__":
    app.run(debug=True)