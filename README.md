# AI Resume Analyzer

A Flask-based web application that analyzes resumes and compares them
with a provided job description.

## Features

- Upload PDF resumes
- Upload DOCX resumes
- Extract resume text
- Identify technical and soft skills
- Calculate a basic resume score
- Compare resume keywords with a job description
- Display matched keywords
- Display missing keywords
- Generate resume improvement recommendations
- Responsive web interface

## Technologies Used

- Python
- Flask
- HTML
- CSS
- JavaScript
- PyPDF
- Python-docx

## Project Structure

```text
AI_RESUME_ANALYZER/
│
├── app.py
├── requirements.txt
├── .gitignore
│
├── templates/
│   ├── index.html
│   └── result.html
│
├── uploads/
│
└── venv/