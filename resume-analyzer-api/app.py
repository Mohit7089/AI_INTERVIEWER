from flask import Flask, request, jsonify
from utils import *

app = Flask(__name__)

@app.route("/")
def home():
    return {"message": "API running 🚀"}

@app.route("/analyze", methods=["POST"])
def analyze():

    if "file" not in request.files:
        return {"error": "Upload file"}, 400

    file = request.files["file"]

    # ✅ everything MUST be inside this function
    text = extract_text_from_pdf(file)

    skills = extract_skills(text)
    soft_skills = extract_all_soft_skills(text)

    roles = predict_roles(text)
    roles = adjust_roles_soft(skills, roles)

    projects = extract_projects(text)
    score = calculate_score(skills, projects, text)

    return jsonify({
        "roles": roles,
        "skills": skills,
        "soft_skills": soft_skills,
        "projects": projects,
        "score": score,
        "resumeText": text
    })

if __name__ == "__main__":
    app.run(debug=True)