import re


ROLE_SKILLS = {

    "Full Stack Developer": [
        "react", "next.js", "node.js", "express", "mongodb",
        "mysql", "postgresql", "javascript", "typescript",
        "docker", "jwt", "graphql", "git", "aws"
    ],

    "Frontend Developer": [
        "html", "css", "javascript", "typescript",
        "react", "next.js", "redux", "bootstrap",
        "tailwind", "graphql"
    ],

    "Backend Developer": [
        "node.js", "express", "mongodb",
        "mysql", "postgresql", "redis",
        "docker", "jwt", "rest api",
        "git", "aws"
    ],

    "Python Developer": [
        "python", "flask", "django",
        "fastapi", "sql", "git",
        "docker", "postgresql"
    ],

    "Java Developer": [
        "java", "spring", "spring boot",
        "hibernate", "jdbc", "mysql",
        "maven", "git"
    ],

    "Data Scientist": [
        "python", "numpy", "pandas",
        "matplotlib", "seaborn",
        "scikit-learn", "tensorflow",
        "pytorch", "opencv",
        "machine learning", "deep learning"
    ],

    "Machine Learning Engineer": [
        "python", "tensorflow", "pytorch",
        "scikit-learn", "opencv",
        "docker", "aws", "mlops"
    ],

    "AI Engineer": [
        "python", "tensorflow", "pytorch",
        "opencv", "transformers",
        "langchain", "llm", "rag",
        "vector database", "docker"
    ],

    "DevOps Engineer": [
        "docker", "kubernetes", "jenkins",
        "aws", "azure", "gcp",
        "terraform", "ansible",
        "linux", "nginx", "git"
    ],

    "Cloud Engineer": [
        "aws", "azure", "gcp",
        "docker", "kubernetes",
        "terraform", "linux"
    ],

    "Android Developer": [
        "java", "kotlin", "android",
        "firebase", "sqlite"
    ],

    "React Native Developer": [
        "react native", "javascript",
        "typescript", "firebase"
    ],

    "Flutter Developer": [
        "flutter", "dart",
        "firebase", "sqlite"
    ],

    "Database Developer": [
        "sql", "mysql", "postgresql",
        "mongodb", "sqlite"
    ],

    "Software Engineer": [
        "java", "python", "c++",
        "javascript", "git",
        "sql", "docker"
    ]
}
def generate_summary(roles, skills):

    top_role = roles[0][0]

    skill_text = ", ".join(skills[:8])

    return (
        f"The candidate is best suited for the role of {top_role}. "
        f"The resume demonstrates knowledge of {skill_text}."
    )
    

def get_top_skills(role, skills):
    required = ROLE_SKILLS.get(role, [])

    current = {skill.upper() for skill in skills}

    top_skills = [
        skill for skill in required
        if skill.upper() in current
    ]

    # Fallback if no role-specific skills are found
    if not top_skills:
        return skills[:5]

    return top_skills[:6]

def get_strengths(skills):

    strengths = []

    if {"react", "node", "express"} & set(skills):
        strengths.append("Full Stack Web Development")

    if "graphql" in skills or "jwt" in skills:
        strengths.append("REST API Development")

    if "docker" in skills:
        strengths.append("Containerization")

    if "git" in skills:
        strengths.append("Version Control")

    if (
        "tensorflow" in skills
        or "pytorch" in skills
        or "opencv" in skills
    ):
        strengths.append("Deep Learning & Computer Vision")

    if "mongodb" in skills or "mysql" in skills:
        strengths.append("Database Design")

    return strengths[:5]
def get_weaknesses(contact,skills):

    weaknesses=[]

    s=set(skills)

    if contact["github"]=="Not Found":
        weaknesses.append("GitHub profile missing")

    if contact["linkedin"]=="Not Found":
        weaknesses.append("LinkedIn profile missing")

    if "docker" not in s:
        weaknesses.append("Docker not mentioned")

    if "aws" not in s:
        weaknesses.append("Cloud platform experience missing")

    return weaknesses

def get_missing_skills(role,skills):

    required=ROLE_SKILLS.get(role,[])

    current=set(skills)

    return sorted(list(set(required)-current))

def calculate_ats_score(score, contact, skills, text):

    ats = score

    # Contact Information
    if not contact["email"]:
        ats -= 5

    if not contact["phone"]:
        ats -= 3

    if not contact["linkedin"]:
        ats -= 2

    # GitHub is optional
    if not contact["github"]:
        ats -= 1

    # Skills
    if len(skills) < 8:
        ats -= 5
    elif len(skills) < 12:
        ats -= 2

    # Resume Length
    words = len(text.split())

    if words < 150:
        ats -= 5
    elif words < 250:
        ats -= 2

    # Important Sections
    lower = text.lower()

    if "technical skills" not in lower and "skills" not in lower:
        ats -= 3

    if "projects" not in lower:
        ats -= 3

    return max(0, min(round(ats), 100))

def recommend_roles(roles):

    result=[]

    stars=[
        "★★★★★",
        "★★★★☆",
        "★★★☆☆"
    ]

    for i,(role,prob) in enumerate(roles):

        result.append({
            "role":role,
            "rating":stars[min(i,2)],
            "confidence":round(prob*100,2)
        })

    return result
def ai_suggestions(contact,skills):

    suggestions=[]

    s=set(skills)

    if not contact["github"]:
        suggestions.append(
            "Add GitHub profile link."
        )

    if not contact["linkedin"]:
        suggestions.append(
            "Add LinkedIn profile link."
        )

    if "aws" not in s:
        suggestions.append(
            "Learn AWS for better backend opportunities."
        )

    if "docker" not in s:
        suggestions.append(
            "Add Docker experience."
        )

    return suggestions
def analyze_resume(
    roles,
    skills,
    contact,
    score,
    text
):

    return {

        "summary":
            generate_summary(
                roles,
                skills,
            ),

        "strengths":
            get_strengths(skills),

        "weaknesses":
            get_weaknesses(contact,skills),

        "missing_skills":
            get_missing_skills(
                roles[0][0],
                skills
            ),

        "ats_score":
            calculate_ats_score(
                score,
                contact,
                skills,
                text
            ),

        "career_recommendation":
            recommend_roles(roles),

        "suggestions":
            ai_suggestions(contact,skills),
            
        "top_skills":
    get_top_skills(
        roles[0][0],
        skills
    ),
    }