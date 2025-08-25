import streamlit as st
from ai_utils import get_explanation, generate_mcq_quiz, extract_text_from_pdf

st.set_page_config(page_title="AI Study Partner", layout="wide")

# -----------------------------
# Sidebar Navigation
# -----------------------------
st.sidebar.title("📚 AI Study Partner")
page = st.sidebar.radio("Go to", ["🏠 Home", "📖 Explanation", "📝 Quiz"])

# -----------------------------
# 🏠 Home
# -----------------------------
if page == "🏠 Home":
    st.title("🤖 Welcome to AI Study Partner")
    st.markdown("""
    Learn smarter with AI:

    - 📖 Explanations at multiple levels + follow-up questions  
    - 📝 Quizzes from PDFs or text  
    - 🗂 Keep track of your progress  
    """)

# -----------------------------
# 📖 Explanation
# -----------------------------
elif page == "📖 Explanation":
    st.title("📖 AI Explanation Assistant")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    topic = st.text_input("Enter a topic:")
    level = st.selectbox("Choose explanation level:", ["Beginner", "Intermediate", "Advanced"])

    if st.button("Explain"):
        explanation = get_explanation(topic, level, st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "user", "content": f"Explain {topic} at {level} level."})
        st.session_state.chat_history.append({"role": "assistant", "content": explanation})
        st.write(explanation)

    follow_up = st.text_input("Ask a follow-up question:")
    if st.button("Ask"):
        if follow_up:
            st.session_state.chat_history.append({"role": "user", "content": follow_up})
            response = get_explanation(topic, level, st.session_state.chat_history)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.write(response)

    if st.session_state.chat_history:
        with st.expander("💬 Conversation History"):
            for msg in st.session_state.chat_history:
                speaker = "🧑 You" if msg["role"] == "user" else "🤖 AI"
                st.markdown(f"**{speaker}:** {msg['content']}")

# -----------------------------
# 📝 Quiz
# -----------------------------
elif page == "📝 Quiz":
    st.title("📝 Quiz Generator")

    uploaded_file = st.file_uploader("Upload a PDF for quiz generation", type=["pdf"])
    text_input = st.text_area("Or enter text to generate quiz:")

    if "quiz" not in st.session_state:
        st.session_state.quiz = None
        st.session_state.answers = {}

    if st.button("Generate Quiz"):
        text = ""
        if uploaded_file:
            text = extract_text_from_pdf(uploaded_file)
            if not text.strip():
                st.warning("⚠️ No text extracted from PDF. Try another file.")
        elif text_input.strip():
            text = text_input

        if text:
            quiz = generate_mcq_quiz(text, num_questions=10)
            if quiz is None:
                st.error("⚠️ The AI service is busy. Please wait a few seconds and try again.")
            elif quiz:
                st.session_state.quiz = quiz
                st.session_state.answers = {}
            else:
                st.error("⚠️ Could not generate quiz. Try again.")
        else:
            st.warning("⚠️ Please upload a PDF or enter text.")

    if st.session_state.quiz:
        st.subheader("📋 Your Quiz")
        for i, q in enumerate(st.session_state.quiz):
            st.write(f"**Q{i+1}: {q['question']}**")
            options = q["options"]
            user_answer = st.radio(
                f"Select your answer for Q{i+1}",
                options,
                key=f"q{i+1}",
                index=None,
            )
            if user_answer:
                st.session_state.answers[i] = user_answer

        if st.button("Submit Answers"):
            correct = 0
            for i, q in enumerate(st.session_state.quiz):
                user_ans = st.session_state.answers.get(i, "")
                correct_ans = q["answer"]
                if user_ans == correct_ans:
                    correct += 1
                else:
                    st.markdown(f"❌ **Q{i+1} Wrong! Correct answer:** {correct_ans}")
            st.success(f"✅ You got {correct}/{len(st.session_state.quiz)} correct!")
