"""
app.py
------
Streamlit UI for the Real Estate Tutor Bot.
Orchestrates VectorDB → QuizGenerator → TutorChat into a
clean, interactive assessment experience.
"""

import os
import streamlit as st
from dotenv import load_dotenv
from vector_db import VectorDB
from quiz_generator import QuizGenerator, TOPICS
from tutor_chat import TutorChat

load_dotenv()

# ──────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────
st.set_page_config(
    page_title="PropTrain AI — Real Estate Tutor",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────
# CUSTOM CSS
# ──────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Source+Sans+3:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Source Sans 3', sans-serif;
    background-color: #0d0d12;
    color: #e8e0d0;
}
h1, h2, h3 { font-family: 'Playfair Display', serif; }

.verdict-correct  { background:#0f2e1a; border:1px solid #2d6a3f; border-radius:6px; padding:16px 20px; }
.verdict-partial  { background:#2e2310; border:1px solid #7a5c20; border-radius:6px; padding:16px 20px; }
.verdict-incorrect{ background:#2e0f0f; border:1px solid #6a2d2d; border-radius:6px; padding:16px 20px; }

.score-big { font-size:3rem; font-family:'Playfair Display',serif; font-style:italic; }
.score-correct   { color:#4ade80; }
.score-partial   { color:#fbbf24; }
.score-incorrect { color:#f87171; }

.question-box {
    background: rgba(180,140,80,0.06);
    border: 1px solid rgba(180,140,80,0.25);
    border-radius: 6px;
    padding: 20px 24px;
    margin-bottom: 16px;
    font-size: 1.1rem;
    line-height: 1.7;
}
.hint-box {
    background: rgba(255,255,255,0.03);
    border-left: 3px solid #b48c50;
    padding: 10px 16px;
    font-style: italic;
    color: #aaa;
    margin-top: 12px;
}
.explanation-box {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius:6px;
    padding: 18px 22px;
    margin-top:12px;
}
.pro-tip {
    border-top: 1px solid rgba(180,140,80,0.2);
    margin-top: 14px;
    padding-top: 14px;
    color: #b48c50;
    font-style: italic;
}
.correct-answer-box {
    background: rgba(74,222,128,0.05);
    border: 1px solid rgba(74,222,128,0.2);
    border-radius: 6px;
    padding: 14px 18px;
    margin-top: 12px;
}
.stat-card {
    background: rgba(180,140,80,0.07);
    border: 1px solid rgba(180,140,80,0.2);
    border-radius:6px;
    padding: 14px;
    text-align:center;
}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────
# CACHED RESOURCE INIT (runs once)
# ──────────────────────────────────────────
@st.cache_resource(show_spinner="Building knowledge base...")
def init_pipeline():
    base_dir = os.path.dirname(__file__)
    doc_path = os.path.join(base_dir, "data", "real_estate_docs.txt")
    db = VectorDB(doc_path)
    generator = QuizGenerator(db)
    tutor = TutorChat(db)
    return db, generator, tutor


db, generator, tutor = init_pipeline()


# ──────────────────────────────────────────
# SESSION STATE INIT
# ──────────────────────────────────────────
def init_state():
    defaults = {
        "screen"        : "home",      # home | quiz
        "question"      : None,        # current question dict
        "evaluation"    : None,        # current evaluation dict
        "user_answer"   : "",
        "answered"      : False,
        "show_hint"     : False,
        "session_scores": [],          # list of ints
        "history"       : [],          # list of result dicts
        "difficulty"    : "intermediate",
        "topic"         : None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ──────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────
def avg_score():
    s = st.session_state.session_scores
    return round(sum(s) / len(s)) if s else 0

def verdict_class(v):
    return {"correct":"verdict-correct","partial":"verdict-partial","incorrect":"verdict-incorrect"}.get(v,"")

def score_class(v):
    return {"correct":"score-correct","partial":"score-partial","incorrect":"score-incorrect"}.get(v,"")

def verdict_icon(v):
    return {"correct":"✓","partial":"◑","incorrect":"✗"}.get(v,"?")

def load_question(topic, difficulty):
    with st.spinner("Retrieving context & generating question..."):
        q = generator.generate_question(topic, difficulty)
    st.session_state.question   = q
    st.session_state.evaluation = None
    st.session_state.answered   = False
    st.session_state.show_hint  = False
    st.session_state.user_answer= ""

def submit_answer():
    q = st.session_state.question
    answer = st.session_state.user_answer.strip()
    if not answer:
        st.warning("Please type an answer before submitting.")
        return
    with st.spinner("AI is evaluating your answer..."):
        ev = tutor.evaluate_answer(
            question      = q["question"],
            user_answer   = answer,
            correct_answer= q["correct_answer"],
            key_points    = q["key_points"],
            topic         = q["topic"],
        )
    st.session_state.evaluation = ev
    st.session_state.answered   = True
    st.session_state.session_scores.append(ev["score"])
    st.session_state.history.append({
        "topic"  : q["topic"],
        "score"  : ev["score"],
        "verdict": ev["verdict"],
    })


# ──────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏠 PropTrain AI")
    st.markdown("*Real Estate Mastery Bot*")
    st.divider()

    st.markdown("### Difficulty")
    st.session_state.difficulty = st.radio(
        "Select Difficulty", ["beginner", "intermediate", "advanced"],
        index=["beginner","intermediate","advanced"].index(st.session_state.difficulty),
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("### Topic")
    selected_topic = st.selectbox("Select Topic", TOPICS, label_visibility="collapsed")

    if st.button("▶  Start Quiz", use_container_width=True, type="primary"):
        st.session_state.topic  = selected_topic
        st.session_state.screen = "quiz"
        load_question(selected_topic, st.session_state.difficulty)

    st.divider()

    # Session stats
    if st.session_state.session_scores:
        st.markdown("### Session Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""<div class='stat-card'>
                <div style='font-size:1.6rem;color:#b48c50;font-style:italic'>{avg_score()}</div>
                <div style='font-size:0.7rem;color:#666;text-transform:uppercase;letter-spacing:.1em'>Avg Score</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""<div class='stat-card'>
                <div style='font-size:1.6rem;color:#b48c50;font-style:italic'>{len(st.session_state.session_scores)}</div>
                <div style='font-size:0.7rem;color:#666;text-transform:uppercase;letter-spacing:.1em'>Questions</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("#### Recent")
        for h in reversed(st.session_state.history[-5:]):
            icon  = verdict_icon(h["verdict"])
            color = {"correct":"#4ade80","partial":"#fbbf24","incorrect":"#f87171"}.get(h["verdict"],"#888")
            st.markdown(
                f"<div style='font-size:0.8rem;color:{color};padding:3px 0'>"
                f"{icon} {h['topic'][:22]}... — {h['score']}pts</div>",
                unsafe_allow_html=True
            )


# ──────────────────────────────────────────
# HOME SCREEN
# ──────────────────────────────────────────
if st.session_state.screen == "home":
    st.markdown("# PropTrain AI")
    st.markdown("### *Master Property Listings with AI*")
    st.markdown("""
    An intelligent assessment platform that evaluates your real estate knowledge,
    pinpoints gaps, and explains concepts with industry-grade depth.

    **How it works:**
    1. 📚 Select a **topic** and **difficulty** from the sidebar
    2. 🤖 Claude generates a question grounded in the knowledge base (RAG)
    3. ✍️ Type your answer — the AI evaluates it intelligently
    4. 💡 Get a deep explanation + pro insider tip
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
            <div style='font-size:1.4rem;color:#b48c50'>RAG</div>
            <div style='font-size:0.7rem;color:#666;text-transform:uppercase'>Grounded AI</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""<div class='stat-card'>
            <div style='font-size:1.4rem;color:#b48c50'>0–100</div>
            <div style='font-size:0.7rem;color:#666;text-transform:uppercase'>Smart Scoring</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("\n*← Select a topic and click **Start Quiz** to begin*")


# ──────────────────────────────────────────
# QUIZ SCREEN
# ──────────────────────────────────────────
elif st.session_state.screen == "quiz":
    q  = st.session_state.question
    ev = st.session_state.evaluation

    if q is None:
        st.info("Loading question...")
        st.stop()

    # Topic + difficulty badge
    st.markdown(
        f"<div style='font-size:0.75rem;color:#b48c50;letter-spacing:.15em;text-transform:uppercase;margin-bottom:4px'>"
        f"{q['topic']}  ·  {q['difficulty'].capitalize()}</div>",
        unsafe_allow_html=True
    )
    st.markdown(f"### Question")

    # Question card
    st.markdown(f"<div class='question-box'>{q['question']}</div>", unsafe_allow_html=True)

    # Hint toggle
    if not st.session_state.answered:
        if st.button("💡 Show Hint"):
            st.session_state.show_hint = not st.session_state.show_hint
        if st.session_state.show_hint:
            st.markdown(f"<div class='hint-box'>{q['hint']}</div>", unsafe_allow_html=True)

    st.divider()

    # ── Answer input ──
    if not st.session_state.answered:
        st.markdown("**Your Answer**")
        answer = st.text_area(
            "Your Answer", height=130, placeholder="Type your answer here...",
            key="answer_input", label_visibility="collapsed"
        )
        st.session_state.user_answer = answer

        if st.button("Submit Answer →", type="primary", use_container_width=True):
            submit_answer()
            st.rerun()

    # ── Evaluation result ──
    if st.session_state.answered and ev:
        v = ev["verdict"]
        vc = verdict_class(v)
        sc = score_class(v)
        vi = verdict_icon(v)

        # Score banner
        st.markdown(f"""
        <div class='{vc}' style='display:flex;align-items:center;justify-content:space-between'>
            <div>
                <div style='font-size:0.75rem;letter-spacing:.2em;text-transform:uppercase;margin-bottom:6px'>
                    {vi} &nbsp; {v.upper()}
                </div>
                <div style='font-size:1rem;color:#ccc'>{ev['short_feedback']}</div>
            </div>
            <div class='score-big {sc}'>{ev['score']}<span style='font-size:1rem;color:#555'>/100</span></div>
        </div>
        """, unsafe_allow_html=True)

        # Explanation
        st.markdown(f"""
        <div class='explanation-box'>
            <div style='font-size:0.7rem;color:#b48c50;letter-spacing:.2em;text-transform:uppercase;margin-bottom:10px'>
                Deep Explanation
            </div>
            <div style='font-size:0.95rem;line-height:1.75;color:#ccc'>{ev['explanation']}</div>
            <div class='pro-tip'>
                ★ <strong>Pro Tip:</strong> {ev['pro_tip']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Model answer
        st.markdown(f"""
        <div class='correct-answer-box'>
            <div style='font-size:0.7rem;color:#4ade80;letter-spacing:.2em;text-transform:uppercase;margin-bottom:8px'>
                Model Answer
            </div>
            <div style='font-size:0.9rem;color:#ccc;line-height:1.6'>{ev['correct_answer']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")

        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Next Question →", type="primary", use_container_width=True):
                load_question(st.session_state.topic, st.session_state.difficulty)
                st.rerun()
        with col2:
            if st.button("Change Topic", use_container_width=True):
                st.session_state.screen = "home"
                st.rerun()