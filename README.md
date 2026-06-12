# 📚 Student Study Helper — AI-Powered Personal Study Buddy

> An intelligent, AI-driven Streamlit web application designed to help students in **Classes 6–12** study smarter using the power of Large Language Models.

---

## 🌐 Live Demo

🔗 **Deployed on Streamlit Cloud:** *(https://smart-student-companion-hjoghitk4fwc6edogpppjp.streamlit.app)*

---

## 🎯 Project Overview

**Student Study Helper** is a comprehensive AI study companion built as a final project. It provide instant, class-appropriate explanations, quizzes, flashcards, summaries, resource recommendations, visual concept maps, and personalized study schedules — all in one place.

Students simply enter their class, subject, and topic — and the AI platform does the rest.

---

## ✨ Features

### 🔐 User Login System
- Simple username-based login
- User data stored in a local **SQLite database**
- Personalized experience per student

### 💡 Tab 1 — Explain
- AI generates a simple, class-appropriate explanation (under 150 words)
- **Follow-up chat** — ask additional questions with full conversation history maintained

### 💬 Tab 2 — AI Tutor
- Dedicated **chat interface** with a context-aware AI tutor
- Remembers last 5 conversation turns for continuity
- Adapts responses to the student's class and subject

### 📝 Tab 3 — Interactive Quiz
- Generates **5 MCQ questions** tailored to the topic
- Fully interactive radio button UI
- **Scoring system**: +1 for correct, −0.5 for incorrect answers
- Correct/incorrect feedback shown after submission
- Quiz scores **saved to database** for progress tracking

### 🃏 Tab 4 — Flashcards
- Generates **5 term/definition flashcard pairs**
- Beautifully displayed in styled containers
- **📄 Download as PDF** for offline revision

### 📋 Tab 5 — Summary
- Concise **bullet-point summary** of the topic
- Automatically highlights **3 key formulas** for Maths, Physics, or Chemistry topics
- **📄 Download as PDF**

### 📚 Tab 6 — Resources
- AI suggests curated resources organized in dropdowns:
  - 🎥 **YouTube** search queries
  - 📖 **Books** with author names
  - 🌐 **Websites** (Khan Academy, NCERT, Byju's, etc.)
  - 💡 **Study Tips** specific to the topic

### 🎨 Tab 7 — Visualise
- **Concept Analogy** — a creative real-world analogy to understand the topic
- **Concept Map** — auto-generated **Mermaid.js flowchart** rendered live in the browser
- **📺 Related YouTube Video** — automatically fetched and embedded based on topic

### 📅 Tab 8 — Study Planner
- Input your exam date and chapters to cover
- AI generates a **day-by-day study schedule** in a markdown table
- **📄 Download schedule as PDF**

### 📊 Progress Dashboard (Sidebar)
- View your **last 5 quiz scores** with subject, topic, score, and date
- Persistent tracking across sessions via SQLite

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Framework | Streamlit |
| AI Provider | Groq API (LLaMA 3.1 8B Instant) |
| Database | SQLite (via `db_utils.py`) |
| PDF Export | FPDF2 |
| Visualisation | Mermaid.js (via CDN in HTML component) |
| Video Fetch | `urllib` (YouTube scraper) |
| Deployment | Streamlit Cloud + GitHub Codespaces |

---

## 📁 Project Structure

```
22mc3028_project_task_classes/
│
├── app.py                   # Main application — all UI & AI logic
├── db_utils.py              # SQLite database helper functions
├── study_helper.db          # Local SQLite database file
├── requirements.txt         # Python dependencies
├── .gitignore               # Ignores secrets.toml
├── .devcontainer/
│   └── devcontainer.json    # GitHub Codespaces configuration
└── .streamlit/
    └── secrets.toml         # (Local only) Stores GROQ_API_KEY
```

---

## ⚙️ Setup & Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/repo-Sarthak0816/Smart-student-companion.git
cd Smart-student-companion
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your Groq API Key
Create the file `.streamlit/secrets.toml` and add:
```toml
GROQ_API_KEY = "your_groq_api_key_here"
```
> 🔑 Get your free API key at [console.groq.com](https://console.groq.com)

### 4. Run the app
```bash
streamlit run app.py
```

The app will open at **http://localhost:8501**

---

## ☁️ Run in GitHub Codespaces (No Setup Needed!)

1. Click the green **"Code"** button on this repo
2. Select **"Codespaces"** → **"Create codespace on main"**
3. The environment auto-installs all dependencies and launches the app
4. Add your `GROQ_API_KEY` in `.streamlit/secrets.toml`

---

## 🗄️ Database Schema

```sql
-- Users table
CREATE TABLE users (
    username TEXT PRIMARY KEY
);

-- Quiz scores table
CREATE TABLE quiz_scores (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT,
    subject     TEXT,
    topic       TEXT,
    score       REAL,
    max_score   REAL,
    date_taken  TEXT,
    FOREIGN KEY(username) REFERENCES users(username)
);
```

---

## 📦 Dependencies

```
streamlit
groq
fpdf2
```

---






