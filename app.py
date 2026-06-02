import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
import re
import urllib.request
import urllib.parse

def get_youtube_video(query):
    query_string = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={query_string}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        html = urllib.request.urlopen(req)
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        if video_ids:
            return f"https://www.youtube.com/watch?v={video_ids[0]}"
    except Exception:
        pass
    return None

def mermaid(code: str):
    components.html(
        f"""
        <div class="mermaid">
            {code}
        </div>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true }});
        </script>
        """,
        height=500,
        scrolling=True
    )

st.set_page_config(layout="wide", page_title="Student Study Helper", page_icon="📚")

# Configure Groq API
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("Please add your GROQ_API_KEY to .streamlit/secrets.toml")
    st.stop()

def ask_groq(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    return response.choices[0].message.content

# Init session states
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = []
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "quiz_final_score" not in st.session_state:
    st.session_state.quiz_final_score = 0.0

# Sidebar
st.sidebar.header("Settings")
student_class = st.sidebar.selectbox("Select Class", [str(i) for i in range(6, 13)])
subject = st.sidebar.selectbox("Select Subject", ["Maths", "Science", "Physics", "Chemistry", "Biology", "History", "Geography", "English"])

st.sidebar.info(f"Class {student_class} | {subject}")

# Main Area
st.title("📚 Student Study Helper")
st.subheader("Your Personal AI Study Buddy 🎓")

st.divider()

question = st.text_area("What do you want to learn today?", height=100)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💡 Explain", "📝 Quiz", "🃏 Flashcards", "📋 Summary", "📚 Resources", "🎨 Visualise"
])

with tab1:
    if st.button("Explain It", key="btn_explain"):
        if not question.strip():
            st.warning("Please enter a topic first!")
        else:
            with st.spinner("Generating explanation..."):
                prompt = f"You are a helpful teacher. Explain this for Class {student_class} {subject} student in simple language under 150 words: {question}"
                try:
                    result = ask_groq(prompt)
                    st.info(result)
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    
    st.divider()
    follow_up = st.text_input("Ask a follow-up question:")
    if st.button("Ask Follow-up", key="btn_followup"):
        if follow_up.strip():
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": follow_up})
            with st.spinner("Thinking..."):
                try:
                    # Construct prompt with context
                    prompt = f"Topic: {question}\nClass: {student_class} {subject}\nAnswer this follow-up question: {follow_up}"
                    answer = ask_groq(prompt)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"An error occurred: {e}")
    
    if st.session_state.chat_history:
        st.write("### Follow-up History")
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.write(f"**You:** {msg['content']}")
            else:
                st.info(f"**AI:** {msg['content']}")

with tab2:
    if st.button("Generate Quiz", key="btn_quiz"):
        if not question.strip():
            st.warning("Please enter a topic first!")
        else:
            with st.spinner("Generating quiz..."):
                prompt = f"Generate 5 MCQ questions for Class {student_class} {subject} on: {question}.\nFormat strictly:\nQ1. question\nA) option\nB) option\nC) option\nD) option\nAnswer: X"
                try:
                    quiz_text = ask_groq(prompt)
                    mcqs = re.findall(r'(Q\d+\..*?)(?=Q\d+\.|$)', quiz_text, re.DOTALL)
                    parsed_mcqs = []
                    for mcq in mcqs:
                        lines = mcq.strip().split('\n')
                        q_text = ""
                        opts = []
                        ans = ""
                        for line in lines:
                            if re.match(r'^[A-D]\)', line.strip()):
                                opts.append(line.strip())
                            elif line.strip().startswith('Answer:'):
                                ans = line.replace('Answer:', '').strip()
                            else:
                                if q_text:
                                    q_text += "\n" + line.strip()
                                else:
                                    q_text = line.strip()
                        parsed_mcqs.append({"question": q_text, "options": opts, "answer": ans})
                    st.session_state.quiz_data = parsed_mcqs
                    st.session_state.quiz_submitted = False
                except Exception as e:
                    st.error(f"An error occurred: {e}")

    if st.session_state.get("quiz_data"):
        st.write("### Quiz")
        user_answers = {}
        for i, q in enumerate(st.session_state.quiz_data):
            st.write(f"**{q['question']}**")
            user_choice = st.radio("Select an option:", q['options'], index=None, key=f"radio_{i}", disabled=st.session_state.quiz_submitted)
            user_answers[i] = user_choice
            st.write("")
            
        if not st.session_state.quiz_submitted:
            if st.button("Submit Quiz"):
                score = 0.0
                for i, q in enumerate(st.session_state.quiz_data):
                    ans_letter = q['answer'].strip()[0] if q['answer'] else ""
                    choice = user_answers[i]
                    if choice:
                        choice_letter = choice.strip()[0]
                        if choice_letter.upper() == ans_letter.upper():
                            score += 1
                        else:
                            score -= 0.5
                st.session_state.quiz_final_score = score
                st.session_state.quiz_submitted = True
                st.rerun()
        else:
            st.success(f"### Final Score: {st.session_state.quiz_final_score} / 5")
            for i, q in enumerate(st.session_state.quiz_data):
                ans_letter = q['answer'].strip()[0] if q['answer'] else ""
                choice = user_answers[i]
                choice_letter = choice.strip()[0] if choice else ""
                
                if choice_letter.upper() == ans_letter.upper():
                    st.info(f"**Q{i+1}:** Correct! Answer is {q['answer']}")
                else:
                    if choice:
                        st.error(f"**Q{i+1}:** Incorrect. You chose {choice}. Correct answer is {q['answer']}")
                    else:
                        st.warning(f"**Q{i+1}:** Not attempted. Correct answer is {q['answer']}")
            
            if st.button("Reset Quiz"):
                st.session_state.quiz_data = []
                st.session_state.quiz_submitted = False
                st.rerun()

