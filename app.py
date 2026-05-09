import streamlit as st
from groq import Groq
import re

# Page config
st.set_page_config(page_title="Student Study Helper", page_icon="📚")

# Header
st.title("📚 Student Study Helper")

# Configure Groq API
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("Please add your GROQ_API_KEY to .streamlit/secrets.toml")
    st.stop()

# Sidebar
st.sidebar.header("Settings")
student_class = st.sidebar.selectbox("Select Class", [str(i) for i in range(6, 13)])
subject = st.sidebar.selectbox("Select Subject", ["Maths", "Science", "History", "Geography", "English", "Physics", "Chemistry", "Biology"])

# Main area
st.subheader("What's your doubt?")
question = st.text_area("Type your question or topic here...", height=150)

col1, col2 = st.columns(2)

def ask_groq(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    return response.choices[0].message.content

if col1.button("Explain It", use_container_width=True):
    if not question.strip():
        st.warning("Please enter a question first!")
    else:
        with st.spinner("Generating explanation..."):
            prompt = f"You are a helpful teacher. Explain this for Class {student_class} {subject} student in simple language under 150 words: {question}"
            try:
                result = ask_groq(prompt)
                st.info(result)
            except Exception as e:
                st.error(f"An error occurred: {e}")

if col2.button("Quiz Me", use_container_width=True):
    if not question.strip():
        st.warning("Please enter a topic first!")
    else:
        with st.spinner("Generating quiz..."):
            prompt = f"Generate 3 MCQ questions for Class {student_class} {subject} on: {question}. Format: Q1. question\nA) \nB) \nC) \nD) \nAnswer: X\n"
            try:
                quiz_text = ask_groq(prompt)
                mcqs = re.findall(r'(Q\d+\..*?)(?=Q\d+\.|$)', quiz_text, re.DOTALL)
                if not mcqs:
                    st.write(quiz_text)
                else:
                    for mcq in mcqs:
                        if "Answer:" in mcq:
                            q_part, a_part = mcq.split("Answer:", 1)
                            st.write(q_part.strip())
                            with st.expander("Show Answer"):
                                st.write(a_part.strip())
                        else:
                            st.write(mcq.strip())
            except Exception as e:
                st.error(f"An error occurred: {e}")
