import json
import PyPDF2
import re
import os
from openai import OpenAI

# Initialize OpenAI client using Streamlit Secrets
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Set it in Streamlit Secrets.")

client = OpenAI(api_key=api_key)

# -----------------------------
# PDF extraction
# -----------------------------
def extract_text_from_pdf(uploaded_file):
    """
    Safely extracts text from an uploaded PDF file.
    Returns a string or a warning message if extraction fails.
    """
    text = ""
    if uploaded_file is None:
        return text

    try:
        uploaded_file.seek(0)  # Reset pointer to start
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        text = ""
        print(f"Error reading PDF: {e}")

    if not text:
        text = "⚠️ No text could be extracted from this PDF. Please try another file."
    return text

# -----------------------------
# Explanation with error handling
# -----------------------------
def get_explanation(topic, level, chat_history):
    """
    Returns an explanation for a topic at the given level.
    Handles API errors gracefully.
    """
    messages = [{"role": "system", "content": "You are a helpful tutor."}]
    messages.extend(chat_history)
    messages.append({"role": "user", "content": f"Explain {topic} at {level} level."})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        return response.choices[0].message.content
    except Exception:
        return "⚠️ The AI service is busy or unavailable. Please try again in a few seconds."

# -----------------------------
# Quiz generation with error handling
# -----------------------------
def generate_mcq_quiz(text, num_questions=10):
    """
    Generates multiple-choice questions from input text.
    Returns a list of questions or None if an error occurs.
    """
    prompt = f"""
    Create {num_questions} multiple-choice questions based on this study material:

    {text}

    Format output ONLY as a JSON list like:
    [
      {{
        "question": "What is ...?",
        "options": ["A", "B", "C", "D"],
        "answer": "B"
      }}
    ]
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        raw_output = response.choices[0].message.content

        match = re.search(r"\[.*\]", raw_output, re.DOTALL)
        if match:
            quiz_json = match.group(0)
            quiz = json.loads(quiz_json)

            # Convert letter answers (A/B/C/D) to actual option text
            for q in quiz:
                ans = q.get("answer")
                if ans in ["A", "B", "C", "D"]:
                    idx = ord(ans) - 65
                    if 0 <= idx < len(q["options"]):
                        q["answer"] = q["options"][idx]
            return quiz
        else:
            return []
    except Exception:
        return None
