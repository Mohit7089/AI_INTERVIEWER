import pickle
from role_data import *
import pdfplumber
import fitz
import re


# -------- LOAD MODELS --------
model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))
le = pickle.load(open("label_encoder.pkl", "rb"))

# model_lines = pickle.load(open("model_lines.pkl", "rb"))
# vectorizer_lines = pickle.load(open("vectorizer_lines.pkl", "rb"))

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

    print("TEXT LENGTH:", len(text))

    file.seek(0)

    return text
def extract_links(file):
    file.seek(0)

    pdf_bytes = file.read()

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    links = []

    for page in doc:
        for link in page.get_links():
            uri = link.get("uri")
            if uri:
                links.append(uri.strip())

    doc.close()

    file.seek(0)

    return links


def extract_contact_info(text, file):

    links = extract_links(file)

    email = ""
    github = ""
    linkedin = ""

    # -------- Extract from hyperlinks --------
    for url in links:

        url = url.strip()

        if url.lower().startswith("mailto:"):
            email = url.replace("mailto:", "").split("?")[0].strip()

        elif "github.com" in url.lower():
            github = url

        elif "linkedin.com" in url.lower():
            linkedin = url

    # -------- Email (fallback) --------
    if not email:
        match = re.search(
            r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',
            text
        )
        if match:
            email = match.group(0)

    # -------- Phone --------
    phone = re.search(
        r'(?:\+91[-\s]?)?[6-9]\d{9}',
        text
    )

    # -------- GitHub (fallback) --------
    if not github:
        match = re.search(
            r'((?:https?://)?(?:www\.)?github\.com/[^\s]+)',
            text,
            re.I
        )
        if match:
            github = match.group(1)

    # -------- LinkedIn (fallback) --------
    if not linkedin:
        match = re.search(
            r'((?:https?://)?(?:www\.)?linkedin\.com/[^\s]+)',
            text,
            re.I
        )
        if match:
            linkedin = match.group(1)

    return {
        "email": email,
        "phone": phone.group(0) if phone else "",
        "github": github,
        "linkedin": linkedin
    }
# -------- SKILLS --------
def extract_skills(text):
    skills_db = [

    # Programming Languages
    "python", "java", "c", "c++", "c#",
    "javascript", "typescript",

    # Frontend
    "html", "css",
    "react", "next.js", "redux",
    "angular", "vue",
    "bootstrap", "tailwind",

    # Backend
    "node", 
    "express", 
    "spring", "spring boot",
    "django", "flask", "fastapi",

    # Databases
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "sqlite",

    # APIs
    "rest api",
    "graphql",
    "jwt",

    # DevOps & Cloud
    "git",
    "github",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "redis",
    "nginx",
    "jenkins",

    # Tools
    "postman",
    "vscode",
    "eclipse",
    "intellij",

    # Java Technologies
    "jdbc",
    "hibernate",
    "swing",
    "maven",

    # Python / Data Science
    "numpy",
    "pandas",
    "matplotlib",
    "seaborn",
    "scikit-learn",
    "tensorflow",
    "keras",
    "pytorch",
    "opencv",
    "machine learning",
    "deep learning",

    # Mobile
    "android",
    "flutter",
    "react native"
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

    total = sum(role_dict.values()) or 1
    role_dict = {k: v / total for k, v in role_dict.items()}

    return sorted(role_dict.items(), key=lambda x: x[1], reverse=True)[:3]

# -------- SCORE --------
import re

from role_data import (
    EDUCATION,
    EXPERIENCE,
    SECTIONS,
    ROLE_SKILLS
)


def calculate_score(skills, text, contact, predicted_role):

    text = text.lower()

    skills = {s.lower().strip() for s in skills}

    score = 0

    # --------------------------
    # Contact (10)
    # --------------------------

    if contact.get("email"):
        score += 3

    if contact.get("phone"):
        score += 2

    if contact.get("linkedin"):
        score += 3

    if contact.get("github"):
        score += 2


    # --------------------------
    # Education (10)
    # --------------------------

    if any(word in text for word in EDUCATION):
        score += 10


    # --------------------------
    # Experience (15)
    # --------------------------

    if any(word in text for word in EXPERIENCE):
        score += 15


    # --------------------------
    # Projects (15)
    # --------------------------

    project_count = text.count("project")

    if project_count >= 2:
        score += 10

    if project_count >= 2:
        score += 7


    # --------------------------
    # Skills (30)
    # --------------------------

    role = ROLE_SKILLS.get(predicted_role)

    if role:

        required = role["required"]

        advanced = role["advanced"]

        required_matches = len(required & skills)

        advanced_matches = len(advanced & skills)

        score += min(required_matches * 2, 10)

        score += min(advanced_matches * 3, 20)

    else:

        score += min(len(skills), 10)


    # --------------------------
    # Quantified Achievements (10)
    # --------------------------

    if re.search(r"\d+%", text):
        score += 5

    if re.search(r"\d+\+?", text):
        score += 5


    # --------------------------
    # Resume Length (5)
    # --------------------------

    words = len(text.split())

    if 250 <= words <= 700:
        score += 5

    elif 150 <= words < 250:
        score += 3


    # --------------------------
    # ATS Sections (5)
    # --------------------------

    found = sum(section in text for section in SECTIONS)

    score += min(found, 3)

    return min(round(score), 100)