with tab3:
    if st.button("Generate Flashcards", key="btn_flashcards"):
        if not question.strip():
            st.warning("Please enter a topic first!")
        else:
            with st.spinner("Generating flashcards..."):
                prompt = f"Generate 5 flashcards for Class {student_class} {subject} on: {question}.\nFormat strictly:\nTERM: term here\nDEFINITION: definition here\n---"
                try:
                    flashcards_text = ask_groq(prompt)
                    cards = flashcards_text.split("---")
                    for card in cards:
                        if card.strip():
                            with st.container():
                                st.info(card.strip())
                except Exception as e:
                    st.error(f"An error occurred: {e}")

with tab4:
    if st.button("Summarise", key="btn_summary"):
        if not question.strip():
            st.warning("Please enter a topic first!")
        else:
            with st.spinner("Summarising..."):
                prompt = f"Give a bullet point summary under 150 words for Class {student_class} {subject} on: {question}. Then if subject is Maths, Physics or Chemistry, list 3 key formulas as: Formula: name = equation"
                try:
                    summary = ask_groq(prompt)
                    st.success(summary)
                except Exception as e:
                    st.error(f"An error occurred: {e}")

with tab5:
    if st.button("Get Resources", key="btn_resources"):
        if not question.strip():
            st.warning("Please enter a topic first!")
        else:
            with st.spinner("Finding resources..."):
                prompt = f"For Class {student_class} {subject} topic: {question} suggest:\n1. YOUTUBE: 3 search queries student should search on YouTube\n2. BOOKS: 3 book names with authors for this topic\n3. WEBSITES: 3 websites to read more (Khan Academy, NCERT, Byju's etc)\n4. TIPS: 2 study tips for this topic\nFormat each section with its header clearly."
                try:
                    resources_text = ask_groq(prompt)
                    parts = re.split(r'(?=1\.\s*YOUTUBE|2\.\s*BOOKS|3\.\s*WEBSITES|4\.\s*TIPS)', resources_text, flags=re.IGNORECASE)
                    
                    if len(parts) <= 1:
                        with st.expander("Resources"):
                            st.write(resources_text)
                    else:
                        for part in parts:
                            if not part.strip(): continue
                            lines = part.strip().split('\n', 1)
                            header = lines[0]
                            content = lines[1] if len(lines) > 1 else ""
                            with st.expander(header):
                                st.write(content)
                except Exception as e:
                    st.error(f"An error occurred: {e}")

with tab6:
    if st.button("Visualise", key="btn_visualise"):
        if not question.strip():
            st.warning("Please enter a topic first!")
        else:
            with st.spinner("Creating visualisation..."):
                prompt = f"Explain the topic '{question}' for a Class {student_class} {subject} student by providing two things:\n1. A highly creative, relatable real-world analogy (1-2 paragraphs).\n2. A Mermaid.js flowchart (graph TD) illustrating the concept. Use ```mermaid\n...\n``` for the code block. IMPORTANT: Do NOT use parentheses (), brackets [], or any special characters inside the node names. Keep the flowchart syntax extremely simple and valid to avoid syntax errors."
                try:
                    visual = ask_groq(prompt)
                    
                    if "```mermaid" in visual:
                        parts = visual.split("```mermaid")
                        analogy = parts[0]
                        mermaid_code = parts[1].split("```")[0]
                        
                        if analogy.strip():
                            st.write("### 📖 Concept Analogy")
                            st.info(analogy.strip())
                            
                        st.write("### 🗺️ Concept Map")
                        mermaid(mermaid_code.strip())
                    else:
                        st.write("### 📖 Visualisation")
                        st.write(visual)
                        
                    st.write("### 📺 Related Video")
                    video_query = f"{question} class {student_class} {subject}"
                    video_url = get_youtube_video(video_query)
                    if video_url:
                        st.video(video_url)
                    else:
                        search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(video_query)}"
                        st.info(f"Could not automatically embed a video. [Click here to search YouTube for '{video_query}']({search_url})")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

st.divider()
st.markdown("<div style='text-align: center'>Powered by Groq LLaMA | Built for Students 🚀</div>", unsafe_allow_html=True)
