import json
import os
import re

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

app = Flask(__name__)


def chat(prompt, system=None, max_tokens=2048):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(model=MODEL, messages=messages, max_tokens=max_tokens)
    return response.choices[0].message.content


def get_system_prompt(grade, task="general"):
    g = int(grade) if str(grade).isdigit() else 0

    if g in [1, 2]:
        return (
            "You are a super friendly and fun teacher helping a little kid in Grade "
            f"{g} (age 6-7). RULES: "
            "1) Use VERY simple words — no hard vocabulary at all. "
            "2) Keep answers SHORT — maximum 6 sentences. "
            "3) Use LOTS of emojis! Make it colorful and fun. "
            "4) For any math or counting, ALWAYS show it visually with emoji objects: "
            "   e.g. '3 apples = 🍎🍎🍎', '5 stars = ⭐⭐⭐⭐⭐'. "
            "5) Use tiny fun stories or examples with animals, food, toys. "
            "6) Always be encouraging — end every answer with a cheer like '🌟 You did it!' or '🎉 Amazing job!'"
        )
    elif g in [3, 4, 5]:
        return (
            "You are a friendly teacher helping a primary school student in Grade "
            f"{g} (age 8-11). RULES: "
            "1) Use simple, clear language a child can understand. "
            "2) Use emojis to make explanations visual and engaging. "
            "3) For math: show step-by-step working with emoji visuals for counting. "
            "4) Use relatable real-life examples (sports, food, school, games). "
            "5) Bold important words using **word**. "
            "6) Be encouraging and positive at the end! 😊"
        )
    elif g in [6, 7, 8]:
        return (
            f"You are a helpful tutor for a middle school student in Grade {g}. "
            "Explain concepts clearly with simple examples. "
            "Use proper subject terminology but define new terms when you introduce them. "
            "Show step-by-step solutions for math and science problems. "
            "Use **bold** for key terms. Be friendly and concise."
        )
    elif g in [9, 10]:
        return (
            f"You are a tutor for a high school student in Grade {g}. "
            "Give clear, detailed explanations using proper terminology. "
            "Show complete step-by-step solutions for problems. "
            "Focus on board exam-relevant concepts. "
            "Use **bold** for key terms and formulas."
        )
    elif g in [11, 12]:
        return (
            f"You are a tutor for a senior high school student in Grade {g}. "
            "Give detailed, exam-focused explanations with precise notation. "
            "Cover concepts thoroughly and show all working for problems. "
            "Use **bold** for key terms and formulas. Be precise and comprehensive."
        )
    else:
        return (
            "You are StudyBuddy AI, a helpful and friendly tutor for college students. "
            "Answer clearly and concisely. Use examples where helpful. "
            "Use **bold** for key terms. Keep it student-friendly."
        )


def get_quiz_system(grade):
    g = int(grade) if str(grade).isdigit() else 0
    if g in [1, 2]:
        return (
            "You generate very simple quiz questions for young children (Grade 1-2). "
            "Questions must be about basic counting, colors, shapes, animals, or simple addition. "
            "Use emojis in questions and options. Keep language VERY simple. "
            "Respond with valid JSON only."
        )
    elif g in [3, 4, 5]:
        return (
            "You generate simple, fun quiz questions for primary school students (Grade 3-5). "
            "Questions on basic math, science, English, GK. Keep language simple and friendly. "
            "Use emojis to make options more visual where relevant. "
            "Respond with valid JSON only."
        )
    else:
        return "You are a quiz generator for students. Respond with valid JSON only, no other text."


