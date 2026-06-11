import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
import re
import urllib.request
import urllib.parse
from fpdf import FPDF
import db_utils

# Init DB
db_utils.init_db()

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

def create_pdf(title, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    
    # Title
    pdf.set_font("helvetica", 'B', 16)
    pdf.cell(w=0, h=10, text=title, new_x="LMARGIN", new_y="NEXT", align='C')
    pdf.ln(10)
    
    # Content
    pdf.set_font("helvetica", size=12)
    # FPDF2 handles unicode strings gracefully if font supports it. Helvetica is standard.
    pdf.multi_cell(w=0, h=8, text=content)
    
    return bytes(pdf.output())

st.set_page_config(layout="wide", page_title="Student Study Helper", page_icon="📚")

# Custom CSS for Premium UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #6e8efb, #a777e3);
        color: white;
        border-radius: 8px;
        border: none;
        transition: transform 0.2s, box-shadow 0.2s;
        font-weight: 600;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(167, 119, 227, 0.4);
        color: white;
    }
    
    .stTextInput>div>div>input, .stTextArea>div>textarea {
        border-radius: 8px;
        border: 1px solid #ddd;
    }
    
    /* Glassmorphism for info boxes */
    .stAlert {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Login System
if "username" not in st.session_state:
    st.markdown("<h1 style='text-align: center; color: #a777e3;'>Welcome to Student Study Helper 🎓</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Please enter your username to continue.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        uname = st.text_input("Username:")
        if st.button("Login", use_container_width=True):
            if uname.strip():
                db_utils.get_or_create_user(uname.strip())
                st.session_state.username = uname.strip()
                st.rerun()
            else:
                st.warning("Username cannot be empty")
    st.stop()


# Configure Groq API
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except KeyError:
    st.error("Please add your GROQ_API_KEY to .streamlit/secrets.toml")
    st.stop()

@st.cache_data(show_spinner=False)
def ask_groq_cached(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    return response.choices[0].message.content

def ask_groq_no_cache(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800
    )
    return response.choices[0].message.content

# Init session states
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "tutor_history" not in st.session_state:
    st.session_state.tutor_history = []
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = []
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False
if "quiz_final_score" not in st.session_state:
    st.session_state.quiz_final_score = 0.0

# Sidebar
st.sidebar.header(f"Welcome, {st.session_state.username}! 👋")
student_class = st.sidebar.selectbox("Select Class", [str(i) for i in range(6, 13)])
subject = st.sidebar.selectbox("Select Subject", ["Maths", "Science", "Physics", "Chemistry", "Biology", "History", "Geography", "English"])

st.sidebar.info(f"Class {student_class} | {subject}")

# Sidebar Dashboard Profile
with st.sidebar.expander("📊 My Progress", expanded=False):
    progress = db_utils.get_user_progress(st.session_state.username)
    if progress:
        for p in progress[:5]: # show last 5
            st.write(f"- **{p[0]} ({p[1]})**: {p[2]}/{p[3]} on {p[4][:10]}")
    else:
        st.write("No quizzes taken yet.")
        
if st.sidebar.button("Logout"):
    del st.session_state.username
    st.rerun()

# Main Area
st.title("📚 Student Study Helper")
st.subheader("Your Personal AI Study Buddy 🎓")

st.divider()

question = st.text_area("What do you want to learn today?", height=100)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "💡 Explain", "💬 Tutor", "📝 Quiz", "🃏 Flashcards", "📋 Summary", "📚 Resources", "🎨 Visualise", "📅 Planner"
])

with tab1:
    if st.button("Explain It", key="btn_explain"):
        if not question.strip():
            st.warning("Please enter a topic first!")
        else:
            with st.spinner("Generating explanation..."):
                prompt = f"You are a helpful teacher. Explain this for Class {student_class} {subject} student in simple language under 150 words: {question}"
                try:
                    result = ask_groq_cached(prompt)
                    st.info(result)
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    
    st.divider()
    follow_up = st.text_input("Ask a follow-up question:")
    if st.button("Ask Follow-up", key="btn_followup"):
        if follow_up.strip():
            st.session_state.chat_history.append({"role": "user", "content": follow_up})
            with st.spinner("Thinking..."):
                try:
                    prompt = f"Topic: {question}\nClass: {student_class} {subject}\nAnswer this follow-up question: {follow_up}"
                    answer = ask_groq_no_cache(prompt)
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
    st.write("### 💬 Your Dedicated AI Tutor")
    st.write("Chat freely about the subject and topic!")
    
    for msg in st.session_state.tutor_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if chat_prompt := st.chat_input("Ask me anything..."):
        st.session_state.tutor_history.append({"role": "user", "content": chat_prompt})
        with st.chat_message("user"):
            st.markdown(chat_prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                sys_msg = f"You are an expert, friendly AI tutor for a Class {student_class} {subject} student. Topic focus: {question if question else 'General'}."
                
                history_text = ""
                for m in st.session_state.tutor_history[-5:]:
                    history_text += f"{m['role']}: {m['content']}\n"
                    
                full_prompt = f"{sys_msg}\nConversation history:\n{history_text}\nassistant:"
                try:
                    response = ask_groq_no_cache(full_prompt)
                    st.markdown(response)
                    st.session_state.tutor_history.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"An error occurred: {e}")

with tab3:
    if st.button("Generate Quiz", key="btn_quiz"):
        if not question.strip():
            st.warning("Please enter a topic first!")
        else:
            with st.spinner("Generating quiz..."):
                prompt = f"Generate 5 MCQ questions for Class {student_class} {subject} on: {question}.\nFormat strictly:\nQ1. question\nA) option\nB) option\nC) option\nD) option\nAnswer: X"
                try:
                    quiz_text = ask_groq_cached(prompt)
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
                
                # Save to Database
                db_utils.save_quiz_score(st.session_state.username, subject, question, score, len(st.session_state.quiz_data))
                
                st.rerun()
        else:
            st.success(f"### Final Score: {st.session_state.quiz_final_score} / {len(st.session_state.quiz_data)}")
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

with tab4:
    if st.button("Generate Flashcards", key="btn_flashcards"):
        if not question.strip():
            st.warning("Please enter a topic first!")
        else:
            with st.spinner("Generating flashcards..."):
                prompt = f"Generate 5 flashcards for Class {student_class} {subject} on: {question}.\nFormat strictly:\nTERM: term here\nDEFINITION: definition here\n---"
                try:
                    flashcards_text = ask_groq_cached(prompt)
                    cards = flashcards_text.split("---")
                    
                    pdf_content = ""
                    
                    for card in cards:
                        if card.strip():
                            pdf_content += card.strip() + "\n\n"
                            with st.container():
                                st.info(card.strip())
                    
                    try:
                        pdf_bytes = create_pdf(f"Flashcards: {question}", pdf_content)
                        st.download_button(
                            label="📄 Download Flashcards PDF",
                            data=pdf_bytes,
                            file_name=f"flashcards.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"Failed to create PDF: {e}")
                        
                except Exception as e:
                    st.error(f"An error occurred: {e}")

with tab5:
    if st.button("Summarise", key="btn_summary"):
        if not question.strip():
            st.warning("Please enter a topic first!")
        else:
            with st.spinner("Summarising..."):
                prompt = f"Give a bullet point summary under 150 words for Class {student_class} {subject} on: {question}. Then if subject is Maths, Physics or Chemistry, list 3 key formulas as: Formula: name = equation"
                try:
                    summary = ask_groq_cached(prompt)
                    st.success(summary)
                    
                    try:
                        pdf_bytes = create_pdf(f"Summary: {question}", summary)
                        st.download_button(
                            label="📄 Download Summary PDF",
                            data=pdf_bytes,
                            file_name=f"summary.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"Failed to create PDF: {e}")
                        
                except Exception as e:
                    st.error(f"An error occurred: {e}")

with tab6:
    if st.button("Get Resources", key="btn_resources"):
        if not question.strip():
            st.warning("Please enter a topic first!")
        else:
            with st.spinner("Finding resources..."):
                prompt = f"For Class {student_class} {subject} topic: {question} suggest:\n1. YOUTUBE: 3 search queries student should search on YouTube\n2. BOOKS: 3 book names with authors for this topic\n3. WEBSITES: 3 websites to read more (Khan Academy, NCERT, Byju's etc)\n4. TIPS: 2 study tips for this topic\nFormat each section with its header clearly."
                try:
                    resources_text = ask_groq_cached(prompt)
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

with tab7:
    if st.button("Visualise", key="btn_visualise"):
        if not question.strip():
            st.warning("Please enter a topic first!")
        else:
            with st.spinner("Creating visualisation..."):
                prompt = f"Explain the topic '{question}' for a Class {student_class} {subject} student by providing two things:\n1. A highly creative, relatable real-world analogy (1-2 paragraphs).\n2. A Mermaid.js flowchart (graph TD) illustrating the concept. Use ```mermaid\n...\n``` for the code block. IMPORTANT: Do NOT use parentheses (), brackets [], or any special characters inside the node names. Keep the flowchart syntax extremely simple and valid to avoid syntax errors."
                try:
                    visual = ask_groq_cached(prompt)
                    
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

with tab8:
    st.write("### 📅 Study Schedule Planner")
    exam_date = st.text_input("When is your exam? (e.g., 'Next Friday', 'In 2 weeks', 'Oct 15')")
    chapters = st.text_area("What chapters/topics do you need to cover?")
    
    if st.button("Generate Schedule"):
        if not exam_date.strip() or not chapters.strip():
            st.warning("Please provide both the exam date and chapters.")
        else:
            with st.spinner("Planning your schedule..."):
                prompt = f"Create a detailed, day-by-day study schedule for a Class {student_class} {subject} student. The exam is on: {exam_date}. The topics to cover are: {chapters}. Output the schedule in a clear markdown table format with columns: Day/Date, Topic to Study, Activity (Read/Practice/Mock Test)."
                try:
                    schedule = ask_groq_cached(prompt)
                    st.markdown(schedule)
                    
                    try:
                        pdf_bytes = create_pdf(f"Study Schedule: {subject}", schedule)
                        st.download_button(
                            label="📄 Download Schedule PDF",
                            data=pdf_bytes,
                            file_name="study_schedule.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"Failed to create PDF: {e}")
                        
                except Exception as e:
                    st.error(f"An error occurred: {e}")

st.divider()
st.markdown("<div style='text-align: center'>Powered by Groq LLaMA | Built for Students 🚀</div>", unsafe_allow_html=True)
