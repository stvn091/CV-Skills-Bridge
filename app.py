import streamlit as st
import json
import pdfplumber
from google import genai
from google.genai import types
from PIL import Image

# ─── Page config — must be first Streamlit call ───────────────────────────────
st.set_page_config(
    page_title="CareerBridge AI",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="collapsed"
)

# ─── Global CSS ───────────────────────────────────────────────────────────────
# FIX: was unsafe_allowed_with_html (typo) → correct param is unsafe_allow_html
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #0a0a0f;
    color: #e8e8f0;
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 4rem 2rem; max-width: 1400px; }

/* ── Hero section ── */
.hero-wrap {
    padding: 3.5rem 0 2.5rem 0;
    border-bottom: 1px solid #1e1e2e;
    margin-bottom: 2.5rem;
}

.hero-eyebrow {
    display: inline-block;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #7c6af7;
    background: rgba(124, 106, 247, 0.12);
    border: 1px solid rgba(124, 106, 247, 0.25);
    padding: 4px 12px;
    border-radius: 20px;
    margin-bottom: 1rem;
}

.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(2rem, 4vw, 3.2rem);
    font-weight: 700;
    color: #f0f0fa;
    line-height: 1.15;
    margin: 0 0 0.75rem 0;
    letter-spacing: -0.02em;
}

.hero-title span {
    background: linear-gradient(135deg, #7c6af7 0%, #a78bfa 50%, #60d4f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    font-size: 1rem;
    color: #8888a8;
    line-height: 1.65;
    max-width: 560px;
    margin: 0;
}

/* ── Step labels ── */
.step-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #5a5a7a;
    margin-bottom: 0.5rem;
}

/* ── Input panels ── */
.panel {
    background: #12121e;
    border: 1px solid #1e1e30;
    border-radius: 14px;
    padding: 1.5rem;
    height: 100%;
}

.panel-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: #d0d0e8;
    margin-bottom: 0.25rem;
}

.panel-sub {
    font-size: 0.8rem;
    color: #5a5a7a;
    margin-bottom: 1rem;
    line-height: 1.5;
}

/* ── Streamlit widget overrides ── */
.stTextArea textarea {
    background: #0d0d18 !important;
    border: 1px solid #2a2a40 !important;
    border-radius: 10px !important;
    color: #c0c0da !important;
    font-size: 0.875rem !important;
    resize: none !important;
}

.stTextArea textarea:focus {
    border-color: #7c6af7 !important;
    box-shadow: 0 0 0 2px rgba(124,106,247,0.15) !important;
}

.stFileUploader {
    background: #0d0d18 !important;
    border: 1px dashed #2a2a40 !important;
    border-radius: 10px !important;
}