def extract_json(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    text = re.sub(r"```(?:json)?\s*", "", text)
    text = re.sub(r"```\s*", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start, end = text.find("{"), text.rfind("}") + 1
    if start >= 0 and end > start:
        return json.loads(text[start:end])
    raise ValueError("No valid JSON in response")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/mode-select")
def mode_select():
    return render_template("mode_select.html")


@app.route("/ask")
def ask():
    return render_template("ask.html")


@app.route("/api/ask", methods=["POST"])
def api_ask():
    data = request.get_json()
    question = data.get("question", "").strip()
    subject = data.get("subject", "General")
    grade = data.get("grade", "college")
    if not question:
        return jsonify({"error": "Question is required"}), 400

    answer = chat(
        prompt=f"Subject: {subject}\n\nQuestion: {question}",
        system=get_system_prompt(grade),
        max_tokens=1024,
    )
    return jsonify({"answer": answer})


@app.route("/quiz")
def quiz():
    return render_template("quiz.html")


@app.route("/api/quiz", methods=["POST"])
def api_quiz():
    data = request.get_json()
    topic = data.get("topic", "").strip()
    num_questions = min(int(data.get("num_questions", 5)), 10)
    difficulty = data.get("difficulty", "Medium")
    grade = data.get("grade", "college")
    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    g = int(grade) if str(grade).isdigit() else 0
    diff_note = f"at {difficulty} difficulty" if g >= 6 else "very simple and easy"

    prompt = (
        f'Generate exactly {num_questions} multiple choice questions about "{topic}" '
        f"{diff_note} for a Grade {grade} student.\n"
        f"Return ONLY valid JSON, no markdown:\n"
        f'{{"topic":"{topic}","questions":['
        f'{{"question":"...","options":["A) ...","B) ...","C) ...","D) ..."],'
        f'"answer":"A","explanation":"..."}}]}}'
    )
    result = chat(prompt, system=get_quiz_system(grade))
    return jsonify(extract_json(result))


@app.route("/summarize")
def summarize():
    return render_template("summarize.html")


@app.route("/api/summarize", methods=["POST"])
def api_summarize():
    data = request.get_json()
    text = data.get("text", "").strip()
    style = data.get("style", "bullet")
    grade = data.get("grade", "college")
    if not text:
        return jsonify({"error": "Text is required"}), 400

    g = int(grade) if str(grade).isdigit() else 0
    if g <= 5:
        style_instruction = "Summarize in very simple words a child can understand. Use bullet points starting with '•' and add a fun emoji to each point. Keep it short!"
    else:
        style_map = {
            "bullet": "Summarize as clear bullet points. Start each with '•'. One key idea per bullet.",
            "paragraph": "Write a concise 2-3 paragraph summary.",
            "structured": "Create a structured summary with a heading, key points, and important details.",
        }
        style_instruction = style_map.get(style, style_map["bullet"])

    result = chat(
        prompt=f"{style_instruction}\n\nText:\n{text}",
        system=get_system_prompt(grade, task="summary"),
        max_tokens=1024,
    )
    return jsonify({"summary": result})


@app.route("/planner")
def planner():
    return render_template("planner.html")


@app.route("/api/planner", methods=["POST"])
def api_planner():
    data = request.get_json()
    subjects = data.get("subjects", [])
    exam_date = data.get("exam_date", "")
    hours_per_day = int(data.get("hours_per_day", 4))
    grade = data.get("grade", "college")
    if not subjects:
        return jsonify({"error": "Add at least one subject"}), 400

    g = int(grade) if str(grade).isdigit() else 0
    if g <= 5:
        session_note = "Keep each session SHORT — 20-30 minutes. Include fun break activities."
        hours_per_day = min(hours_per_day, 3)
    elif g <= 10:
        session_note = "Sessions of 45-60 minutes with breaks."
    else:
        session_note = "Sessions of 1-2 hours each."

    prompt = (
        f"Create a study schedule for a Grade {grade} student.\n"
        f"Subjects: {', '.join(subjects)}\n"
        f"Target date: {exam_date}\n"
        f"Study hours per day: {hours_per_day}\n"
        f"Note: {session_note}\n\n"
        f"Return ONLY valid JSON (no markdown):\n"
        f'{{"schedule":[{{"day":"Day 1","date_label":"Monday - May 13",'
        f'"sessions":[{{"subject":"...","duration":"30 minutes","topics":"...","priority":"High"}}]}}],'
        f'"tips":["tip1","tip2","tip3"]}}\n'
        f"Generate 5-7 days. Priority must be High, Medium, or Low."
    )
    result = chat(prompt, system="You are a study planner. Respond with valid JSON only.")
    return jsonify(extract_json(result))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
