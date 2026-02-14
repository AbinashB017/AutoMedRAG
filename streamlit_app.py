"""
AutoMedRAG - Streamlit Cloud Entry Point with Chat History
Run as: streamlit run streamlit_app.py
"""
import streamlit as st
import requests
import json

# Configuration
API_BASE_URL = st.secrets.get("API_URL", "http://127.0.0.1:8000")
API_ENDPOINT = f"{API_BASE_URL}/ask"

st.set_page_config(page_title="AutoMedRAG", layout="wide", initial_sidebar_state="expanded")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.title("⚙️ AutoMedRAG Settings")
    
    # Show API URL (editable for testing)
    if st.checkbox("Custom API URL", value=False):
        api_url = st.text_input("API URL", value=API_ENDPOINT)
    else:
        api_url = API_ENDPOINT
    
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
    
    st.markdown("---")
    
    # Clear chat history button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("""
    ### About AutoMedRAG
    Retrieve medical papers from PubMed and get evidence-based answers using AI.
    
    **Pipeline:**
    1. Search PubMed for relevant papers
    2. Hybrid retrieval (semantic + keyword)
    3. Re-rank by relevance
    4. Generate AI answer
    
    **Features:**
    - Chat history maintained
    - Ask follow-up questions
    - View source papers
    
    **Deployment Info:**
    - Backend: FastAPI
    - Frontend: Streamlit Cloud
    - Data Source: PubMed API
    """)

# Main interface
st.title("🏥 AutoMedRAG")
st.subheader("Clinical Evidence Assistant")
st.markdown("*Powered by PubMed + AI + Hybrid Search*")

# Display chat history
st.markdown("### 💬 Conversation")
chat_container = st.container(border=True)

with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user", avatar="🧑‍⚕️"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.write(message["answer"])
                if message.get("papers"):
                    with st.expander("📚 View Source Papers"):
                        for idx, paper in enumerate(message["papers"], 1):
                            with st.expander(f"**Paper {idx}:** {paper['title']}", expanded=False):
                                st.markdown(f"**Abstract:**\n{paper['abstract']}")
                                cols = st.columns(3)
                                if paper.get("hybrid_score") is not None:
                                    cols[0].metric("Hybrid Score", f"{paper['hybrid_score']:.3f}")
                                if paper.get("rerank_score") is not None:
                                    cols[1].metric("Rerank Score", f"{paper['rerank_score']:.3f}")

st.markdown("---")

# Query input
st.markdown("### 📋 Ask a Question")
query = st.text_area(
    "Enter your medical question or follow-up:",
    placeholder="e.g., What are the latest treatments for type 2 diabetes?",
    height=80,
    key="query_input"
)

col1, col2 = st.columns([1, 4])
with col1:
    search_button = st.button("🔍 Search", use_container_width=True)

if search_button and query:
    with st.spinner("🔄 Searching medical literature..."):
        try:
            # Build history for context
            history = []
            for msg in st.session_state.messages:
                history.append({
                    "role": msg["role"],
                    "content": msg["content"] if msg["role"] == "user" else msg["answer"]
                })
            
            # Send query with history
            payload = {
                "question": query,
                "history": history
            }
            
            response = requests.post(
                api_url,
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                
                # Add to chat history
                st.session_state.messages.append({
                    "role": "user",
                    "content": query
                })
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "answer": data["answer"],
                    "papers": data.get("papers", [])
                })
                
                # Clear input and rerun to show new messages
                st.rerun()

            else:
                st.error(f"❌ API Error {response.status_code}")
                st.code(response.text)

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend API")
            st.info(f"Trying to connect to: {api_url}")
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. The search might be taking longer than expected.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    <p>AutoMedRAG v2.0 | Chat History Enabled | Disclaimer: Always consult qualified medical professionals</p>
</div>
""", unsafe_allow_html=True)
