# AI Interview Simulator

A full-stack mock-interview platform: candidates upload their resume, get AI-generated
interview questions tailored to their target role, answer by voice or text, receive
instant AI-scored feedback on technical + communication quality, and download a PDF
feedback report at the end.

## Features
- 🔐 JWT authentication (register/login)
- 📄 Resume upload (PDF/DOCX/TXT) with text extraction
- 🤖 AI-generated interview questions (OpenAI) tailored to resume + target role
- 🎤 Voice input via the browser's Web Speech API (falls back to typing)
- 📊 AI evaluation of each answer — separate technical & communication scores (0–10) + written feedback
- 🧾 Auto-generated PDF feedback report (ReportLab) with per-question breakdown

## Tech Stack
- **Frontend:** React (Vite), React Router, Axios
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL (SQLAlchemy ORM)
- **AI:** OpenAI API (chat completions)
- **Auth:** JWT (python-jose + passlib/bcrypt)

## Project Structure
```
ai-interview-simulator/
  backend/
    app/
      main.py          # FastAPI app + CORS + router registration
      config.py         # env-based settings
      database.py        # SQLAlchemy engine/session
      models.py          # User, Resume, InterviewSession, InterviewQuestion
      schemas.py          # Pydantic request/response models
      auth.py            # password hashing + JWT
      routers/
        auth.py            # /api/auth/register, /login, /me
        resume.py           # /api/resume/upload, list
        interview.py         # /api/interview/start, /answer, /complete, /report
      services/
        openai_service.py     # question generation + answer evaluation prompts
        resume_parser.py       # PDF/DOCX/TXT -> plain text
        pdf_service.py          # feedback report PDF generation
    requirements.txt
    .env.example
  frontend/
    src/
      pages/           # Login, Register, ResumeUpload, Interview, Report
      components/       # VoiceRecorder, ScoreCard
      api.js            # axios client with JWT interceptor
    package.json
    vite.config.js
```

## Setup

### 1. Database
Create a PostgreSQL database:
```bash
createdb interview_simulator
```

### 2. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # then fill in DATABASE_URL, JWT_SECRET_KEY, OPENAI_API_KEY
uvicorn app.main:app --reload --port 8000
```
Tables are auto-created on startup for convenience. For production, replace
`Base.metadata.create_all` in `main.py` with proper Alembic migrations.

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```
Visit http://localhost:5173 — the Vite dev server proxies `/api` calls to
`http://localhost:8000` (see `vite.config.js`).

## How it works
1. **Register/Login** — JWT issued on login, stored in `localStorage`, attached to every API call.
2. **Upload resume** — file is parsed to plain text server-side (`pypdf`/`python-docx`) and stored alongside the candidate's target role.
3. **Start interview** — backend sends the resume text + target role to OpenAI, asking for a JSON array of technical/behavioral/communication questions.
4. **Answer** — candidate speaks (Web Speech API transcribes live) or types; each answer is sent to `/api/interview/answer`, which asks OpenAI to score technical accuracy and communication quality (0–10 each) with written feedback.
5. **Complete** — once all questions are answered, `/api/interview/{id}/complete` averages the scores and generates a PDF report (ReportLab) with a full question-by-question breakdown.
6. **Download** — candidate downloads the PDF from the results page.

## Notes & Next Steps
- Voice input uses the browser's built-in `SpeechRecognition` (Chrome/Edge support it natively; Firefox does not — the UI falls back to manual typing).
- Swap `Base.metadata.create_all` for Alembic migrations before deploying.
- Consider rate-limiting `/interview/start` and `/interview/answer` since each call hits the OpenAI API.
- Add refresh tokens / token revocation for production-grade auth.
- The `OPENAI_MODEL` env var defaults to `gpt-4o-mini` — swap for any chat-completion-capable model.
