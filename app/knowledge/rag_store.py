"""
RAG (Retrieval Augmented Generation) Store for Knowledge Base
Uses embeddings and vector search to retrieve relevant chunks from PDF reports.
Supports persistent indexing to avoid re-indexing on every run.
"""
import os
import json
import pickle
from typing import List, Optional, Dict, Any
from pathlib import Path
import hashlib

# RAG dependencies are required - fail if not available
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.messages import SystemMessage, HumanMessage


def _safe_print(s: str) -> str:
    """Encode to ASCII for console output (avoids UnicodeEncodeError on Windows cp1252)."""
    return s.encode("ascii", "replace").decode("ascii")


class RAGKnowledgeStore:
    """
    RAG-based knowledge store that chunks PDFs and retrieves relevant sections.
    Supports persistent indexing to avoid re-indexing on every run.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gpt-4o",
        embedding_model: str = "text-embedding-3-small",
        cache_dir: Optional[str] = None
    ):
        """
        Initialize RAG store.
        
        Args:
            api_key: OpenAI API key
            model_name: Model for LLM operations
            embedding_model: Model for embeddings
            cache_dir: Directory to save/load cached vector store (default: .rag_cache in project root)
        """
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required for RAG")
        
        self.api_key = api_key
        self.model_name = model_name
        self.embeddings = OpenAIEmbeddings(api_key=api_key, model=embedding_model)
        self.vector_store = None
        self.chunks = []
        self.llm = ChatOpenAI(model=model_name, temperature=0.3, api_key=api_key)
        
        # Set up cache directory
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            # Default: .rag_cache in project root
            current_file = Path(__file__).resolve()
            # Find project root (where app/ directory is)
            project_root = current_file.parent.parent.parent  # app/knowledge -> app -> project_root
            self.cache_dir = project_root / ".rag_cache"
        
        self.cache_dir.mkdir(exist_ok=True)
        self.index_path = self.cache_dir / "faiss_index"
        self.metadata_path = self.cache_dir / "index_metadata.json"
        
        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,  # ~500 tokens per chunk
            chunk_overlap=200,  # Overlap to preserve context
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def load_and_index_report(
        self, 
        report_content: str,
        report_files: Optional[List[Dict[str, Any]]] = None,
        force_reindex: bool = False
    ) -> None:
        """
        Load report content, chunk it, and create vector embeddings.
        Tries to load from cache if available and up-to-date.
        
        Args:
            report_content: Full text content from PDF(s)
            report_files: Optional list of dicts with 'filename' and 'mtime' for cache validation
            force_reindex: Force re-indexing even if cache exists
        """
        # Try to load from cache first
        if not force_reindex and self._can_load_from_cache(report_files):
            print("Loading RAG index from cache...")
            try:
                self.vector_store = FAISS.load_local(
                    str(self.index_path),
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                # Load chunks metadata
                if (self.cache_dir / "chunks.pkl").exists():
                    with open(self.cache_dir / "chunks.pkl", "rb") as f:
                        self.chunks = pickle.load(f)
                print(f"[OK] Loaded cached index with {len(self.chunks)} chunks")
                return
            except Exception as e:
                print(_safe_print(f"[WARN] Error loading cache: {e}. Re-indexing..."))
        
        # Index from scratch
        print(f"Chunking report content ({len(report_content)} chars)...")
        
        # Split into chunks
        self.chunks = self.text_splitter.split_text(report_content)
        print(f"Created {len(self.chunks)} chunks")
        
        # Create vector store from chunks
        print("Creating vector embeddings (this may take a moment)...")
        self.vector_store = FAISS.from_texts(
            texts=self.chunks,
            embedding=self.embeddings
        )
        print("Vector store created successfully")
        
        # Save to cache
        self._save_to_cache(report_files)
    
    def _can_load_from_cache(self, report_files: Optional[List[Dict[str, any]]] = None) -> bool:
        """
        Check if cached index exists and is still valid.
        
        Args:
            report_files: List of dicts with 'filename' and 'mtime' for validation
        
        Returns:
            True if cache is valid and can be loaded
        """
        # Check if cache files exist
        if not self.index_path.exists() or not self.metadata_path.exists():
            return False
        
        # If no report_files provided, assume cache is valid (user can force reindex)
        if not report_files:
            return True
        
        # Load metadata and check if reports match
        try:
            with open(self.metadata_path, 'r') as f:
                cached_metadata = json.load(f)
            
            # Check if same number of files
            cached_files = cached_metadata.get('files', [])
            if len(cached_files) != len(report_files):
                print(_safe_print(f"Cache mismatch: {len(cached_files)} files in cache, {len(report_files)} files now"))
                return False
            
            # Check if files and modification times match
            cached_dict = {f['filename']: f['mtime'] for f in cached_files}
            for report_file in report_files:
                filename = report_file.get('filename', '')
                mtime = report_file.get('mtime', 0)
                if filename not in cached_dict or cached_dict[filename] != mtime:
                    print(_safe_print(f"Cache mismatch: {filename} has been modified"))
                    return False
            
            return True
        except Exception as e:
            print(_safe_print(f"Error checking cache metadata: {e}"))
            return False
    
    def _save_to_cache(self, report_files: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Save vector store and metadata to cache.
        
        Args:
            report_files: List of dicts with 'filename' and 'mtime' for metadata
        """
        try:
            print("Saving RAG index to cache...")
            
            # Save FAISS index
            self.vector_store.save_local(str(self.index_path))
            
            # Save chunks
            with open(self.cache_dir / "chunks.pkl", "wb") as f:
                pickle.dump(self.chunks, f)
            
            # Save metadata
            metadata = {
                "embedding_model": "text-embedding-3-small",
                "chunk_size": 2000,
                "chunk_overlap": 200,
                "num_chunks": len(self.chunks),
                "files": report_files or []
            }
            
            with open(self.metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(_safe_print(f"[OK] Index cached to {self.cache_dir}"))
        except Exception as e:
            print(_safe_print(f"[WARN] Could not save cache: {e}"))
    
    def get_relevant_content(
        self,
        query: str,
        agent_domain: str,
        max_chunks: int = 10,
        max_tokens: int = 15000
    ) -> str:
        """
        Retrieve relevant chunks from the report based on query and agent domain.
        
        Args:
            query: User query or analysis request
            agent_domain: Domain of the agent (e.g., "behaviour_psychology", "health_wellness")
            max_chunks: Maximum number of chunks to retrieve
            max_tokens: Maximum tokens for returned content (~4 chars per token)
        
        Returns:
            Relevant report content as a string
        """
        if not self.vector_store:
            return "No report content indexed."
        
        # Enhance query with domain-specific keywords
        domain_keywords = self._get_domain_keywords(agent_domain)
        enhanced_query = f"{query} {domain_keywords}"
        
        # Retrieve relevant chunks
        try:
            docs = self.vector_store.similarity_search(
                enhanced_query,
                k=max_chunks
            )
            
            # Combine chunks
            relevant_content = "\n\n".join([doc.page_content for doc in docs])
            
            # If still too long, use LLM to summarize the retrieved chunks
            estimated_tokens = len(relevant_content) // 4
            if estimated_tokens > max_tokens:
                print(_safe_print(f"Retrieved content too large ({estimated_tokens} tokens). Summarizing..."))
                relevant_content = self._summarize_chunks(relevant_content, max_tokens)
            
            return relevant_content
            
        except Exception as e:
            print(_safe_print(f"Error retrieving content: {e}"))
            # Fallback: return first few chunks
            return "\n\n".join(self.chunks[:5])
    
    def _get_domain_keywords(self, agent_domain: str) -> str:
        """Get domain-specific keywords to improve retrieval."""
        keyword_map = {
            "behaviour_psychology": "RRI PRI AntarBahya DISC 7WPD personality behavior communication emotional",
            "career_profession": "career job profession employment salary income work stress ambition",
            "medical_lifestyle": "medical health condition treatment medication chronic disease",
            "health_wellness": "health wellness diet exercise fitness smoking addiction HRI",
            "family_dynamics": "family parents siblings relationships family values culture",
            "character_values": "values ethics integrity morals character habits hobbies",
            "education_readiness": "education qualification learning academic study",
            "social_philosophy": "social beliefs gender roles equality culture society",
            "hygiene_lifestyle": "hygiene cleanliness routine lifestyle habits grooming",
            "life_philosophy": "purpose meaning worldview philosophy life direction",
            "religious_values": "religion faith spiritual beliefs religious practices",
            "political_alignment": "political politics ideology beliefs civic values"
        }
        return keyword_map.get(agent_domain, "")
    
    def _summarize_chunks(self, content: str, max_tokens: int) -> str:
        """Summarize retrieved chunks if they're too long."""
        try:
            summary_prompt = f"""Summarize the following report sections, preserving ALL critical information:
- Assessment scores and numbers
- Key findings
- Important metrics
- Risk indicators

Target: ~{max_tokens * 4} characters.

Content:
{content[:40000]}  # Limit input size
"""
            
            messages = [
                SystemMessage(content="You are an expert at summarizing report sections while preserving critical data."),
                HumanMessage(content=summary_prompt)
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            print(_safe_print(f"Error summarizing chunks: {e}"))
            # Fallback: truncate
            max_chars = max_tokens * 4
            if len(content) > max_chars:
                return content[:max_chars//2] + "\n\n[... truncated ...]\n\n" + content[-max_chars//2:]
            return content
    
    def get_summary_for_agent(self, agent_domain: str, user_query: str = "") -> str:
        """
        Get a focused summary for a specific agent domain.
        
        Args:
            agent_domain: The domain of the agent
            user_query: Optional user query to further focus retrieval
        
        Returns:
            Domain-specific report content
        """
        if not self.vector_store:
            return "No report content available."
        
        # Create domain-specific query
        query = user_query or f"Analyze {agent_domain.replace('_', ' ')}"
        
        return self.get_relevant_content(
            query=query,
            agent_domain=agent_domain,
            max_chunks=15,  # Get more chunks for comprehensive analysis
            max_tokens=12000  # ~30k chars = ~7.5k tokens
        )
