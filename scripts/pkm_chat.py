import streamlit as st
from sentence_transformers import SentenceTransformer
import numpy as np
from supabase import create_client, Client
import logging
from datetime import datetime
import openai
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Personal Knowledge Assistant",
    page_icon="🧠",
    layout="wide",   initial_sidebar_state="expanded"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'embedding_model' not in st.session_state:
    st.session_state.embedding_model = None

@st.cache_resource
def load_embedding_model():
    """Load the sentence transformer model"""
    logger.info("Loading embedding model: all-MiniLM-L6-v2...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info(f"Embedding model loaded. Dimension: {model.get_sentence_embedding_dimension()}")
    return model

@st.cache_resource
def init_supabase():
    """Initialize Supabase client"""
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except KeyError as e:
        st.error(f"Please set {e} in .streamlit/secrets.toml")
        st.stop()
    
    return create_client(url, key)

def search_knowledge_base(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Search the knowledge base using vector similarity"""
    
    # Load model if not already loaded
    if st.session_state.embedding_model is None:
        st.session_state.embedding_model = load_embedding_model()
    
    # Generate embedding for query
    embedding = st.session_state.embedding_model.encode([query])[0]
    embedding_list = embedding.tolist()
    
    # Search Supabase
    supabase = init_supabase()
    
    try:
        response = supabase.rpc(
            'match_crawled_pages',
            {
                'query_embedding': embedding_list,
                'match_count': top_k,
                'match_threshold': 0.1
            }
        ).execute()
print(f"Search response: {response}")
print(f"Response data: {response.data}")
print(f"Embedding length: {len(embedding_list)}")
        
        return response.data if response.data else []
        
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        return []

def generate_response(query: str, context_docs: List[Dict[str, Any]]) -> str:
    """Generate AI response using context from knowledge base"""
    
    # Prepare context from retrieved documents
    context_text = ""
    for i, doc in enumerate(context_docs, 1):
        title = doc.get('title', 'Unknown')
        content = doc.get('content', '')[:500]  # Limit content length
        similarity = doc.get('similarity', 0)
        
        context_text += f"\n--- Document {i} (Similarity: {similarity:.3f}) ---\n"
        context_text += f"Title: {title}\n"
        context_text += f"Content: {content}...\n"
    
    # Prepare system prompt
    system_prompt = f"""You are a personal knowledge assistant. Answer the user's question based on the provided context from their personal knowledge base.

CONTEXT FROM KNOWLEDGE BASE:
{context_text}

Instructions:
- Answer based primarily on the provided context
- If the context doesn't fully answer the question, say so
- Be conversational and helpful
- Cite which documents you're referencing when relevant
- If no relevant context is provided, say you don't have information about that topic
"""

    # Check if OpenAI API key is available
    try:
        openai_key = st.secrets["OPENAI_API_KEY"]
    except KeyError:
        openai_key = None
    
    if not openai_key:
        return f"""I found {len(context_docs)} relevant documents in your knowledge base, but I need an OpenAI API key to generate a response. 

Here's what I found:

""" + "\n".join([f"• {doc.get('title', 'Unknown')} (Similarity: {doc.get('similarity', 0):.3f})" for doc in context_docs])

    try:
        # Use OpenAI to generate response
        client = openai.OpenAI(api_key=openai_key)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # More cost-effective option
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        return f"Found {len(context_docs)} relevant documents, but couldn't generate AI response. Error: {str(e)}"

def main():
    # Sidebar
    with st.sidebar:
        st.title("🧠 Settings")
        
        # Knowledge base stats
        st.subheader("Knowledge Base")
        supabase = init_supabase()
        
        try:
            # Get total document count
            count_response = supabase.table('crawled_pages').select('*', count='exact').execute()
            total_docs = count_response.count if hasattr(count_response, 'count') else 0
            st.metric("Total Documents", total_docs)
        except:
            st.metric("Total Documents", "Error loading")
        
        # Search settings
        st.subheader("Search Settings")
        top_k = st.slider("Documents to retrieve", 1, 10, 5)
        
        # Clear chat
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
    
    # Main interface
    st.title("🤖 Personal Knowledge Assistant")
    st.caption("Ask questions about your personal knowledge base")
    
    # Display environment status
    col1, col2, col3 = st.columns(3)
    with col1:
        try:
            supabase_status = "✅" if st.secrets["SUPABASE_URL"] and st.secrets["SUPABASE_KEY"] else "❌"
        except KeyError:
            supabase_status = "❌"
        st.metric("Supabase", supabase_status)
    with col2:
        try:
            openai_status = "✅" if st.secrets["OPENAI_API_KEY"] else "❌"
        except KeyError:
            openai_status = "❌"
        st.metric("OpenAI API", openai_status)
    with col3:
        model_status = "✅" if st.session_state.embedding_model else "⏳"
        st.metric("Embedding Model", model_status)
    
    # Chat interface
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Show sources if available
                if message["role"] == "assistant" and "sources" in message:
                    with st.expander("📚 Sources"):
                        for i, source in enumerate(message["sources"], 1):
                            st.write(f"**{i}. {source.get('title', 'Unknown')}** (Similarity: {source.get('similarity', 0):.3f})")
                            st.write(source.get('content', '')[:200] + "...")
                            st.divider()
    
    # Chat input
    if prompt := st.chat_input("Ask about your knowledge..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Searching knowledge base..."):
                # Search knowledge base
                relevant_docs = search_knowledge_base(prompt, top_k)
                
                if not relevant_docs:
                    response = "I couldn't find any relevant information in your knowledge base for that question."
                    sources = []
                else:
                    # Generate AI response
                    with st.spinner("Generating response..."):
                        response = generate_response(prompt, relevant_docs)
                    sources = relevant_docs
                
                # Display response
                st.markdown(response)
                
                # Show sources
                if sources:
                    with st.expander("📚 Sources"):
                        for i, source in enumerate(sources, 1):
                            st.write(f"**{i}. {source.get('title', 'Unknown')}** (Similarity: {source.get('similarity', 0):.3f})")
                            st.write(source.get('content', '')[:200] + "...")
                            if i < len(sources):
                                st.divider()
        
        # Add assistant message to session state
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response,
            "sources": sources if 'sources' in locals() else []
        })

if __name__ == "__main__":
    main()
