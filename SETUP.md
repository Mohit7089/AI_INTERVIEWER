# AI Interviewer - Setup Guide

This guide explains how to set up and run the AI Interviewer project on your local machine.

---

## Prerequisites

Make sure the following software is installed:

- Node.js (v18 or later)
- npm
- Python 3.10 or later
- Git

---

## 1. Clone the Repository

```bash
git clone https://github.com/Mohit7089/AI_INTERVIEWER.git
cd AI_INTERVIEWER
```

---

## 2. Install Dependencies

### Root

```bash
npm install
```

### Frontend

```bash
cd client
npm install
```

### Backend

```bash
cd ../server
npm install
```

### Resume Analyzer (Flask API)

```bash
cd ../resume-analyzer-api

python -m venv venv
```

Activate the virtual environment:

**Windows**
```bash
venv\Scripts\activate
```

**macOS / Linux**
```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### AI Proctoring

The AI Proctoring module provides interview monitoring and proctoring functionality.

```bash
cd ../ai_proctoring

python -m venv .venv
```

Activate the virtual environment:

**Windows**
```bash
.venv\Scripts\activate
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Audio Confidence

The Audio Confidence module analyzes interview audio and uses a trained machine learning model to perform confidence classification.

```bash
cd ../Audio_Confidence

python -m venv venv
```

Activate the virtual environment:

**Windows**
```bash
venv\Scripts\activate
```

**macOS / Linux**
```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

The following pretrained model files must be present in the `Audio_Confidence` directory:

- `model.pkl`
- `scaler.pkl`
- `label_encoder.pkl`

These files are required for loading the trained model and performing predictions.

---

## 3. Frontend Environment

The required frontend environment configuration (`client/.env`) is already included in the repository.

No additional Firebase setup is required.

---

## 4. Backend Environment Variables

Create a file named:

```text
server/.env
```

Add the following variables:

```env
PORT=8000

MONGODB_URI=YOUR_MONGODB_CONNECTION_STRING

JWT_SECRET=YOUR_JWT_SECRET

OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY

CLIENT_URL=http://localhost:5173
```

Replace the placeholder values with your own credentials.

---

## 5. AI Proctoring Environment

The AI Proctoring module includes an `.env.example` file.

Create a `.env` file inside the `ai_proctoring` directory using the example configuration:

```bash
cd ai_proctoring
```

Copy `.env.example` to `.env` and configure the required environment variables.

---

## 6. Run the Project

Return to the project root:

```bash
cd ..
```

Start the project using:

```bash
npm run dev
```

This command starts:

- React Frontend
- Express Backend
- Flask Resume Analyzer

AI Proctoring and Audio Confidence should be configured and started according to their respective module README instructions.

---

## Project Structure

```text
AI_INTERVIEWER/
│
├── client/
├── server/
├── resume-analyzer-api/
├── ai_proctoring/
├── Audio_Confidence/
├── package.json
├── SETUP.md
└── .gitignore
```

---

## Common Issues

### Python Packages Missing

Navigate to the required Python module, activate its virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

### Port 5000 Already in Use

**macOS / Linux**

```bash
kill -9 $(lsof -ti:5000)
```

**Windows**

```powershell
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Port 5173 Already in Use

**macOS / Linux**

```bash
kill -9 $(lsof -ti:5173)
```

**Windows**

```powershell
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

### Node Modules Missing

Run the following command inside the required folder:

```bash
npm install
```

### Python Virtual Environment Issues

If the virtual environment is missing or corrupted, recreate it:

```bash
python -m venv venv
```

Activate it and reinstall the dependencies:

```bash
pip install -r requirements.txt
```

---

## Notes

- Do not commit `server/.env` or other `.env` files containing sensitive credentials.
- The frontend environment (`client/.env`) is already included in this repository.
- If you change backend credentials, update `server/.env` accordingly before running the project.
- Each Python module maintains its own virtual environment.
- Do not commit `venv/`, `.venv/`, `node_modules/`, or `__pycache__/` directories.
- Ensure all required pretrained model files are available before running the Audio Confidence module.
- Install Python dependencies separately for each module using its respective `requirements.txt`.
- Refer to the individual module README files for additional configuration and service-specific startup instructions.