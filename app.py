"""
app.py
------
Streamlit UI for PropTrain AI — MCQ-based Real Estate Tutor Bot.
"""

import os
import streamlit as st
from dotenv import load_dotenv
from vector_db import VectorDB
from quiz_generator import QuizGenerator, TOPICS
from tutor_chat import TutorChat

load_dotenv()

st.set_page_config(
    page_title="PropTrain AI — Real Estate Tutor",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Source+Sans+3:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Source Sans 3', sans-serif;
    background-color: #0d0d12;
    color: #e8e0d0;
}
h1, h2, h3 { font-family: 'Playfair Display', serif; }

.question-box {
    background: rgba(180,140,80,0.06);
    border: 1px solid rgba(180,140,80,0.3);
    border-radius: 8px;
    padding: 22px 26px;
    margin-bottom: 20px;
    font-size: 1.15rem;
    line-height: 1.75;
}
.hint-box {
    background: rgba(255,255,255,0.03);
    border-left: 3px solid #b48c50;
    padding: 10px 16px;
    font-style: italic;
    color: #aaa;
    margin-top: 8px;
    border-radius: 0 6px 6px 0;
}
.option-btn {
    display: block;
    width: 100%;
    padding: 14px 20px;
    margin: 8px 0;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(180,140,80,0.25);
    border-radius: 8px;
    color: #e8e0d0;
    font-size: 1rem;
    text-align: left;
    cursor: pointer;
    transition: all 0.2s;
}
.option-correct {
    background: rgba(74,222,128,0.12) !important;
    border: 2px solid #4ade80 !important;
    border-radius: 8px;
    padding: 14px 20px;
    margin: 8px 0;
    color: #4ade80;
    font-size: 1rem;
    font-weight: 600;
}
.option-wrong {
    background: rgba(248,113,113,0.12) !important;
    border: 2px solid #f87171 !important;
    border-radius: 8px;
    padding: 14px 20px;
    margin: 8px 0;
    color: #f87171;
    font-size: 1rem;
}
.option-neutral {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 14px 20px;
    margin: 8px 0;
    color: #888;
    font-size: 1rem;
}
.result-correct {
    background: rgba(74,222,128,0.08);
    border: 1px solid rgba(74,222,128,0.3);
    border-radius: 10px;
    padding: 20px 24px;
    margin: 16px 0;
}
.result-incorrect {
    background: rgba(248,113,113,0.08);
    border: 1px solid rgba(248,113,113,0.3);
    border-radius: 10px;
    padding: 20px 24px;
    margin: 16px 0;
}
.explanation-box {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 20px 24px;
    margin: 12px 0;
}
.example-box {
    background: rgba(180,140,80,0.08);
    border-left: 4px solid #b48c50;
    border-radius: 0 8px 8px 0;
    padding: 16px 20px;
    margin: 12px 0;
}
.tip-box {
    background: rgba(96,165,250,0.08);
    border: 1px solid rgba(96,165,250,0.2);
    border-radius: 8px;
    padding: 14px 20px;
    margin: 12px 0;
    color: #93c5fd;
}
.stat-card {
    background: rgba(180,140,80,0.07);
    border: 1px solid rgba(180,140,80,0.2);
    border-radius: 8px;
    padding: 14px;
    text-align: center;
}
.score-display {
    font-size: 2.5rem;
    font-family: 'Playfair Display', serif;
    font-style: italic;
}
</style>
""", unsafe_allow_html=True)


# ── Init pipeline (cached) ──
@st.cache_resource(show_spinner="Building knowledge base...")
def init_pipeline():
    base_dir = os.path.dirname(__file__)
    doc_path = os.path.join(base_dir, "data", "real_estate_docs.txt")
    db = VectorDB(doc_path)
    generator = QuizGenerator(db)
    tutor = TutorChat(db)
    return db, generator, tutor

db, generator, tutor = init_pipeline()


# ── Session state ──
def init_state():
    defaults = {
        "screen"         : "home",
        "question"       : None,
        "evaluation"     : None,
        "selected_option": None,
        "answered"       : False,
        "show_hint"      : False,
        "correct_count"  : 0,
        "total_count"    : 0,
        "history"        : [],
        "topic"          : None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ── Helpers ──
def accuracy():
    if st.session_state.total_count == 0:
        return 0
    return round((st.session_state.correct_count / st.session_state.total_count) * 100)

def load_question(topic):
    with st.spinner("Generating question..."):
        q = generator.generate_question(topic, difficulty="beginner")
    st.session_state.question       = q
    st.session_state.evaluation     = None
    st.session_state.answered       = False
    st.session_state.selected_option= None
    st.session_state.show_hint      = False

def submit_answer(selected):
    q = st.session_state.question
    st.session_state.selected_option = selected
    with st.spinner("Checking your answer..."):
        ev = tutor.evaluate_answer(
            question       = q["question"],
            options        = q["options"],
            selected_option= selected,
            correct_option = q["correct_option"],
            topic          = q["topic"],
        )
    st.session_state.evaluation = ev
    st.session_state.answered   = True
    st.session_state.total_count += 1
    if ev["verdict"] == "correct":
        st.session_state.correct_count += 1
    st.session_state.history.append({
        "topic"  : q["topic"],
        "verdict": ev["verdict"],
    })


# ── SIDEBAR ──
with st.sidebar:
    st.markdown("## 🏠 PropTrain AI")
    st.markdown("*Real Estate Mastery Bot*")
    st.divider()

    st.markdown("### Topic")
    selected_topic = st.selectbox("Select Topic", TOPICS, label_visibility="collapsed")

    if st.button("▶  Start Quiz", use_container_width=True, type="primary"):
        st.session_state.topic  = selected_topic
        st.session_state.screen = "quiz"
        load_question(selected_topic)

    st.divider()

    if st.session_state.total_count > 0:
        st.markdown("### Session Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""<div class='stat-card'>
                <div style='font-size:1.6rem;color:#b48c50;font-style:italic'>{accuracy()}%</div>
                <div style='font-size:0.7rem;color:#666;text-transform:uppercase;letter-spacing:.1em'>Accuracy</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class='stat-card'>
                <div style='font-size:1.6rem;color:#b48c50;font-style:italic'>{st.session_state.correct_count}/{st.session_state.total_count}</div>
                <div style='font-size:0.7rem;color:#666;text-transform:uppercase;letter-spacing:.1em'>Score</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("#### Recent")
        for h in reversed(st.session_state.history[-6:]):
            icon  = "✓" if h["verdict"] == "correct" else "✗"
            color = "#4ade80" if h["verdict"] == "correct" else "#f87171"
            st.markdown(
                f"<div style='font-size:0.8rem;color:{color};padding:3px 0'>"
                f"{icon} {h['topic'][:28]}...</div>",
                unsafe_allow_html=True
            )


# ── HOME ──
if st.session_state.screen == "home":
    st.markdown("# PropTrain AI")
    st.markdown("### *Learn Real Estate, One Question at a Time*")
    st.markdown("""
    A beginner-friendly real estate quiz bot that:

    - 🎯 Asks you **multiple choice questions** on real estate topics
    - 🤖 Uses **AI** to explain answers in simple, everyday language
    - 💡 Gives **real-world examples** so concepts actually stick
    - 📈 Tracks your **accuracy** as you improve

    *No prior knowledge needed — perfect for complete beginners!*
    """)
    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""<div class='stat-card'>
            <div style='font-size:1.4rem;color:#b48c50'>10</div>
            <div style='font-size:0.7rem;color:#666;text-transform:uppercase'>Topics</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class='stat-card'>
            <div style='font-size:1.4rem;color:#b48c50'>MCQ</div>
            <div style='font-size:0.7rem;color:#666;text-transform:uppercase'>Format</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class='stat-card'>
            <div style='font-size:1.4rem;color:#b48c50'>Free</div>
            <div style='font-size:0.7rem;color:#666;text-transform:uppercase'>Always</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("\n*← Pick a topic and click **Start Quiz** to begin!*")


# ── QUIZ ──
elif st.session_state.screen == "quiz":
    q  = st.session_state.question
    ev = st.session_state.evaluation

    if q is None:
        st.info("Loading question...")
        st.stop()

    # Topic badge
    st.markdown(
        f"<div style='font-size:0.75rem;color:#b48c50;letter-spacing:.15em;"
        f"text-transform:uppercase;margin-bottom:8px'>"
        f"🏠 {q['topic']}  ·  Beginner</div>",
        unsafe_allow_html=True
    )

    # Question card
    st.markdown(f"<div class='question-box'>❓ {q['question']}</div>", unsafe_allow_html=True)

    # Hint toggle
    if not st.session_state.answered:
        if st.button("💡 Need a hint?"):
            st.session_state.show_hint = not st.session_state.show_hint
        if st.session_state.show_hint:
            st.markdown(f"<div class='hint-box'>{q.get('hint','')}</div>", unsafe_allow_html=True)

    st.markdown("**Choose your answer:**")

    # ── Options ──
    if not st.session_state.answered:
        cols = st.columns(2)
        options = q.get("options", {})
        option_keys = ["A", "B", "C", "D"]
        for i, key in enumerate(option_keys):
            with cols[i % 2]:
                label = f"{key}.  {options.get(key, '')}"
                if st.button(label, key=f"opt_{key}", use_container_width=True):
                    submit_answer(key)
                    st.rerun()
    else:
        # Show styled options after answering
        options = q.get("options", {})
        correct = ev.get("correct_option", q.get("correct_option", ""))
        selected = st.session_state.selected_option

        for key in ["A", "B", "C", "D"]:
            text = options.get(key, "")
            if key == correct and key == selected:
                st.markdown(f"<div class='option-correct'>✅ {key}.  {text}  ← Your Answer (Correct!)</div>", unsafe_allow_html=True)
            elif key == correct:
                st.markdown(f"<div class='option-correct'>✅ {key}.  {text}  ← Correct Answer</div>", unsafe_allow_html=True)
            elif key == selected:
                st.markdown(f"<div class='option-wrong'>❌ {key}.  {text}  ← Your Answer</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='option-neutral'>{key}.  {text}</div>", unsafe_allow_html=True)

    # ── Evaluation result ──
    if st.session_state.answered and ev:
        st.markdown("")

        if ev["verdict"] == "correct":
            # ── CORRECT ──
            st.markdown(f"""
            <div class='result-correct'>
                <div style='font-size:0.75rem;letter-spacing:.2em;color:#4ade80;text-transform:uppercase;margin-bottom:8px'>
                    ✓ &nbsp; CORRECT!
                </div>
                <div style='font-size:1rem;color:#ccc'>{ev.get('short_feedback','Great job!')}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class='explanation-box'>
                <div style='font-size:0.7rem;color:#b48c50;letter-spacing:.2em;text-transform:uppercase;margin-bottom:10px'>
                    Why this is correct
                </div>
                <div style='font-size:0.95rem;line-height:1.75;color:#ccc'>{ev.get('explanation','')}</div>
            </div>
            """, unsafe_allow_html=True)

        else:
            # ── INCORRECT ──
            st.markdown(f"""
            <div class='result-incorrect'>
                <div style='font-size:0.75rem;letter-spacing:.2em;color:#f87171;text-transform:uppercase;margin-bottom:8px'>
                    ✗ &nbsp; NOT QUITE — Let's Learn This Together!
                </div>
                <div style='font-size:1rem;color:#ccc'>{ev.get('short_feedback','No worries, let me explain!')}</div>
            </div>
            """, unsafe_allow_html=True)

            # Detailed explanation
            st.markdown(f"""
            <div class='explanation-box'>
                <div style='font-size:0.7rem;color:#b48c50;letter-spacing:.2em;text-transform:uppercase;margin-bottom:10px'>
                    📖 Here's What You Need to Know
                </div>
                <div style='font-size:0.95rem;line-height:1.8;color:#ccc'>{ev.get('explanation','')}</div>
            </div>
            """, unsafe_allow_html=True)

            # Real world example
            if ev.get("real_world_example"):
                st.markdown(f"""
                <div class='example-box'>
                    <div style='font-size:0.7rem;color:#b48c50;letter-spacing:.2em;text-transform:uppercase;margin-bottom:8px'>
                        🌍 Real-World Example
                    </div>
                    <div style='font-size:0.95rem;line-height:1.8;color:#ddd'>{ev.get('real_world_example','')}</div>
                </div>
                """, unsafe_allow_html=True)

        # Memory tip (shown for both correct and incorrect)
        if ev.get("remember_tip"):
            st.markdown(f"""
            <div class='tip-box'>
                <span style='color:#b48c50;font-weight:bold'>🧠 Remember: </span>
                <span style='color:#ccc'>{ev.get('remember_tip','')}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")

        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➡️  Next Question", type="primary", use_container_width=True):
                load_question(st.session_state.topic)
                st.rerun()
        with col2:
            if st.button("🔀  Change Topic", use_container_width=True):
                st.session_state.screen = "home"
                st.rerun()
                