import streamlit as st
import requests
import json

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"
API_ENDPOINT = f"{API_BASE_URL}/ask"

st.set_page_config(page_title="AutoMedRAG", layout="wide", initial_sidebar_state="expanded")

# Initialize session state for report text
if "report_text" not in st.session_state:
    st.session_state.report_text = ""

# Initialize session state for research questions (kept separate)
if "quick_research_results" not in st.session_state:
    st.session_state.quick_research_results = []

# Sidebar
with st.sidebar:
    st.title("⚙️ AutoMedRAG Settings")
    api_url = st.text_input("API URL", value=API_ENDPOINT)
    st.markdown("---")
    
    # Check API connection
    try:
        health = requests.get(f"{API_BASE_URL}/", timeout=2)
        if health.status_code == 200:
            st.success("✅ Backend Connected")
        else:
            st.warning("⚠️ Backend Unresponsive")
    except:
        st.error("❌ Backend Offline")
    
    st.markdown("""
    ### About AutoMedRAG
    Retrieve medical papers from PubMed and get evidence-based answers using AI.
    
    **Pipeline:**
    1. Search PubMed for relevant papers
    2. Hybrid retrieval (semantic + keyword)
    3. Re-rank by relevance
    4. Generate AI answer
    """)

# Main interface
st.title("🏥 AutoMedRAG")
st.subheader("Clinical Evidence Assistant")
st.markdown("*Powered by PubMed + AI + Hybrid Search*")

# Create tabs for different search modes
tab1, tab2 = st.tabs(["⚡ Quick Research", "📄 Medical Reports"])

with tab1:
    st.markdown("### Quick Research (Independent Searches)")
    st.markdown("_Each search is independent - no context mixing between queries_")
    
    # Show previous quick research results
    if st.session_state.quick_research_results:
        st.markdown("**Recent Results:**")
        for idx, result in enumerate(st.session_state.quick_research_results):
            with st.expander(f"📊 Result {idx+1}: {result['question'][:50]}...", expanded=True):
                st.write(f"**Q:** {result['question']}")
                st.info(f"**A:** {result['answer']}")
                if result.get("papers"):
                    with st.expander(f"📚 {len(result['papers'])} papers found", expanded=False):
                        for paper_idx, paper in enumerate(result["papers"], 1):
                            st.write(f"**{paper_idx}. {paper['title']}**")
                            st.caption(f"{paper['abstract'][:200]}...")
        st.markdown("---")
    
    query = st.text_area(
        "📋 Enter your medical question:",
        placeholder="e.g., What are the latest treatments for type 2 diabetes?",
        height=100,
        key="query_quick"
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        search_button = st.button("🔍 Search", use_container_width=True, key="btn_quick")

    if search_button and query:
        with st.spinner("🔄 Searching medical literature..."):
            try:
                # NO history - independent search
                response = requests.post(
                    api_url,
                    json={"question": query, "history": []},
                    timeout=60
                )

                if response.status_code == 200:
                    data = response.json()

                    # Store result separately
                    st.session_state.quick_research_results.append({
                        "question": query,
                        "answer": data["answer"],
                        "papers": data.get("papers", [])
                    })
                    
                    st.rerun()

                else:
                    st.error(f"❌ API Error {response.status_code}")
                    st.code(response.text)

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend API")
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

with tab2:
    st.markdown("### 📄 Medical Report Analyzer")
    st.markdown("Upload your medical reports to get AI-powered summaries and analysis")

    uploaded_file = st.file_uploader(
        "Upload a medical report (PDF, DOCX, or TXT)",
        type=["pdf", "docx", "txt"],
        key="report_uploader"
    )

    if uploaded_file is not None:
        with st.spinner(f"📖 Analyzing {uploaded_file.name}..."):
            try:
                # Prepare file for upload to backend
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                
                response = requests.post(
                    f"{API_BASE_URL}/summarize-report",
                    files=files,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Store the actual extracted report text from backend response
                    if result.get("report_text"):
                        st.session_state.report_text = result["report_text"]
                    else:
                        # Fallback for older versions
                        file_content = uploaded_file.read()
                        if uploaded_file.name.endswith('.txt'):
                            st.session_state.report_text = file_content.decode('utf-8', errors='ignore')
                        else:
                            st.session_state.report_text = "[Binary file]"
                    
                    st.success("✅ Report Analyzed Successfully!")
                    
                    # Display summary
                    with st.expander("📋 Report Summary", expanded=True):
                        st.write(result["summary"])
                    
                    # Display key sections
                    if result.get("key_sections"):
                        st.markdown("#### 🔍 Key Medical Findings")
                        st.markdown("The AI has extracted the most important information from your report:")
                        
                        key_sections = result["key_sections"]
                        
                        # Create columns for better layout
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if key_sections.get("diagnoses"):
                                st.markdown("**🏥 Diagnoses** *(Medical conditions identified)*")
                                if key_sections["diagnoses"]:
                                    for diagnosis in key_sections["diagnoses"][:5]:
                                        st.write(f"• {diagnosis}")
                                else:
                                    st.write("No diagnoses found in report")
                            
                            if key_sections.get("medications"):
                                st.markdown("**💊 Medications** *(Drugs prescribed or being taken)*")
                                if key_sections["medications"]:
                                    for med in key_sections["medications"][:5]:
                                        st.write(f"• {med}")
                                else:
                                    st.write("No medications found in report")
                        
                        with col2:
                            if key_sections.get("procedures"):
                                st.markdown("**🔬 Procedures** *(Tests or treatments performed)*")
                                if key_sections["procedures"]:
                                    for proc in key_sections["procedures"][:5]:
                                        st.write(f"• {proc}")
                                else:
                                    st.write("No procedures found in report")
                            
                            if key_sections.get("allergies"):
                                st.markdown("**⚠️ Allergies** *(Substances patient is allergic to)*")
                                if key_sections["allergies"]:
                                    for allergy in key_sections["allergies"][:5]:
                                        st.write(f"• {allergy}")
                                else:
                                    st.write("No allergies found in report")
                    
                else:
                    st.error(f"❌ Error analyzing report: {response.status_code}")
                    st.code(response.text)
            
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to backend API")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    <p>AutoMedRAG v2.0 | Report Analysis Enabled | Disclaimer: Always consult qualified medical professionals</p>
</div>
""", unsafe_allow_html=True)
