import pickle
import re
import pdfplumber

# -------- LOAD MODELS --------
model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))
le = pickle.load(open("label_encoder.pkl", "rb"))

model_lines = pickle.load(open("model_lines.pkl", "rb"))
vectorizer_lines = pickle.load(open("vectorizer_lines.pkl", "rb"))

# -------- CLEAN TEXT --------
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
    return text

# -------- PDF --------
import pytesseract
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

from PIL import Image
import pdfplumber
import tempfile

def extract_text_from_pdf(file):
    text = ""

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            t = page.extract_text()

            if t:
                text += t + "\n"
            else:
                with tempfile.NamedTemporaryFile(suffix=".png") as temp_img:
                    page_image = page.to_image(resolution=300)
                    page_image.save(temp_img.name, format="PNG")

                    ocr_text = pytesseract.image_to_string(
                        Image.open(temp_img.name),
                        config="--oem 3 --psm 6"
                    )

                    text += ocr_text + "\n"

    print("TEXT LENGTH:", len(text))  # DEBUG

    return text
# -------- SKILLS --------
def extract_skills(text):
    skills_db = [
        "python","java","c","c++","html","css",
        "javascript","typescript",
        "react","angular","vue","bootstrap","tailwind",
        "node","express","spring","django","flask",
        "sql","mysql","postgresql","mongodb",
        "aws","docker","kubernetes","git",
        "pandas","numpy","matplotlib","seaborn",
        "scikit-learn","machine learning","deep learning",
        "swing","jdbc"
    ]

    text = text.lower()
    return list(set([s for s in skills_db if s in text]))

# -------- SOFT SKILLS --------
def extract_all_soft_skills(text):

    text = text.lower()

    soft_skills_db = [
        "communication","leadership","teamwork","collaboration",
        "problem solving","critical thinking","adaptability",
        "time management","creativity","decision making",
        "analytical thinking"
    ]

    direct = [s for s in soft_skills_db if s in text]

    # 🔥 improved mapping
    mapping = {
        "developed": "problem solving",
        "designed": "creativity",
        "implemented": "problem solving",
        "analyzed": "analytical thinking",
        "identified": "analytical thinking",
        "proposed": "decision making",
        "led": "leadership",
        "collaborated": "teamwork",
        "built": "problem solving",
        "created": "creativity"
    }

    inferred = [v for k, v in mapping.items() if k in text]

    return list(set(direct + inferred))

# -------- PROJECTS --------
def extract_projects(text):

    lines = [l.strip() for l in text.split('\n') if l.strip()]

    X = vectorizer_lines.transform(lines)
    preds = model_lines.predict(X)

    projects = []
    current_project = None
    in_project_section = False

    for line, label in zip(lines, preds):

        clean = re.sub(r'\s+', ' ', line)
        lower = clean.lower()

        # detect project section
        if "project" in lower:
            in_project_section = True

        # stop at other sections
        if any(x in lower for x in ["education", "technical skills", "skills"]):
            in_project_section = False

        if not in_project_section:
            continue

        clean = re.sub(r'(?i)projects?', '', clean).strip()

        # 🔥 improved title detection
        if (
            label == "TITLE" and
            2 <= len(clean.split()) <= 8 and
            not clean.endswith('.') and
            not any(x in clean.lower() for x in [
                "java","python","sql","html","css","react",
                "c++","javascript","node"
            ])
        ):
            current_project = {
                "project_name": clean,
                "summary": ""
            }
            projects.append(current_project)
            continue

        # description
        if current_project:
            if len(clean.split()) > 5:
                current_project["summary"] += " " + clean

    final = []
    for p in projects:
        if len(p["summary"].split()) > 5:
            final.append({
                "project_name": p["project_name"],
                "summary": " ".join(p["summary"].split()[:25]) + "..."
            })

    return final[:5]

# -------- ROLES --------
def predict_roles(text):
    cleaned = clean_text(text)
    vec = vectorizer.transform([cleaned])

    probs = model.predict_proba(vec)[0]

    roles = sorted(
        zip(le.classes_, probs),
        key=lambda x: x[1],
        reverse=True
    )[:3]

    total = sum([p for _, p in roles])
    roles = [(r, float(p/total)) for r, p in roles]

    return roles

def adjust_roles_soft(skills, roles, text=""):
    role_dict = dict(roles)
    skills_set = set(s.lower() for s in skills)
    text = text.lower()

    # 🔥 FULL STACK DETECTION (improved)
    if (
        ("react" in skills_set or "angular" in skills_set)
        and ("node" in skills_set or "express" in skills_set)
    ):
        role_dict["Full Stack Developer"] = role_dict.get("Full Stack Developer", 0) + 0.8

    # 🔥 BACKEND (Python)
    if "django" in skills_set or "flask" in skills_set:
        role_dict["Python Developer"] = role_dict.get("Python Developer", 0) + 0.2

    # 🔥 JAVA (only if strong signal)
    if "spring" in skills_set and "java" in skills_set:
        role_dict["Java Developer"] = role_dict.get("Java Developer", 0) + 0.4
    elif "spring" in skills_set:
        role_dict["Backend Developer"] = role_dict.get("Backend Developer", 0) + 0.3

    # 🔥 REDUCE PYTHON BIAS
    if "python" in skills_set and not ("django" in skills_set or "flask" in skills_set):
        role_dict["Python Developer"] = role_dict.get("Python Developer", 0) + 0.1

    # 🔥 DATA SCIENCE (STRICT CHECK)
    data_skills = {"pandas", "numpy", "matplotlib", "seaborn", "scikit-learn"}
    ml_keywords = ["machine learning", "ml", "deep learning"]

    ml_count = sum(1 for k in ml_keywords if k in text)
    data_skill_count = len(data_skills & skills_set)
     
    # 🚨 HARD FILTER FOR DATA SCIENCE
    if ml_count < 2 or data_skill_count < 2:
      role_dict["Data Scientist"] = 0

    if ml_count >= 2 and data_skill_count >= 2:
        role_dict["Data Scientist"] = role_dict.get("Data Scientist", 0) + 0.5
    else:
        # ❌ reduce false positives
        if "Data Scientist" in role_dict:
            role_dict["Data Scientist"] *= 0.3

    # 🔥 NORMALIZE (safe)
    total = sum(role_dict.values()) or 1
    role_dict = {k: v / total for k, v in role_dict.items()}

    return sorted(role_dict.items(), key=lambda x: x[1], reverse=True)[:3]

# -------- SCORE --------
def calculate_score(skills, projects, text):
    score = 0

    score += min(len(skills) * 3, 30)
    score += min(len(projects) * 15, 30)

    if "experience" in text.lower():
        score += 20

    if any(x in text.lower() for x in ["bachelor","master","mca","btech"]):
        score += 10

    if len(text.split()) > 300:
        score += 10

    return min(score, 100)