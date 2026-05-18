# StudyBuddy AI

An AI-powered study assistant for students built with Python (Flask) and Groq's free LLM API. Supports three school modes — Primary (Grades 1–5), Secondary (Grades 6–12), and College — each with age-appropriate explanations.

## Features

- **Ask AI** — Chat with an AI tutor. Ask anything, get clear explanations tailored to your grade level.
- **Quiz Generator** — Enter any topic and get auto-generated multiple-choice questions with answers and explanations.
- **Summarise Notes** — Paste any text (notes, textbook content, PDFs) and get a clean bullet-point, paragraph, or structured summary.
- **Study Planner** — Add your subjects and an exam date and get a day-by-day study schedule.

---

## Prerequisites

- Python 3.10 or higher
- A free [Groq API key](https://console.groq.com) (no credit card needed)

---

## Setup

### 1. Clone or download the project

```
cd ProjectSem4
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate it:

- **Mac / Linux:**
  ```bash
  source .venv/bin/activate
  ```
- **Windows:**
  ```bash
  .venv\Scripts\activate
  ```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `flask` — web framework
- `groq` — Groq Python SDK (free LLM API)
- `python-dotenv` — loads environment variables from `.env`

### 4. Get a free Groq API key

1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up for a free account (no credit card required)
3. Go to **API Keys** → **Create API Key**
4. Copy the key

### 5. Set up your API key

Create a `.env` file in the project root (copy from the example):

```bash
cp .env.example .env
```

Open `.env` and replace the placeholder with your actual key:

```
GROQ_API_KEY=your_actual_key_here
```

---

## Running the App

```bash
python main.py
```

The server starts on `http://127.0.0.1:5000`. Open that URL in your browser.

On first visit you'll be asked to pick your school mode (Primary / Secondary / College) and your grade. This gets saved in your browser so you only need to do it once.

---

## Project Structure

```
ProjectSem4/
├── main.py                  # Flask app — all routes and AI logic
├── requirements.txt         # Python dependencies
├── .env                     # Your API key (not committed to git)
├── .env.example             # Template for the .env file
├── templates/
│   ├── base.html            # Sidebar layout shared by all pages
│   ├── mode_select.html     # Onboarding — pick school mode and grade
│   ├── index.html           # Dashboard / home page
│   ├── ask.html             # Ask AI chat page
│   ├── quiz.html            # Quiz generator page
│   ├── summarize.html       # Note summariser page
│   └── planner.html         # Study planner page
└── static/
    ├── css/style.css        # All styles
    └── js/app.js            # Shared JS utilities (grade, theme, toast, markdown)
```

---

## How It Works

### Backend (`main.py`)

Flask serves all pages and exposes four API endpoints:

| Endpoint | Method | What it does |
|---|---|---|
| `/api/ask` | POST | Answers a question for the given subject and grade |
| `/api/quiz` | POST | Generates MCQs for a topic, count, and difficulty |
| `/api/summarize` | POST | Summarises pasted text in a chosen style |
| `/api/planner` | POST | Builds a day-by-day study schedule |

Every endpoint receives a `grade` field from the frontend. The `get_system_prompt(grade)` function adjusts the AI's language and style:

- **Grades 1–2** — very simple words, emojis, visual counting (🍎🍎🍎), short answers
- **Grades 3–5** — simple language, emojis, step-by-step working, real-life examples
- **Grades 6–8** — clear explanations, proper terms defined, step-by-step solutions
- **Grades 9–10** — detailed, board-exam focused, complete working shown
- **Grades 11–12** — comprehensive, precise, all working and formulas included
- **College** — concise, student-friendly, examples where helpful

The AI model used is `llama-3.1-8b-instant` via the Groq API.

### Frontend

The grade is stored in `localStorage` under the key `sb_grade`. The shared `app.js` reads it on every page load, applies the correct colour theme to the sidebar, and updates the grade chip in the bottom-left corner. Switching mode/grade is done through the `/mode-select` page.

---

## Switching Grade / Mode

Click the chip in the bottom-left of the sidebar (shows your current grade or "College") to go back to the mode selection screen. Changes take effect immediately.

---

## Common Issues

**`Error: GROQ_API_KEY not set` or 401 Unauthorized**
Make sure your `.env` file exists in the project root and contains a valid key. Restart the server after editing `.env`.

**Port 5000 already in use**
Change the port in the last line of `main.py`:
```python
app.run(debug=True, port=5001)
```

**`ModuleNotFoundError: No module named 'flask'`**
Your virtual environment is not activated. Run `source .venv/bin/activate` (Mac/Linux) or `.venv\Scripts\activate` (Windows) first.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| AI / LLM | Groq API — Llama 3.1 8B Instant (free tier) |
| Frontend | HTML, CSS, Vanilla JavaScript |
| Fonts / Icons | Google Fonts (Poppins), Font Awesome 6 |
| Config | python-dotenv |
