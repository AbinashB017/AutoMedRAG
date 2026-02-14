"""
AutoMedRAG - Streamlit Cloud Entry Point with Chat History
Run as: streamlit run streamlit_app.py
"""
import streamlit as st
import requests
import json

# Initialize session state for mic recording
if "mic_query" not in st.session_state:
    st.session_state.mic_query = ""

# Configuration
API_BASE_URL = st.secrets.get("API_URL", "http://127.0.0.1:8000")
API_ENDPOINT = f"{API_BASE_URL}/ask"

st.set_page_config(page_title="AutoMedRAG", layout="wide", initial_sidebar_state="expanded")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize session state for research questions (kept separate)
if "research_results" not in st.session_state:
    st.session_state.research_results = []

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
    
    # Clear research results button
    if st.button("🗑️ Clear Research Results", use_container_width=True):
        st.session_state.research_results = []
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

# Initialize session state for report text
if "report_text" not in st.session_state:
    st.session_state.report_text = ""

# Main interface
st.title("🏥 AutoMedRAG")
st.subheader("Clinical Evidence Assistant")
st.markdown("*Powered by PubMed + AI + Hybrid Search*")

st.markdown("**Three Ways to Search:**")
st.markdown("1. **📚 Quick Research** - Fast independent searches (no context mixing)")
st.markdown("2. **💬 Conversational** - Build on previous answers with context")
st.markdown("3. **📄 Medical Reports** - Upload and analyze your medical documents")

# Display chat history
if st.session_state.messages:
    st.markdown("### 💬 Conversation History")
    for idx, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            with st.chat_message("user", avatar="🧑‍⚕️"):
                st.write(f"**Q:** {message['content']}")
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.write(f"**A:** {message['answer']}")
                
                # Add read-aloud button
                col_speak, col_papers = st.columns([1, 3])
                with col_speak:
                    if st.button(f"🔊 Read Aloud", key=f"speak_{idx}"):
                        try:
                            from gtts import gTTS
                            import io
                            
                            # Create speech
                            tts = gTTS(message['answer'], lang='en', slow=False)
                            audio_buffer = io.BytesIO()
                            tts.write_to_fp(audio_buffer)
                            audio_buffer.seek(0)
                            
                            st.audio(audio_buffer, format="audio/mp3")
                        except Exception as e:
                            st.error(f"Could not generate speech: {e}")
                
                if message.get("papers"):
                    with st.expander(f"📚 Papers ({len(message['papers'])} found)"):
                        for paper_idx, paper in enumerate(message["papers"], 1):
                            st.write(f"**{paper_idx}. {paper['title']}**")
                            st.caption(paper['abstract'][:200] + "...")
else:
    st.info("💭 No conversation history yet. Ask a question to start!")

st.markdown("---")

# Two separate sections for research: Conversational vs Quick Research
tab1, tab2 = st.tabs(["💬 Conversational Research", "⚡ Quick Research"])

with tab1:
    st.markdown("### Chat-Based Research (with conversation context)")
    st.markdown("Ask follow-up questions and build on previous answers")
    
    if st.session_state.messages:
        st.markdown("**Conversation History:**")
        for idx, message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                with st.chat_message("user", avatar="🧑‍⚕️"):
                    st.write(f"**Q:** {message['content']}")
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(f"**A:** {message['answer']}")
                    
                    # Add read-aloud button
                    col_speak, col_papers = st.columns([1, 3])
                    with col_speak:
                        if st.button(f"🔊 Read Aloud", key=f"speak_conv_{idx}"):
                            try:
                                from gtts import gTTS
                                import io
                                
                                # Create speech
                                tts = gTTS(message['answer'], lang='en', slow=False)
                                audio_buffer = io.BytesIO()
                                tts.write_to_fp(audio_buffer)
                                audio_buffer.seek(0)
                                
                                st.audio(audio_buffer, format="audio/mp3")
                            except Exception as e:
                                st.error(f"Could not generate speech: {e}")
                    
                    if message.get("papers"):
                        with st.expander(f"📚 Papers ({len(message['papers'])} found)"):
                            for paper_idx, paper in enumerate(message["papers"], 1):
                                st.write(f"**{paper_idx}. {paper['title']}**")
                                st.caption(paper['abstract'][:200] + "...")
    else:
        st.info("💭 No conversation yet. Ask your first question!")
    
    st.markdown("---")
    # Query input for conversational research
    st.markdown("### Ask a Follow-up Question")
    query = st.text_area(
        "Enter your medical question or follow-up:",
        placeholder="e.g., What are the latest treatments for type 2 diabetes?",
        height=80,
        key="query_input_conv"
    )
    use_text_query = query

    col1, col2 = st.columns([1, 4])
    with col1:
        search_button = st.button("🔍 Search", use_container_width=True, key="search_conv")

    if search_button and use_text_query:
        with st.spinner("🔄 Searching medical literature..."):
            try:
                # Build history for context
                history = []
                for msg in st.session_state.messages:
                    history.append({
                        "role": msg["role"],
                        "content": msg["content"] if msg["role"] == "user" else msg["answer"]
                    })
                
                # Send query with history FOR CONVERSATIONAL
                payload = {
                    "question": use_text_query,
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
                        "content": use_text_query
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

with tab2:
    st.markdown("### Single Research Query (independent, no history)")
    st.markdown("Each search is independent - results don't mix with other queries")
    
    # Show recent quick research results
    if st.session_state.research_results:
        st.markdown("**Recent Quick Research Results:**")
        for idx, result in enumerate(st.session_state.research_results):
            with st.container(border=True):
                st.write(f"**Q:** {result['question']}")
                st.write(f"**A:** {result['answer']}")
                if result.get("papers"):
                    with st.expander(f"📚 Papers ({len(result['papers'])} found)"):
                        for paper_idx, paper in enumerate(result["papers"], 1):
                            st.write(f"**{paper_idx}. {paper['title']}**")
                            st.caption(paper['abstract'][:200] + "...")
        st.markdown("---")
    
    # Query input for quick research (NO history)
    st.markdown("### Enter Your Research Question")
    quick_query = st.text_area(
        "Search for something specific:",
        placeholder="e.g., Side effects of aspirin for cancer patients",
        height=80,
        key="query_input_quick"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        quick_search_button = st.button("🔍 Search", use_container_width=True, key="search_quick")

    if quick_search_button and quick_query:
        with st.spinner("🔄 Searching medical literature..."):
            try:
                # Send query WITHOUT history for independent research
                payload = {
                    "question": quick_query,
                    "history": []  # NO HISTORY - independent search
                }
                
                response = requests.post(
                    api_url,
                    json=payload,
                    timeout=60
                )

                if response.status_code == 200:
                    data = response.json()
                    
                    # Add to quick research results (NOT to main messages)
                    st.session_state.research_results.append({
                        "question": quick_query,
                        "answer": data["answer"],
                        "papers": data.get("papers", [])
                    })
                    
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

# Report Analysis Section
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
                
# Report Q&A section removed - focus on key findings
            else:
                st.error(f"❌ Error analyzing report: {response.status_code}")
                st.code(response.text)
        
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend API")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    <p>AutoMedRAG v2.0 | Chat History + Report Analysis | Disclaimer: Always consult qualified medical professionals</p>
</div>
""", unsafe_allow_html=True)
