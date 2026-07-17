# AI Interviewer - Project Setup

Follow these steps to run the project on a new system.

## 1. Clone the Repository

```bash
git clone https://github.com/Mohit7089/AI_INTERVIEWER.git
cd AI_INTERVIEWER
```

---

## 2. Install Root Dependencies

```bash
npm install
```

---

## 3. Install Frontend Dependencies

```bash
cd client
npm install
```

---

## 4. Install Backend Dependencies

```bash
cd ../server
npm install
```

---

## 5. Setup Resume Analyzer

```bash
cd ../resume-analyzer-api

python3 -m venv venv
source venv/bin/activate      # macOS/Linux
# OR
venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

---

## 6. Environment Variables

### Client

Create a file named:

```
client/.env
```

Add:

```env
VITE_FIREBASE_API_KEY=YOUR_FIREBASE_API_KEY
VITE_FIREBASE_AUTH_DOMAIN=YOUR_AUTH_DOMAIN
VITE_FIREBASE_PROJECT_ID=YOUR_PROJECT_ID
VITE_FIREBASE_STORAGE_BUCKET=YOUR_STORAGE_BUCKET
VITE_FIREBASE_MESSAGING_SENDER_ID=YOUR_SENDER_ID
VITE_FIREBASE_APP_ID=YOUR_APP_ID
VITE_FIREBASE_MEASUREMENT_ID=YOUR_MEASUREMENT_ID
```

---

### Server

Create:

```
server/.env
```

Example:

```env
PORT=8000

MONGODB_URI=YOUR_MONGODB_URI

JWT_SECRET=YOUR_JWT_SECRET

OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY

CLIENT_URL=http://localhost:5173
```

---

## 7. Start the Project

From the project root:

```bash
npm run dev
```

This starts:

- React Frontend
- Node.js Backend
- Flask Resume Analyzer

---

## Common Issues

### Port 5000 already in use

```bash
kill -9 $(lsof -ti:5000)
```

### Port 5173 already in use

```bash
kill -9 $(lsof -ti:5173)
```

### Python packages missing

```bash
cd resume-analyzer-api

source venv/bin/activate

pip install -r requirements.txt
```

### Node modules missing

```bash
npm install
```

inside the required folder (`client`, `server`, or project root).

---

## Project Structure

```
AI_INTERVIEWER/
│
├── client/
├── server/
├── resume-analyzer-api/
├── package.json
└── SETUP.md
```