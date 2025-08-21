import os
import streamlit as st
import pandas as pd
import json
from parsers.pdf_parser import parse_pdf
from parsers.docx_parser import parse_docx
from core.extractor import extract_name, extract_experience, extract_skills
from core.scorer import compute_score
from core.filter import filter_candidate
from utils.file_handler import save_results

st.set_page_config(page_title="Resume Parser & Filter", layout="wide")

# ---------- SESSION STATE ----------
if "roles" not in st.session_state:
    st.session_state.roles = {}

# ---------- SIDEBAR: ROLE CONFIG ----------
st.sidebar.title("⚙️ Configure Roles")

with st.sidebar.expander("➕ Add / Update Role Config"):
    role_name = st.text_input("Role Name")
    min_exp_role = st.number_input("Minimum Experience (years)", min_value=0, max_value=30, value=2)
    threshold_role = st.number_input("Threshold Score", min_value=0, max_value=100, value=70)

    st.markdown("### Define Skills & Weights (simple input)")
    st.info("Enter skills in format: Python:40, SQL:30, ML:20")

    skills_input = st.text_area("Skills (comma separated)", value="Python:40, SQL:30")

    if st.button("💾 Save Role"):
        if role_name:
            skill_dict = {}
            for item in skills_input.split(","):
                item = item.strip()
                if ":" in item:
                    skill, weight = item.split(":")
                    skill = skill.strip()
                    try:
                        weight = int(weight.strip())
                        if 0 <= weight <= 100:  # validate range
                            skill_dict[skill] = weight
                    except ValueError:
                        continue

            st.session_state.roles[role_name] = {
                "skills": skill_dict,
                "threshold": threshold_role,
                "min_experience": min_exp_role
            }
            st.success(f"Role '{role_name}' saved/updated with {len(skill_dict)} skills")

st.sidebar.write("### Current Roles Configuration")
st.sidebar.json(st.session_state.roles)

# ---------- MAIN SECTION ----------
st.title("📄 Resume Parser & Filtering System")
st.write("Upload resumes (PDF/DOCX), select a role, and process.")

# Upload resumes
uploaded_files = st.file_uploader("Upload Resumes", type=["pdf", "docx"], accept_multiple_files=True)

# Role selection
if st.session_state.roles:
    role_selected = st.selectbox("Select Role", options=list(st.session_state.roles.keys()))
else:
    st.warning("Please configure a role from the sidebar first.")
    role_selected = None

# ---------- PROCESSING ----------
if uploaded_files and role_selected and st.button("🚀 Process Resumes"):
    config = st.session_state.roles[role_selected]
    results = []

    for file in uploaded_files:
        filename = file.name
        text = ""

        if filename.endswith(".pdf"):
            text = parse_pdf(file)
        elif filename.endswith(".docx"):
            text = parse_docx(file)

        name = extract_name(text)
        exp = extract_experience(text)  # extract only from work exp section
        found_skills = extract_skills(text, config["skills"])
        score = compute_score(found_skills)
        status = filter_candidate(exp, config["min_experience"], score, config["threshold"])

        results.append({
            "name": name,
            "file": filename,
            "role": role_selected,
            "experience_years": exp,
            "skills_matched": list(found_skills.keys()),
            "score": score,
            "status": status
        })

    os.makedirs("output", exist_ok=True)
    save_results(results, "output/results.json", "output/results.csv")

    # ---------- DISPLAY RESULTS ----------
    st.success("✅ Processing Complete")
    results_df = pd.DataFrame(results)
    st.dataframe(results_df)

    st.download_button(
        "📥 Download Results (CSV)",
        data=results_df.to_csv(index=False),
        file_name="results.csv",
        mime="text/csv"
    )

    st.download_button(
        "📥 Download Results (JSON)",
        data=json.dumps(results, indent=4),
        file_name="results.json",
        mime="application/json"
    )

    # Summary Chart
    st.markdown("### 📊 Summary")
    summary_chart = results_df["status"].value_counts()
    st.bar_chart(summary_chart)