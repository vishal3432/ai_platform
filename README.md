# 🤖 AI Task Platform

A full-stack AI-powered task management platform built with Django, Celery, Redis, WebSockets, and React.It upload files, get AI summaries, and watch status updates in real time.

---

## 🏗️ Architecture Overview

```
ai-platform/
├── core/               # Django project settings, URLs, Celery config
├── api/                # Task & File models, REST endpoints, WebSocket consumer
├── services/           # AI logic (ai_service.py) — separated from web layer
├── workers/            # Celery background tasks (file processing)
├── frontend/src/       # React Kanban board (App.jsx)
├── .github/workflows/  # GitHub Actions CI/CD
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django + Django REST Framework |
| Auth | SimpleJWT (token-based) |
| Background Jobs | Celery |
| Message Broker | Redis |
| Real-time | Django Channels (WebSockets) |
| AI | OpenAI GPT-3.5 (or mock mode) |
| Frontend | React (Kanban board) |
| Containers | Docker + Docker Compose |
| CI/CD | GitHub Actions |

---

## 🚀 Quick Start (Windows)

### Prerequisites
- Python 3.11+
- Docker Desktop for Windows (for Redis)
- Node.js 18+ (for frontend)

### Step 1 — Clone & Virtual Environment

```cmd
git clone <your-repo-url>
cd ai-platform

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2 — Environment Variables

```cmd
copy .env.example .env
```

Open `.env` and fill in your values:
```
SECRET_KEY=any-random-long-string
DEBUG=True
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-...   ← leave blank for mock mode
```

### Step 3 — Start Redis (via Docker)

```cmd
docker run -d -p 6379:6379 redis
```

### Step 4 — Run Migrations & Create Admin User

```cmd
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### Step 5 — Start the Django Server

```cmd
python manage.py runserver
```

### Step 6 — Start the Celery Worker (new terminal)

```cmd
venv\Scripts\activate
celery -A core worker --loglevel=info --pool=solo
```
> **Windows note:** Use `--pool=solo` on Windows since multiprocessing has limitations.

### Step 7 — Open the App

- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/
- Get a JWT token: `POST http://localhost:8000/api/token/`

---

## 🐳 Run Everything with Docker

If you prefer Docker for everything (recommended for sharing):

```cmd
docker-compose up --build
```

This launches 4 containers: Django web, Celery worker, Redis, PostgreSQL.

---

## 📡 API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/api/token/` | Login → get JWT token |
| POST | `/api/token/refresh/` | Refresh JWT token |
| GET | `/api/tasks/` | List your tasks |
| POST | `/api/tasks/` | Create a task |
| GET | `/api/tasks/<id>/` | Get task details |
| PATCH | `/api/tasks/<id>/` | Update task (e.g. change status) |
| DELETE | `/api/tasks/<id>/` | Delete task |
| POST | `/api/tasks/<id>/upload/` | Upload a file → triggers background AI processing |
| POST | `/api/summarize-text/` | Summarize raw text with AI |

### Example: Login

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"admin\", \"password\": \"your-password\"}"
```

### Example: Create a Task

```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"My First Task\", \"status\": \"todo\"}"
```

### Example: Summarize Text

```bash
curl -X POST http://localhost:8000/api/summarize-text/ \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Django is a high-level Python web framework...\"}"
```

---

## 🔌 WebSocket (Real-time Updates)

Connect to track a task's status live:

```
ws://localhost:8000/ws/tasks/<task_id>/
```

When a file finishes processing, you'll receive:
```json
{
  "type": "task_update",
  "task_id": "5",
  "message": "File processed! Summary: ..."
}
```

---

## 🧪 Running Tests

```cmd
python manage.py test
```

---

## 🔄 CI/CD (GitHub Actions)

Every `git push` to `main`:
1. Runs Django unit tests
2. Builds the Docker image

To enable Render deployment, uncomment the deploy block in `.github/workflows/deploy.yml` and add `RENDER_DEPLOY_HOOK_URL` to your GitHub Secrets.

---

## 💡 Key Design Decisions

- **Separation of Concerns** — AI logic lives in `services/ai_service.py`, not in views
- **Async file processing** — Files are processed in background via Celery so uploads never block the API
- **Streaming file reads** — Large files are read line-by-line to avoid memory issues
- **JWT auth** — Stateless, works across frontend + API seamlessly
- **Mock AI mode** — Works without an OpenAI key (great for dev/testing)

---
