import streamlit as st
import requests
import json

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"
API_ENDPOINT = f"{API_BASE_URL}/ask"

st.set_page_config(page_title="AutoMedRAG", layout="wide", initial_sidebar_state="expanded")

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

# Query input
query = st.text_area(
    "📋 Enter your medical question:",
    placeholder="e.g., What are the latest treatments for type 2 diabetes?",
    height=100
)

col1, col2, col3 = st.columns([1, 2, 2])
with col1:
    search_button = st.button("🔍 Search", use_container_width=True)

if search_button and query:
    with st.spinner("🔄 Searching medical literature..."):
        try:
            response = requests.post(
                api_url,
                json={"question": query},
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()

                # Display answer
                st.markdown("### 📝 Clinical Summary")
                st.info(data["answer"])

                # Display papers
                if data.get("papers") and len(data["papers"]) > 0:
                    st.markdown("### 📚 Source Papers")
                    
                    for idx, paper in enumerate(data["papers"], 1):
                        with st.expander(f"**Paper {idx}:** {paper['title']}", expanded=(idx==1)):
                            st.markdown(f"**Abstract:**\n{paper['abstract']}")
                            
                            cols = st.columns(3)
                            if paper.get("hybrid_score") is not None:
                                cols[0].metric("Hybrid Score", f"{paper['hybrid_score']:.3f}")
                            if paper.get("rerank_score") is not None:
                                cols[1].metric("Rerank Score", f"{paper['rerank_score']:.3f}")
                else:
                    st.warning("⚠️ No papers found for this query.")
            else:
                st.error(f"❌ API Error {response.status_code}")
                st.code(response.text)

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend API")
            st.info("Make sure the backend is running: `uvicorn backend.main:app --reload`")
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. The search might be taking longer than expected.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    <p>AutoMedRAG v1.0 | Disclaimer: Always consult qualified medical professionals</p>
</div>
""", unsafe_allow_html=True)
