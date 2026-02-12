# Todo App with AI Chatbot

A full-stack todo application with an AI-powered chatbot assistant. Users can manage tasks through a traditional UI or by chatting with an AI agent that understands natural language commands.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, React 18, Tailwind CSS, TypeScript |
| Backend | FastAPI, SQLModel, Python 3.11 |
| Database | PostgreSQL (Neon.tech) / SQLite (local dev) |
| AI | OpenRouter API (Qwen 2.5 72B) with tool calling |
| Auth | JWT (python-jose + bcrypt) |
| Deployment | Vercel (frontend) + Hugging Face Spaces (backend) |

## Features

- User registration and login with JWT authentication
- Create, read, update, and delete tasks
- AI chatbot that can add, list, complete, delete, and update tasks via natural language
- Conversation history persistence
- Rate limiting on API endpoints
- Per-user task isolation (users can only see their own tasks)

---

## Project Structure

```
phase_3/
├── backend/                  # FastAPI backend
│   ├── main.py               # App entrypoint, CORS, startup
│   ├── auth.py               # JWT token creation & verification
│   ├── auth_endpoints.py     # /api/auth/register, /login, /logout
│   ├── task_endpoints.py     # CRUD /api/{user_id}/tasks
│   ├── chat_endpoints.py     # POST /api/{user_id}/chat
│   ├── agent.py              # AI agent with tool calling loop
│   ├── mcp_tools.py          # Tool definitions for the AI agent
│   ├── models.py             # SQLModel models (User, Task, Conversation, Message)
│   ├── database.py           # Database engine setup (SQLite / PostgreSQL)
│   ├── logging_config.py     # Structured logging
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile            # Docker config for Hugging Face Spaces
│   └── .env.example          # Environment variable template
├── frontend/                 # Next.js frontend
│   ├── app/                  # Next.js app router pages
│   │   ├── layout.tsx        # Root layout
│   │   ├── login/page.tsx    # Login page
│   │   ├── signup/page.tsx   # Signup page
│   │   └── dashboard/page.tsx # Main dashboard
│   ├── components/           # React components
│   │   ├── TodoList.tsx      # Task list display
│   │   ├── TodoItem.tsx      # Individual task item
│   │   ├── TodoForm.tsx      # Task creation form
│   │   └── ChatbotWidget.tsx # AI chatbot widget
│   ├── contexts/AuthContext.tsx # Auth state management
│   ├── lib/api.js            # API client with JWT handling
│   ├── .env.production       # Production environment variables
│   └── package.json          # Node dependencies
└── README.md
```

---

## Local Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm

### Step 1: Clone the Repository

```bash
git clone https://github.com/sobiamehak/hack2-phase3.git
cd hack2-phase3
```

### Step 2: Set Up the Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from template
cp .env.example .env
```

Edit `backend/.env` and fill in your values:

```env
OPEN_ROUTER_API_KEY=your-openrouter-api-key
DATABASE_URL=sqlite:///./chatbot.db
BETTER_AUTH_SECRET=your-secret-key
FRONTEND_URL=http://localhost:3000
```

Start the backend:

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. Tables are created automatically on startup.

### Step 3: Set Up the Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The frontend will be available at `http://localhost:3000`.

### Step 4: Test the App

1. Open `http://localhost:3000` in your browser
2. Click **Sign Up** to create an account
3. Log in with your credentials
4. Add tasks using the form or the AI chatbot widget
5. Try chatting: "Add a task to buy groceries" or "Show my tasks"

---

## Production Deployment

### Step 1: Set Up Neon.tech PostgreSQL Database

1. Go to [neon.tech](https://neon.tech) and create a free account
2. Create a new project
3. Copy the connection string — it looks like:
   ```
   postgresql://user:password@ep-xxx.region.neon.tech/dbname?sslmode=require
   ```
4. Save this — you'll use it as `DATABASE_URL` in the backend

### Step 2: Deploy Backend to Hugging Face Spaces

1. Go to [huggingface.co/spaces](https://huggingface.co/spaces) and create a new Space
   - **SDK:** Docker
   - **Visibility:** Public
2. Clone the Space repo locally:
   ```bash
   git clone https://huggingface.co/spaces/<your-username>/<space-name>
   ```
3. Copy the backend files into the Space repo:
   ```bash
   cp -r backend/* <space-repo>/
   ```
4. Add secrets in the Space settings (Settings > Variables and secrets):
   | Secret | Value |
   |--------|-------|
   | `DATABASE_URL` | Your Neon PostgreSQL connection string |
   | `OPEN_ROUTER_API_KEY` | Your OpenRouter API key |
   | `BETTER_AUTH_SECRET` | A strong random secret for JWT signing |
   | `FRONTEND_URL` | Your Vercel URL (set after Step 3) |
5. Push to the Space repo:
   ```bash
   cd <space-repo>
   git add .
   git commit -m "Deploy backend"
   git push
   ```
6. Wait for the Space to build. Test with:
   ```bash
   curl https://<your-username>-<space-name>.hf.space/health
   # Expected: {"status":"healthy"}
   ```

### Step 3: Deploy Frontend to Vercel

1. Push this repo to GitHub (if not already)
2. Go to [vercel.com](https://vercel.com) and import the GitHub repository
3. Set the **Root Directory** to `frontend/`
4. Add environment variable:
   | Variable | Value |
   |----------|-------|
   | `NEXT_PUBLIC_API_BASE_URL` | `https://<your-username>-<space-name>.hf.space` |
5. Click **Deploy**

### Step 4: Update CORS on Backend

After getting your Vercel URL (e.g., `https://your-app.vercel.app`):

1. Go to your Hugging Face Space settings
2. Set the `FRONTEND_URL` secret to your Vercel URL
3. The Space will automatically rebuild

### Step 5: Verify Everything Works

| Check | How |
|-------|-----|
| Backend health | `curl https://<space>.hf.space/health` |
| Frontend loads | Open your Vercel URL in a browser |
| Registration | Create a new account on the signup page |
| Login | Log in with your credentials |
| Add task (UI) | Use the task form on the dashboard |
| Add task (AI) | Use the chatbot: "Add a task to buy milk" |
| Complete task | Click the checkbox on a task |
| Delete task | Click the delete button on a task |

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register` | No | Register a new user |
| POST | `/api/auth/login` | No | Login and get JWT token |
| POST | `/api/auth/logout` | No | Logout |
| GET | `/api/{user_id}/tasks` | Yes | List user's tasks |
| POST | `/api/{user_id}/tasks` | Yes | Create a task |
| PUT | `/api/{user_id}/tasks/{task_id}` | Yes | Update a task |
| DELETE | `/api/{user_id}/tasks/{task_id}` | Yes | Delete a task |
| POST | `/api/{user_id}/chat` | Yes | Send message to AI chatbot |
| GET | `/health` | No | Health check |

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Database connection string |
| `OPEN_ROUTER_API_KEY` | Yes | OpenRouter API key for AI |
| `BETTER_AUTH_SECRET` | Yes | Secret key for JWT signing |
| `FRONTEND_URL` | Yes | Frontend URL for CORS |
| `OPENAI_BASE_URL` | No | AI API base URL (default: OpenRouter) |
| `OPENAI_MODEL` | No | AI model to use (default: qwen/qwen-2.5-72b-instruct) |

### Frontend (`frontend/.env.production`)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_BASE_URL` | Yes | Backend API URL |