.stRadio label { color: #8888a8 !important; font-size: 0.875rem !important; }
.stRadio [data-testid="stMarkdownContainer"] p { color: #8888a8 !important; }

/* ── Primary button ── */
.stButton button[kind="primary"] {
    background: linear-gradient(135deg, #7c6af7, #60d4f7) !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    color: #ffffff !important;
    padding: 0.65rem 2rem !important;
    transition: opacity 0.2s ease !important;
    letter-spacing: 0.01em !important;
}

.stButton button[kind="primary"]:hover { opacity: 0.88 !important; }

/* ── Score card ── */
.score-card {
    background: linear-gradient(145deg, #14142a 0%, #1a1030 100%);
    border: 1px solid #2e2060;
    border-radius: 16px;
    padding: 2rem 1.5rem;
    text-align: center;
}

.score-label {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #7c6af7;
    margin-bottom: 0.5rem;
}

.score-number {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 4rem;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 0.25rem;
}

.score-sub {
    font-size: 0.75rem;
    color: #5a5a7a;
}

/* Score colour tiers */
.score-high  { color: #34d399; }
.score-mid   { color: #fbbf24; }
.score-low   { color: #f87171; }

/* ── Gap pills ── */
.gap-pill {
    display: inline-block;
    background: rgba(248, 113, 113, 0.1);
    border: 1px solid rgba(248, 113, 113, 0.25);
    color: #f87171;
    font-size: 0.78rem;
    font-weight: 500;
    padding: 4px 12px;
    border-radius: 20px;
    margin: 3px 3px 3px 0;
}

/* ── Result sections ── */
.result-section {
    background: #12121e;
    border: 1px solid #1e1e30;
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.result-section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: #d0d0e8;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── Project card ── */
.project-title-pill {
    background: rgba(124,106,247,0.12);
    border: 1px solid rgba(124,106,247,0.25);
    color: #a78bfa;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 1rem;
    display: inline-block;
}

.tech-chip {
    display: inline-block;
    background: #1a1a2e;
    border: 1px solid #2a2a45;
    color: #60d4f7;
    font-size: 0.75rem;
    font-weight: 500;
    padding: 3px 10px;
    border-radius: 6px;
    margin: 2px 3px 2px 0;
    font-family: 'Space Grotesk', sans-serif;
}

.roadmap-step {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid #1a1a2a;
    font-size: 0.875rem;
    color: #a0a0c0;
    line-height: 1.5;
}

.roadmap-step:last-child { border-bottom: none; }

.step-num {
    flex-shrink: 0;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: rgba(124,106,247,0.15);
    border: 1px solid rgba(124,106,247,0.3);
    color: #7c6af7;
    font-size: 0.7rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* ── Outreach box ── */
.outreach-box {
    background: #0d0d18;
    border: 1px solid #2a2a40;
    border-radius: 10px;
    padding: 1.2rem;
    font-size: 0.875rem;
    color: #b0b0cc;
    line-height: 1.7;
    font-family: 'Inter', sans-serif;
    white-space: pre-wrap;
}

/* ── Divider ── */
.custom-divider {
    border: none;
    border-top: 1px solid #1e1e2e;
    margin: 2rem 0;
}

/* ── Info box ── */
.info-callout {
    background: rgba(96, 212, 247, 0.06);
    border: 1px solid rgba(96, 212, 247, 0.18);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    font-size: 0.85rem;
    color: #60d4f7;
}

/* ── Expander ── */
div[data-testid="stExpander"] {
    background: #12121e !important;
    border: 1px solid #1e1e30 !important;
    border-radius: 12px !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #7c6af7 !important; }
</style>
""", unsafe_allow_html=True)  # ← BUG FIX: was unsafe_allowed_with_html


# ─── Hero ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-eyebrow">⚡ AI-Powered · Graduate Edition</div>
    <h1 class="hero-title">Your career gap is a<br><span>solvable engineering problem.</span></h1>
    <p class="hero-sub">
        Drop your CV and a job posting. The pipeline identifies your skill gaps,
        builds you a proof project, and drafts your outreach — all in one pass.
    </p>
</div>
""", unsafe_allow_html=True)


# ─── API key ─────────────────────────────────────────────────────────────────
if "GEMINI_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.markdown("""
    <div class="info-callout">
        ⚠️  No <code>GEMINI_API_KEY</code> found in Streamlit Secrets.
        Add it via <b>Settings → Secrets</b> in your Streamlit Cloud dashboard.
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─── Input columns ────────────────────────────────────────────────────────────
col1, spacer, col2 = st.columns([1, 0.05, 1])

with col1:
    st.markdown('<div class="step-label">Step 01 — Target Role</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Job Description</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-sub">Paste the posting text or upload a screenshot of the listing.</div>', unsafe_allow_html=True)

    input_method = st.radio(
        "Input method",
        ["Paste job text", "Upload screenshot"],
        label_visibility="collapsed"
    )

    job_payload = None
    is_image_input = False

    if input_method == "Paste job text":
        job_payload = st.text_area(
            "Job description",
            height=200,
            placeholder="Paste the full job posting here — company name, role, requirements...",
            label_visibility="collapsed"
        )
    else:
        uploaded_screenshot = st.file_uploader(
            "Upload screenshot",
            type=["png", "jpg", "jpeg"],
            label_visibility="collapsed"
        )
        if uploaded_screenshot:
            job_payload = Image.open(uploaded_screenshot)
            is_image_input = True
            st.image(job_payload, caption="Job posting screenshot", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="step-label">Step 02 — Your CV</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Resume Upload</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-sub">PDF format only. Text is extracted and never stored.</div>', unsafe_allow_html=True)

    uploaded_cv = st.file_uploader(
        "Upload CV",
        type=["pdf"],
        label_visibility="collapsed"
    )

    if uploaded_cv:
        st.markdown(f"""
        <div style="margin-top:1rem; background:#0d0d18; border:1px solid #2a2a40;
                    border-radius:10px; padding:12px 16px; font-size:0.8rem; color:#7c6af7;">
            ✓ &nbsp;<b style="color:#a78bfa">{uploaded_cv.name}</b>
            <span style="color:#5a5a7a; margin-left:8px;">ready for analysis</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ─── Analyse button ───────────────────────────────────────────────────────────
st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

both_ready = uploaded_cv is not None and job_payload is not None

if not both_ready:
    missing = []
    if not uploaded_cv:    missing.append("CV PDF")
    if not job_payload:    missing.append("job description")
    st.markdown(f"""
    <div class="info-callout">
        💡  Still waiting for: <b>{" and ".join(missing)}</b>.
        Upload both inputs above to unlock the analysis.
    </div>
    """, unsafe_allow_html=True)

_, btn_col, _ = st.columns([1, 1, 1])
with btn_col:
    run = st.button(
        "⚡ Run Career Analysis",
        use_container_width=True,
        type="primary",
        disabled=not both_ready
    )


# ─── Pipeline execution ───────────────────────────────────────────────────────
if run and both_ready:

    with st.spinner("Running pipeline — extracting CV, matching against role, synthesising gaps..."):

        # BUG FIX: or "" prevents crash when extract_text() returns None (scanned pages)
        with pdfplumber.open(uploaded_cv) as pdf:
            cv_text = "".join(page.extract_text() or "" for page in pdf.pages)

        if not cv_text.strip():
            st.error("Could not extract text from your PDF. It may be a scanned image — try a text-based CV export.")
            st.stop()

        system_prompt = """You are a senior technical career advisor specialising in graduate hiring.
Analyse the candidate's resume against the job description and return ONLY valid JSON with this exact schema:

{
  "match_score": <integer 0-100>,
  "match_verdict": "<one of: Strong Match | Moderate Match | Needs Work>",
  "missing_technical_skills": ["<skill>", ...],
  "candidate_strengths": ["<strength>", ...],
  "personalized_project": {
    "project_title": "<business-framed title, not a tutorial name>",
    "business_problem": "<one sentence — what real problem this solves>",
    "technical_stack": ["<tool>", ...],
    "step_by_step_guide": ["<step 1>", "<step 2>", "<step 3>"],
    "github_tags": ["<tag>", ...]
  },
  "linkedin_outreach_template": "<professional 4-sentence message targeting an internal engineer or hiring manager>",
  "interview_questions": [
    {"question": "<question>", "why_asked": "<what skill/trait it probes>"},
    {"question": "<question>", "why_asked": "<what skill/trait it probes>"},
    {"question": "<question>", "why_asked": "<what skill/trait it probes>"}
  ]
}

Rules:
- match_score must reflect genuine gap analysis, not flattery
- project_title must be framed as a business simulation, not a learning exercise
- linkedin_outreach_template must NOT start with 'I am' or 'Excited to share'
- Return ONLY the JSON object, no markdown fences, no preamble"""

        user_content = f"Candidate Resume:\n{cv_text}\n\n"

        if is_image_input:
            contents = [
                f"{system_prompt}\n\n{user_content}Job description is in the attached image.",
                job_payload
            ]
        else:
            contents = [f"{system_prompt}\n\n{user_content}Job Description:\n{job_payload}"]

        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.15
                )
            )
            data = json.loads(response.text)

        except json.JSONDecodeError:
            st.error("The AI returned malformed JSON. Try re-running — this is usually a transient issue.")
            st.stop()
        except Exception as e:
            st.error(f"API error: {e}")
            st.stop()

    # ── Results header ──────────────────────────────────────────────────────
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    st.markdown('<div class="step-label">Step 03 — Analysis Results</div>', unsafe_allow_html=True)

    score = data.get("match_score", 0)
    verdict = data.get("match_verdict", "")
    score_class = "score-high" if score >= 70 else ("score-mid" if score >= 45 else "score-low")

    # ── Top row: score + gaps + strengths ────────────────────────────────────
    top_left, top_right = st.columns([1, 2], gap="large")

    with top_left:
        st.markdown(f"""
        <div class="score-card">
            <div class="score-label">Fit alignment</div>
            <div class="score-number {score_class}">{score}%</div>
            <div style="font-size:0.85rem;font-weight:600;color:#8888a8;margin-top:4px;">{verdict}</div>
        </div>
        """, unsafe_allow_html=True)

    with top_right:
        gaps = data.get("missing_technical_skills", [])
        strengths = data.get("candidate_strengths", [])

        st.markdown('<div class="result-section" style="margin-bottom:0.75rem">', unsafe_allow_html=True)
        st.markdown('<div class="result-section-title">⚠️ Skill gaps identified</div>', unsafe_allow_html=True)
        if gaps:
            pills = "".join(f'<span class="gap-pill">{g}</span>' for g in gaps)
            st.markdown(pills, unsafe_allow_html=True)
        else:
            st.markdown('<span style="color:#5a5a7a;font-size:0.85rem;">No critical gaps detected.</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        st.markdown('<div class="result-section-title">✅ Your strengths</div>', unsafe_allow_html=True)
        if strengths:
            for s in strengths:
                st.markdown(f'<div style="font-size:0.85rem;color:#a0a0c0;padding:3px 0;">· {s}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    # ── Bottom row: project + outreach ───────────────────────────────────────
    proj_col, out_col = st.columns(2, gap="large")

    with proj_col:
        project = data.get("personalized_project", {})
        stack = project.get("technical_stack", [])
        steps = project.get("step_by_step_guide", [])
        tags  = project.get("github_tags", [])

        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        st.markdown('<div class="result-section-title">🛠️ Proof project brief</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="project-title-pill">{project.get("project_title","")}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:0.82rem;color:#6a6a8a;margin-bottom:1rem;">{project.get("business_problem","")}</div>', unsafe_allow_html=True)

        if stack:
            chips = "".join(f'<span class="tech-chip">{t}</span>' for t in stack)
            st.markdown(f'<div style="margin-bottom:1rem;">{chips}</div>', unsafe_allow_html=True)

        for i, step in enumerate(steps, 1):
            st.markdown(f"""
            <div class="roadmap-step">
                <div class="step-num">{i}</div>
                <div>{step}</div>
            </div>
            """, unsafe_allow_html=True)

        if tags:
            tag_str = " ".join(f"#{t}" for t in tags)
            st.markdown(f'<div style="margin-top:1rem;font-size:0.75rem;color:#5a5a7a;">{tag_str}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with out_col:
        outreach = data.get("linkedin_outreach_template", "")
        interview_qs = data.get("interview_questions", [])

        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        st.markdown('<div class="result-section-title">📨 LinkedIn outreach draft</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="outreach-box">{outreach}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if interview_qs:
            st.markdown('<div class="result-section">', unsafe_allow_html=True)
            st.markdown('<div class="result-section-title">🎯 Predicted interview questions</div>', unsafe_allow_html=True)
            for q in interview_qs:
                with st.expander(q.get("question", ""), expanded=False):
                    st.markdown(f"""
                    <div style="font-size:0.82rem;color:#8888a8;padding:4px 0;">
                        <b style="color:#7c6af7;">Why they ask it:</b>&nbsp;{q.get("why_asked","")}
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
