import streamlit as st
import os
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

# --- BRANDING & PAGE CONFIG SETUP ---
st.set_page_config(
    page_title="VeloRAG // YouTube Context Engine",
    page_icon="⚡",
    layout="wide"
)
st.write("App Loaded Successfully")

# Custom Glassmorphism Visual Layer Injection
st.markdown("""
    <style>
    .stApp { background-color: #0B0E14; color: #E2E8F0; }
    div[data-testid="stSidebarUserContent"] { background-color: #111622; }
    .stButton>button {
        background: linear-gradient(135deg, #00F5A0 0%, #00D9F6 100%) !important;
        color: #0B0E14 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 6px !important;
    }
    div[data-testid="stMetricValue"] { color: #00F5A0 !important; font-family: monospace; }
    </style>
""", unsafe_allow_html=True)

# --- CACHING THE HEAVY EMBEDDING MODEL ---
@st.cache_resource
def load_embedding_model():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

embedding_model = load_embedding_model()

# --- INSTANTIATE LOGICAL STATE CACHES ---
if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_video" not in st.session_state:
    st.session_state.current_video = None

# --- SIDEBAR CONTROL UNIT ---
with st.sidebar:
    st.title("⚙️ Control Matrix")
    video_url = st.text_input("YouTube Target URL", placeholder="https://www.youtube.com/watch?v=...")
    
    with st.expander("🎛️ Tunable Parameters", expanded=False):
        chunk_size = st.slider("Chunk Size", 500, 1500, 1000, 100)
        chunk_overlap = st.slider("Overlap", 0, 200, 20, 10)
        top_k = st.slider("Top K Docs", 1, 6, 4)
    
    trigger_ingest = st.button("BUILD PIPELINE", use_container_width=True)

# Utility parser for extracting ID string patterns cleanly
def get_video_id(url):
    if "v=" in url: return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url: return url.split("youtu.be/")[1].split("?")[0]
    return url

# --- PIPELINE INGESTION EXECUTION ENGINE ---
if trigger_ingest and video_url:
    video_id = get_video_id(video_url)
    st.session_state.current_video = video_id
    
    with st.spinner("⏳ Extracting Context Layers & Creating Vector Space..."):
        try:
            # Step 1: Extract Transcripts
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
            transcript = " ".join(chunk["text"] for chunk in transcript_list)
            
            # Step 2: Split Texts
            splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            chunks = splitter.create_documents([transcript])
            
            # Step 3: Vector Store Generation (In-Memory Isolation for Performance)
            vector_db = Chroma.from_documents(
                documents=chunks,
                embedding=embedding_model
            )
            
            # Step 4: Component Attachment
            retriever = vector_db.as_retriever(search_type="similarity", search_kwargs={"k": top_k})
            
            llm = HuggingFaceEndpoint(
                repo_id="mistralai/Mistral-7B-Instruct-v0.1",
                temperature=0.3,
                max_new_tokens=256,
                huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN")
            )
            
            prompt = PromptTemplate(
                template="You are a helpful assistant.\n\nAnswer ONLY using the given context.\n\nIf the answer is not present in the context, just say: \"I don't know.\"\n\nContext:\n{context}\n\nQuestion:\n{question}",
                input_variables=["context", "question"]
            )
            
            # Formulate Clean LCEL Execution Thread
            st.session_state.rag_chain = (
                {
                    "context": retriever | (lambda docs: "\n\n".join(doc.page_content for doc in docs)),
                    "question": RunnablePassthrough(),
                }
                | prompt
                | llm
            )
            st.success("Ingestion successful! Neural data routing active.")
            
        except TranscriptsDisabled:
            st.error("Extraction Failed: Captions are disabled on this video target.")
        except Exception as e:
            st.error(f"Error compiling RAG context nodes: {e}")

# --- MAIN RUNTIME PANEL INTERFACE ---
st.title("⚡ VeloRAG // YouTube Analytics")
st.caption("Engineered using declarative LangChain Expression Language (LCEL) chains wrapped in an optimized runtime matrix.")

# Metrics Row
m1, m2, m3 = st.columns(3)
with m1: st.metric("System Vector State", "Active" if st.session_state.rag_chain else "Idle")
with m2: st.metric("Dynamic Context Strategy", f"Similarity k={top_k}")
with m3: st.metric("Inference Engine Core", "Mistral-7B")

st.divider()

# Core Visual Split
col_stream, col_chat = st.columns([1, 1.2], gap="large")

with col_stream:
    st.subheader("🎥 Active Video Stream")
    if st.session_state.current_video:
        st.video(f"https://www.youtube.com/watch?v={st.session_state.current_video}")
    else:
        st.info("Provide a video URL in the control sidebar matrix to initialize stream telemetry.")

with col_chat:
    st.subheader("💬 Execution Engine Chat")
    
    # Render Persistent Logs
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # Process Live User Traffic Queries
    if user_query := st.chat_input("Ask a question about the video transcript data...", disabled=not st.session_state.rag_chain):
        with st.chat_message("user"):
            st.markdown(user_query)
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        
        with st.chat_message("assistant"):
            with st.spinner("Traversing multi-vector embedding spaces..."):
                try:
                    response = st.session_state.rag_chain.invoke(user_query)
                    st.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Error executing vector search processing nodes: {e}")