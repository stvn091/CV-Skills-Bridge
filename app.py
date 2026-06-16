import streamlit as st
import json
import pdfplumber
from google import genai
from google.genai import types
from PIL import Image

# 1. Dashboard Layout Page Configuration
st.set_page_config(
    page_title="AI Career Engine", 
    layout="wide", # Widens the app to create a dashboard look instead of a squeezed list
    page_icon="🚀"
)

# Custom minimal CSS styling injections to create border cards and better typography
st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    div[data-testid="stExpander"] {
        border-radius: 10px;
    }
    </style>
""", unsafe_allowed_with_html=True)

# 2. Hero Header Block with Visual Anchor
col_title, col_img = st.columns([2, 1], vertical_alignment="center")

with col_title:
    st.title("🤖 AI-Powered CV & Career Dev Engine")
    st.write("An advanced data pipeline built to bridge professional skill gaps, synthesize software portfolio projects, and construct high-conversion outreach templates.")

with col_img:
    # Embedding a clean, free-to-use tech illustration via remote URL anchor
    st.image("https://unsplash.com", use_container_width=True)

st.write("---")

# 3. Secure Key Retrieval
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
else:
    st.error("Missing Gemini API Key configuration in Streamlit Secrets.")
    st.stop()

# 4. Step 1: Side-by-Side Dual Column Inputs Layout
col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("🎯 Target Job Details")
    input_method = st.radio("Choose how to input the job description:", ["Paste Text From Website", "Upload Screenshot / Image"])

    job_payload = None
    is_image_input = False

    if input_method == "Paste Text From Website":
        job_payload = st.text_area("Paste the job description requirements:", height=180, placeholder="Paste company name, job title, and specifications here...")
    else:
        uploaded_screenshot = st.file_uploader("Upload a screenshot of the job posting", type=["png", "jpg", "jpeg"])
        if uploaded_screenshot is not None:
            job_payload = Image.open(uploaded_screenshot)
            is_image_input = True
            st.image(job_payload, caption="Uploaded Job Screenshot", use_container_width=True)

with col2:
    st.subheader("📤 Upload Resume")
    st.write("Drop your existing graduate CV down below to initialize semantic pipeline evaluation mapping rules.")
    uploaded_cv = st.file_uploader("Upload your CV (PDF format only)", type=["pdf"])

st.write("---")

# 5. Core Match Processing Architecture
if uploaded_cv is not None and job_payload is not None:
    # Big primary processing button anchored in the middle
    _, btn_col, _ = st.columns([1, 1, 1])
    with btn_col:
        submit_btn = st.button("🚀 Initialize Deep Match Analysis", use_container_width=True, type="primary")
        
    if submit_btn:
        with st.spinner("Analyzing alignment metrics across both data targets..."):
            
            # Extract PDF raw strings
            with pdfplumber.open(uploaded_cv) as pdf:
                cv_text = "".join([page.extract_text() for page in pdf.pages])
            
            base_prompt = "You are an expert career advisor. Analyze the provided resume text against the provided job posting information." \
                          "Isolate technical skill gaps, formulate a recovery project with titles, a tech stack, and a 3-step guide, " \
                          "draft a 4-sentence LinkedIn template, and generate a match score."
            
            if is_image_input:
                contents_payload = [
                    f"{base_prompt}\n\nCandidate Resume Text:\n{cv_text}\n\nTarget Job details are inside the attached screenshot image.",
                    job_payload
                ]
            else:
                contents_payload = [
                    f"{base_prompt}\n\nCandidate Resume Text:\n{cv_text}\n\nTarget Job Posting Text:\n{job_payload}"
                ]
            
            try:
                # Call Gemini
                response = client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=contents_payload,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.2 
                    ),
                )
                
                data = json.loads(response.text)
                
                # --- VISUAL DASHBOARD RENDER LAYER ---
                st.subheader("📊 Step 3: Performance Analysis Dashboard")
                
                # Split Results Panel into 2 Clean Columns
                res_col1, res_col2 = st.columns([1, 2], gap="medium")
                
                with res_col1:
                    # Beautiful Metric Card Box via CSS markdown injection
                    score = data.get('match_score', 'N/A')
                    st.markdown(f"""
                        <div class="metric-card">
                            <h3 style="margin:0;color:#6c757d;font-size:16px;">Overall Fit Alignment</h3>
                            <h1 style="margin:10px 0;color:#2e7d32;font-size:48px;">{score}%</h1>
                        </div>
                    """, unsafe_allowed_with_html=True)
                
                with res_col2:
                    st.markdown("**⚠️ Identified Technical Skill Deficiencies:**")
                    gaps = data.get('missing_technical_skills', [])
                    if isinstance(gaps, list):
                        for gap in gaps:
                            st.markdown(f"• :red[{gap}]")
                    else:
                        st.markdown(f"• :red[{gaps}]")
                
                st.write("---")
                
                # Render Strategies Layout Split
                strat_col1, strat_col2 = st.columns(2, gap="large")
                
                with strat_col1:
                    st.markdown("### 🛠️ Recommended Recovery Project")
                    project = data.get("personalized_project", {})
                    
                    st.info(f"**Project Focus:** {project.get('project_title', 'N/A')}")
                    
                    tech_stack = project.get('technical_stack', [])
                    tech_str = ", ".join(tech_stack) if isinstance(tech_stack, list) else tech_stack
                    st.markdown(f"**🔧 Tech Stack Dependencies:** `{tech_str}`")
                    
                    st.markdown("**Execution Roadmap:**")
                    for step in project.get("step_by_step_guide", []):
                        st.write(f"✔️ {step}")
                        
                with strat_col2:
                    st.markdown("### 📨 Context-Aware Inbound Outreach")
                    st.write("The engine synthesized this professional 4-sentence LinkedIn template to target internal engineers:")
                    st.code(data.get("linkedin_outreach_template", "No template generated."), language="text")
                    
            except Exception as e:
                st.error(f"An unexpected API transaction error occurred: {e}")
                
elif uploaded_cv is not None or job_payload is not None:
    # A soft informational callout warning panel
    st.info("💡 Data validation status: Pending. Please upload BOTH target inputs above to activate the processing loop.")
