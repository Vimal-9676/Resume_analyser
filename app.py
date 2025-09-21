# backend/app.py
import os, uuid, re
from flask import Flask, request, jsonify
from flask_cors import CORS
import pdfplumber
import spacy

# locate frontend folder (relative)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "frontend"))

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)

# load small spacy model (download required once)
nlp = spacy.load("en_core_web_sm")

# small skill list to start with — expand this later
SKILLS = ["python","java","c++","sql","javascript","html","css","git","docker","react","node","django","flask","machine learning","nlp"]

def extract_text_from_pdf(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text

def extract_skills(text):
    L = text.lower()
    found = [s for s in SKILLS if s in L]
    return found

def score_resume(text, skills):
    s = 0
    if "project" in text.lower(): s += 2
    if "experience" in text.lower(): s += 2
    s += min(len(skills), 6)   # up to 6 points
    return max(0, min(10, s))

@app.route("/")
def index():
    # serve frontend/index.html
    return app.send_static_file("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    if "resume" not in request.files:
        return jsonify({"error":"No file part 'resume'"}), 400
    f = request.files["resume"]
    if f.filename == "":
        return jsonify({"error":"No selected file"}), 400

    tmp_path = f"/tmp/{uuid.uuid4()}.pdf"
    f.save(tmp_path)

    try:
        text = extract_text_from_pdf(tmp_path)
    except Exception as e:
        os.remove(tmp_path)
        return jsonify({"error":"Failed to read PDF", "details": str(e)}), 500

    skills = extract_skills(text)
    score = score_resume(text, skills)

    # simple 1-line summary generation (very basic)
    summary = "Candidate skilled in " + ", ".join(skills[:4]) if skills else "Candidate shows fundamentals; needs more listed skills."

    suggestions = []
    if score < 6:
        suggestions.append("Add quantified outcomes (e.g., 'reduced X by Y%').")
    if not skills:
        suggestions.append("Create a clear 'Skills' section and list technologies/tools.")
    if "intern" in text.lower() or "project" in text.lower():
        suggestions.append("Highlight projects with tech stack + impact lines.")

    # cleanup
    os.remove(tmp_path)

    return jsonify({
        "score": score,
        "skills": skills,
        "summary": summary,
        "suggestions": suggestions
    })

if __name__ == "__main__":
    # runs on http://127.0.0.1:5000/
    app.run(debug=True, port=5000)