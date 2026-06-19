import streamlit as st
import pandas as pd
import os
import subprocess
import sys

st.set_page_config(
    page_title="Redrob Talent Ranker — Team Rishita",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Redrob Talent Ranker")
st.subheader("Automated Candidate Ranking Engine — Team Rishita")
st.markdown("---")

# ================= SIDEBAR INPUT CHANNELS =================
st.sidebar.header("📁 Upload Channels")

# 1. Job Description Upload
jd_file = st.sidebar.file_uploader("Upload Job Description (.docx)", type=["docx"])

# 2. Dataset Strategy Selection
data_option = st.sidebar.radio(
    "Choose Candidate Data Source:",
    ("Use Sample Dataset", "Upload Custom Dataset")
)

# Har text aur compressed format ko support karne ke liye flexi-uploader
uploaded_candidates = None
if data_option == "Upload Custom Dataset":
    uploaded_candidates = st.sidebar.file_uploader(
        "Upload Candidates File (.jsonl, .json, .txt, .gz)", 
        type=["jsonl", "json", "txt", "gz"]
    )

st.sidebar.markdown("---")
run_pipeline = st.sidebar.button("🚀 Run Ranking Engine", type="primary")
# ==========================================================

# Main Dashboard Layout: Left column for Clean Tabs, Right for execution results
col1, col2 = st.columns([1, 1.8])

with col1:
    tab1, tab2 = st.tabs(["📋 System Blueprint", "🏗️ Pipeline Stages"])
    
    with tab1:
        st.markdown("""
        ### Core Engine Goals
        - **Dynamic Parsing:** Extracts keywords, skills, and eligibility requirements directly from the `.docx`.
        - **Score Normalization:** Scales candidate matching indicators onto a standard `0.0 to 1.0` spectrum.
        - **Deterministic Ranking:** Resolves equal score scenarios using structured primary and secondary keys.
        """)
        
    with tab2:
        st.markdown("""
        ### Processing Pipeline Steps
        1. **Parse Job Description:** Extract raw node strings from text formats.
        2. **Extract Requirements:** Map target title tokens & experience metrics.
        3. **Build Candidate Features:** Structural vector extraction per profile.
        4. **Detect Anomalies:** Clean concurrent profile timelines & overlaps.
        5. **Multi-Signal Scoring:** Weigh distinct token scores into an aggregate matrix.
        6. **Normalize Distributions:** Map values onto a standard `0.0` to `1.0` scale.
        7. **Deterministic Sorting:** Execute cascade sort utilizing tie-breaker arrays.
        8. **Export Validated Layout:** Assemble structured output files cleanly.
        """)

with col2:
    if run_pipeline:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        raw_dir = os.path.join(base_dir, "data", "raw")
        output_dir = os.path.join(base_dir, "data", "outputs")
        os.makedirs(raw_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Resolve Job Description Source
        jd_path = os.path.join(raw_dir, "sample_jd.docx")
        if jd_file is not None:
            jd_path = os.path.join(raw_dir, "uploaded_job_description.docx")
            with open(jd_path, "wb") as f:
                f.write(jd_file.getbuffer())
        elif not os.path.exists(jd_path):
            st.error("⚠️ Please upload a Job Description (`.docx`) file or verify `sample_jd.docx` exists in the repository environment.")
            st.stop()
            
        # 2. Resolve Candidate Profiles Source
        candidates_path = os.path.join(raw_dir, "sample_candidates.jsonl")
        if data_option == "Upload Custom Dataset":
            if uploaded_candidates is not None:
                file_extension = uploaded_candidates.name.split('.')[-1]
                candidates_path = os.path.join(raw_dir, f"uploaded_candidates.{file_extension}")
                with open(candidates_path, "wb") as f:
                    f.write(uploaded_candidates.getbuffer())
            else:
                st.error("⚠️ Please upload a custom tracking dataset file in the sidebar.")
                st.stop()
        elif not os.path.exists(candidates_path):
            st.error("❌ System Error: Default sample dataset file missing at `data/raw/sample_candidates.jsonl`!")
            st.stop()
            
        output_path = os.path.join(output_dir, "team_rishita.csv")
        script_path = os.path.join(base_dir, "rank.py")
        
        with st.spinner("Executing analytical sorting routines and normalizing signal strengths..."):
            try:
                # Execution command enforcing consistent interpreter paths
                cmd = [
                    sys.executable, script_path,
                    "--candidates", candidates_path,
                    "--jd", jd_path,
                    "--out", output_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                
                if os.path.exists(output_path):
                    df_results = pd.read_csv(output_path)
                    
                    st.success("🎉 Pipeline Runtime Execution Successful!")
                    
                    # Core Analytical Metrics Setup
                    m1, m2 = st.columns(2)
                    with m1:
                        st.metric("Total Candidates Evaluated", len(df_results))
                    with m2:
                        if "score" in df_results.columns:
                            st.metric("Peak Distribution Strength", f"{df_results['score'].max():.4f}")
                    
                    # Highlight Block for Elite Match Profile
                    if not df_results.empty:
                        top_candidate = df_results.iloc[0]
                        cand_id = top_candidate.get('candidate_id', top_candidate.get('id', 'N/A'))
                        cand_score = top_candidate.get('score', 0.0)
                        
                        st.info(f"🏆 **Top Designated Match:** `{cand_id}` | **Calibrated Evaluation Score:** `{cand_score}`")
                        
                        # Explainable AI System Block
                        if "reasoning" in df_results.columns:
                            with st.expander("📝 Top Candidate Operational Trace (XAI)", expanded=True):
                                st.markdown(f"**Structural Justification Log for `{cand_id}`:**")
                                st.write(top_candidate["reasoning"])
                    
                    # Vector Analytics Segment: Score Distributions Bar Chart
                    if "score" in df_results.columns and not df_results.empty:
                        st.markdown("### 📊 Target Distribution (Top 20 Profiles Score Matrix)")
                        id_col = 'candidate_id' if 'candidate_id' in df_results.columns else ('id' if 'id' in df_results.columns else None)
                        if id_col:
                            chart_data = df_results.head(20).set_index(id_col)["score"]
                            st.bar_chart(chart_data)
                        else:
                            st.line_chart(df_results["score"].head(20))
                    
                    # Output Stream Matrix
                    st.markdown(f"### 📋 Evaluated Matrix Stream (Showing Top {min(15, len(df_results))} Records)")
                    st.dataframe(df_results.head(15), use_container_width=True)
                    
                    # Safe File Storage Stream Downloader
                    with open(output_path, "rb") as file:
                        st.download_button(
                            label="📥 Download Certified Evaluation CSV (team_rishita.csv)",
                            data=file,
                            file_name="team_rishita.csv",
                            mime="text/csv"
                        )
                        
                    # Standard Console Running Execution logs
                    if result.stdout:
                        with st.expander("⚙️ System Pipeline Routing Terminal Logs"):
                            st.code(result.stdout)
                else:
                    st.error("❌ System Error: Output generation path target validation failed.")
                    
            except subprocess.CalledProcessError as e:
                st.error("❌ System Subprocess Parsing Anomaly Encountered:")
                st.code(e.stderr if e.stderr else e.stdout)
            except Exception as ex:
                st.error(f"❌ Core Structural System Exception: {ex}")
    else:
        st.warning("👈 Adjust validation datasets or configs via the left sidebar controls and activate execution channels.")