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

# Sidebar for inputs
st.sidebar.header("📁 Upload Channels")

# 1. Job Description Upload
jd_file = st.sidebar.file_uploader("Upload Job Description (.docx)", type=["docx"])

# 2. Dataset Strategy Selection
data_option = st.sidebar.radio(
    "Choose Candidate Data Source:",
    ("Use Sample Dataset", "Upload Custom Dataset (.jsonl / .gz)")
)

uploaded_candidates = None
if data_option == "Upload Custom Dataset (.jsonl / .gz)":
    # Enhanced to dynamically support both raw text and gzip streams
    uploaded_candidates = st.sidebar.file_uploader("Upload Candidates File", type=["jsonl", "gz"])

st.sidebar.markdown("---")
run_pipeline = st.sidebar.button("🚀 Run Ranking Engine", type="primary")

# Main Dashboard View
col1, col2 = st.columns([1, 2])

with col1:
    st.info("### ℹ️ System Blueprint")
    st.markdown("""
    - **Dynamic Parsing:** Extracts keywords, skills, and eligibility requirements directly from the JD.
    - **Score Normalization:** Scales candidate matching indicators onto a standard `0.0 to 1.0` spectrum.
    - **Deterministic Ranking:** Resolves equal score scenarios using structured primary and secondary keys.
    """)
    
    st.markdown("""
    ### 🏗️ Pipeline Architecture
    1. **Parse Job Description:** Extract core data from the `.docx` document.
    2. **Extract Keywords & Experience Signals:** Map baseline requirements dynamically.
    3. **Build Candidate Features:** Align profile structures with extracted target goals.
    4. **Detect Profile Anomalies:** Filter timeline overlaps or experience mismatches.
    5. **Score Candidates:** Calculate individual multi-signal weights.
    6. **Normalize Scores:** Convert final evaluations to a standardized `0.0 to 1.0` range.
    7. **Rank Candidates:** Deterministically sort the evaluated candidates list.
    8. **Export Validated Output:** Generate the final submission-ready data layout.
    """)

with col2:
    if run_pipeline:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        raw_dir = os.path.join(base_dir, "data", "raw")
        output_dir = os.path.join(base_dir, "data", "outputs")
        os.makedirs(raw_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # JD Resolution
        jd_path = os.path.join(raw_dir, "sample_jd.docx")
        if jd_file is not None:
            jd_path = os.path.join(raw_dir, "uploaded_job_description.docx")
            with open(jd_path, "wb") as f:
                f.write(jd_file.getbuffer())
        elif not os.path.exists(jd_path):
            st.error("⚠️ Please upload a Job Description (`.docx`) file or ensure `sample_jd.docx` exists in the repository.")
            st.stop()
            
        # Flexible Candidates Path Allocation
        candidates_path = os.path.join(raw_dir, "sample_candidates.jsonl")
        if data_option == "Upload Custom Dataset (.jsonl / .gz)" and uploaded_candidates is not None:
            file_extension = uploaded_candidates.name.split('.')[-1]
            candidates_path = os.path.join(raw_dir, f"uploaded_candidates.{file_extension}")
            with open(candidates_path, "wb") as f:
                f.write(uploaded_candidates.getbuffer())
        elif data_option == "Upload Custom Dataset (.jsonl / .gz)" and uploaded_candidates is None:
            st.error("⚠️ Please upload a custom `.jsonl` or `.gz` dataset file in the sidebar.")
            st.stop()
        elif not os.path.exists(candidates_path):
            st.error("❌ Sample dataset file missing at `data/raw/sample_candidates.jsonl`!")
            st.stop()
            
        output_path = os.path.join(output_dir, "team_rishita.csv")
        script_path = os.path.join(base_dir, "rank.py")
        
        with st.spinner("Executing pipeline routines and ranking candidates..."):
            try:
                cmd = [
                    sys.executable, script_path,
                    "--candidates", candidates_path,
                    "--jd", jd_path,
                    "--out", output_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                
                if os.path.exists(output_path):
                    df_results = pd.read_csv(output_path)
                    
                    st.success("🎉 Engine Execution Successful!")
                    
                    # Metrics Block
                    m1, m2 = st.columns(2)
                    with m1:
                        st.metric("Total Candidates Ranked", len(df_results))
                    with m2:
                        if "score" in df_results.columns:
                            st.metric("Top Matched Score", f"{df_results['score'].max():.4f}")
                    
                    # Spotlight & Reasoning Engine Integration
                    if not df_results.empty:
                        top_candidate = df_results.iloc[0]
                        cand_id = top_candidate.get('candidate_id', top_candidate.get('id', 'N/A'))
                        cand_score = top_candidate.get('score', 0.0)
                        
                        st.info(f"🏆 **Top Strategic Match:** `{cand_id}` | **Calibrated Score:** `{cand_score}`")
                        
                        # Dynamic Explainable AI Block
                        if "reasoning" in df_results.columns:
                            with st.expander("📝 Top Candidate Match Explanation (XAI)", expanded=True):
                                st.markdown(f"**Justification Trace for `{cand_id}`:**")
                                st.write(top_candidate["reasoning"])
                    
                    # Visual Analytics: Score Distribution Chart
                    if "score" in df_results.columns and not df_results.empty:
                        st.markdown("### 📊 Distribution of Top 20 Candidates Scaling Scores")
                        # Match structural IDs with clean index mapping for charts
                        id_col = 'candidate_id' if 'candidate_id' in df_results.columns else ('id' if 'id' in df_results.columns else None)
                        if id_col:
                            chart_data = df_results.head(20).set_index(id_col)["score"]
                            st.bar_chart(chart_data)
                        else:
                            st.line_chart(df_results["score"].head(20))
                    
                    st.markdown(f"### 📋 Full Engine Table Matrix (Showing Top {min(15, len(df_results))} Rows)")
                    st.dataframe(df_results.head(15), use_container_width=True)
                    
                    # File Downloader
                    with open(output_path, "rb") as file:
                        st.download_button(
                            label="📥 Download Official Validated CSV (team_rishita.csv)",
                            data=file,
                            file_name="team_rishita.csv",
                            mime="text/csv"
                        )
                        
                    # System Execution Logs
                    if result.stdout:
                        with st.expander("⚙️ System Pipeline Output Logs"):
                            st.code(result.stdout)
                else:
                    st.error("❌ Error: Output CSV payload was not generated.")
                    
            except subprocess.CalledProcessError as e:
                st.error("❌ Pipeline Runtime Error:")
                st.code(e.stderr if e.stderr else e.stdout)
            except Exception as ex:
                st.error(f"❌ System Error: {ex}")
    else:
        st.warning("👈 Select input parameters and click 'Run Ranking Engine' to start the sandbox simulation.")