import os
import glob
import logging
from pathlib import Path
from typing import Optional
from pypdf import PdfReader
from app.knowledge.knowledge_base import CandidateKnowledgeBase

# RAG is required - import will fail if dependencies not installed
from app.knowledge.rag_store import RAGKnowledgeStore

logger = logging.getLogger(__name__)


def _safe_print(s: str) -> str:
    """Encode to ASCII for console output (avoids UnicodeEncodeError on Windows cp1252)."""
    return s.encode("ascii", "replace").decode("ascii")


# ------------------------------------------------------------------
# MongoDB-based loader (primary)
# ------------------------------------------------------------------

def load_knowledge_base_from_mongodb(
    mongodb_uri: Optional[str] = None,
    db_name: Optional[str] = None,
    collection_name: Optional[str] = None,
    storage_mode: str = "gridfs",
    use_rag: bool = True,
) -> CandidateKnowledgeBase:
    """
    Load all PDF reports from MongoDB and index them into the RAG store.

    Connection parameters fall back to environment variables:
        MONGODB_URI, MONGODB_DB_NAME, MONGODB_COLLECTION

    Args:
        mongodb_uri:      MongoDB connection string.
        db_name:          Database name.
        collection_name:  Collection / GridFS bucket name.
        storage_mode:     "gridfs" (default) or "collection".
        use_rag:          Whether to use RAG for intelligent retrieval (default: True).

    Returns:
        CandidateKnowledgeBase with all reports indexed in the RAG store.
    """
    from app.knowledge.mongodb_loader import MongoDBPDFLoader

    loader = MongoDBPDFLoader(
        uri=mongodb_uri,
        db_name=db_name,
        collection_name=collection_name,
        storage_mode=storage_mode,
    )

    try:
        loader.connect()
    except Exception as e:
        print(_safe_print(f"[ERROR] Could not connect to MongoDB: {e}"))
        return CandidateKnowledgeBase(raw_report_content="MongoDB connection failed.")

    # Lightweight metadata for cache validation (no PDF download yet)
    report_files_metadata = loader.get_files_metadata()

    if not report_files_metadata:
        print("No PDF reports found in MongoDB. Using empty base.")
        loader.close()
        return CandidateKnowledgeBase(raw_report_content="No report found in MongoDB.")

    print(f"Found {len(report_files_metadata)} PDF report(s) in MongoDB.")

    if not use_rag:
        # RAG disabled – just download text and return
        documents = loader.fetch_pdfs()
        loader.close()
        combined = "\n\n".join(
            f"\n\n=== REPORT: {d['filename']} ===\n\n{d['content']}" for d in documents
        )
        return CandidateKnowledgeBase(raw_report_content=combined or "No valid report content.")

    # --- RAG path ---
    print("\nUsing RAG (Retrieval Augmented Generation) for intelligent content retrieval...")
    rag_store = RAGKnowledgeStore(model_name="gpt-4o")

    cache_valid = rag_store._can_load_from_cache(report_files_metadata)

    if cache_valid:
        print("[OK] Valid cache found. Attempting to load from cache (skipping PDF download)...")
        try:
            rag_store.load_and_index_report(
                report_content="",
                report_files=report_files_metadata,
                force_reindex=False,
            )
            cached_content = _load_cached_raw_content(rag_store.cache_dir)
            kb = CandidateKnowledgeBase(raw_report_content=cached_content)
            kb.rag_store = rag_store
            print(f"[OK] Loaded RAG index from cache with {len(rag_store.chunks)} chunks.")
            print("[OK] Ready to use – no PDF download required!")
            loader.close()
            return kb
        except Exception as e:
            print(_safe_print(f"[WARN] Error loading from cache: {e}. Will re-index..."))
            import traceback
            print(_safe_print(traceback.format_exc()))

    # Cache miss or invalid – download PDFs from MongoDB
    if not cache_valid:
        print("Cache not found or invalid. Downloading PDFs from MongoDB and creating new index...")
    else:
        print("Cache validation passed but loading failed. Re-indexing from MongoDB PDFs...")

    documents = loader.fetch_pdfs()
    loader.close()

    if not documents:
        print("No valid PDF content found in MongoDB.")
        return CandidateKnowledgeBase(raw_report_content="No valid report content found in MongoDB.")

    all_reports_text = [
        f"\n\n=== REPORT: {d['filename']} ===\n\n{d['content']}" for d in documents
    ]
    combined_text = "\n\n".join(all_reports_text)
    total_length = len(combined_text)
    print(f"\nCombined all reports: {total_length} characters (~{total_length // 4} tokens)")
    print(f"Total reports indexed: {len(documents)}")

    print("Creating vector embeddings (this may take a moment)...")
    rag_store.load_and_index_report(combined_text, report_files=report_files_metadata)

    # Persist raw content for future cache hits
    with open(rag_store.cache_dir / "raw_content.txt", "w", encoding="utf-8") as f:
        f.write(combined_text)

    kb = CandidateKnowledgeBase(raw_report_content=combined_text)
    kb.rag_store = rag_store
    print(f"[OK] RAG store created with {len(documents)} report(s).")
    print("[OK] Agents will retrieve relevant chunks from any report based on user queries.")
    print("[OK] Index cached for faster loading next time.")
    return kb


# ------------------------------------------------------------------
# Local filesystem loader (kept for backward compatibility / offline use)
# ------------------------------------------------------------------

def load_knowledge_base_from_reports(
    report_dir: str = "Report",
    use_rag: bool = True
) -> CandidateKnowledgeBase:
    """
    Loads the knowledge base from ALL PDF reports in the specified directory.
    All reports are indexed into a single RAG store, allowing queries to retrieve
    relevant information from any report based on the user's question.
    
    Args:
        report_dir: Path to the report directory. Can be relative or absolute.
                    If relative, will search from project root.
        use_rag: Whether to use RAG for intelligent content retrieval (default: True)
    
    Returns:
        CandidateKnowledgeBase with all reports indexed in RAG store
    """
    
    # Convert to Path object for easier handling
    report_path = Path(report_dir)
    
    # If it's a relative path, try to find it relative to project root
    if not report_path.is_absolute():
        # Try to find project root by looking for app/ directory
        # Start from current file's directory and go up
        current_file = Path(__file__).resolve()
        search_path = current_file.parent  # app/knowledge
        
        # Go up to find project root (where app/ and Report/ should be)
        for _ in range(3):
            parent = search_path.parent
            # Check if this looks like project root (has app/ and Report/)
            if (parent / "app").exists() and (parent / "Report").exists():
                report_path = parent / report_dir
                break
            search_path = parent
        else:
            # If we didn't find it, try current working directory
            cwd = Path(os.getcwd())
            if (cwd / report_dir).exists():
                report_path = cwd / report_dir
            else:
                # Last resort: use the relative path as-is
                report_path = Path(report_dir)
    
    # Ensure it's absolute
    report_path = report_path.resolve()
    
    # Find all PDF files
    pdf_pattern = str(report_path / "*.pdf")
    pdf_files = glob.glob(pdf_pattern)
    
    if not pdf_files:
        print(_safe_print(f"No PDF reports found in {report_path}. Using empty base."))
        print(_safe_print(f"Searching in: {report_path}"))
        print(_safe_print(f"Directory exists: {report_path.exists()}"))
        if report_path.exists():
            print(_safe_print(f"Contents: {list(report_path.iterdir())[:10]}"))
        return CandidateKnowledgeBase(raw_report_content="No report found.")
    
    print(f"Found {len(pdf_files)} PDF report(s).")
    
    # First, collect file metadata for cache validation (without reading PDFs)
    report_files_metadata = []  # For cache validation
    for pdf_file in pdf_files:
        try:
            pdf_path = Path(pdf_file)
            report_name = pdf_path.name
            mtime = os.path.getmtime(pdf_file)  # Modification time for cache validation
            report_files_metadata.append({
                "filename": report_name,
                "mtime": mtime
            })
        except Exception as e:
            print(_safe_print(f"  [X] Error getting metadata for {Path(pdf_file).name}: {e}"))
            continue
    
    # RAG is required - always use it
    if use_rag:
        print("\nUsing RAG (Retrieval Augmented Generation) for intelligent content retrieval...")
        
        # Create RAG store first to check cache
        rag_store = RAGKnowledgeStore(model_name="gpt-4o")
        
        # Check if we can load from cache (this checks file metadata without reading PDFs)
        cache_valid = rag_store._can_load_from_cache(report_files_metadata)
        
        if cache_valid:
            print("[OK] Valid cache found. Attempting to load from cache (skipping PDF reading)...")
            try:
                # Load from cache - we can pass empty content since we're loading from cache
                # The method will check cache first and return early if successful
                rag_store.load_and_index_report(
                    report_content="",  # Empty since we're loading from cache
                    report_files=report_files_metadata,
                    force_reindex=False
                )
                
                cached_content = _load_cached_raw_content(rag_store.cache_dir)
                kb = CandidateKnowledgeBase(raw_report_content=cached_content)
                kb.rag_store = rag_store
                print(f"[OK] Loaded RAG index from cache with {len(rag_store.chunks)} chunks.")
                print("[OK] Ready to use - no PDF reading required!")
                return kb
            except Exception as e:
                print(_safe_print(f"[WARN] Error loading from cache: {e}. Will re-index from PDFs..."))
                import traceback
                print(_safe_print(traceback.format_exc()))
                # Fall through to re-indexing (cache was invalid or corrupted)
        
        # Cache not available, invalid, or failed to load - need to read PDFs and index
        if not cache_valid:
            print("Cache not found or invalid. Reading PDFs and creating new index...")
        else:
            print("Cache validation passed but loading failed. Re-indexing from PDFs...")
        
        # Load and combine all PDFs
        all_reports_content = []
        all_reports_text = []
        
        for pdf_file in pdf_files:
            try:
                pdf_path = Path(pdf_file)
                report_name = pdf_path.name
                
                print(_safe_print(f"Loading: {report_name}"))
                reader = PdfReader(pdf_file)
                text_content = []
                
                for page in reader.pages:
                    text_content.append(page.extract_text())
                
                report_text = "\n".join(text_content)
                if report_text.strip():  # Only add non-empty reports
                    # Store with metadata about which report it came from
                    all_reports_content.append({
                        "filename": report_name,
                        "content": report_text,
                        "length": len(report_text)
                    })
                    all_reports_text.append(f"\n\n=== REPORT: {report_name} ===\n\n{report_text}")
                    
                    print(_safe_print(f"  [OK] Loaded {len(report_text)} characters from {report_name}"))
            except Exception as e:
                print(_safe_print(f"  [X] Error reading {Path(pdf_file).name}: {e}"))
                continue
        
        if not all_reports_content:
            print("No valid PDF content found in any reports.")
            return CandidateKnowledgeBase(raw_report_content="No valid report content found.")
        
        # Combine all reports into single text
        combined_text = "\n\n".join(all_reports_text)
        total_length = len(combined_text)
        print(f"\nCombined all reports: {total_length} characters (~{total_length//4} tokens)")
        print(f"Total reports indexed: {len(all_reports_content)}")
        
        print("Creating vector embeddings (this may take a moment)...")
        # Index all reports
        rag_store.load_and_index_report(
            combined_text,
            report_files=report_files_metadata
        )
        
        # Save raw content to cache for future use
        cache_dir = rag_store.cache_dir
        with open(cache_dir / "raw_content.txt", "w", encoding="utf-8") as f:
            f.write(combined_text)
        
        # Store RAG store in knowledge base for later retrieval
        kb = CandidateKnowledgeBase(raw_report_content=combined_text)
        kb.rag_store = rag_store  # Store for agent-specific retrieval
        print(f"[OK] RAG store created with {len(all_reports_content)} report(s).")
        print("[OK] Agents will retrieve relevant chunks from any report based on user queries.")
        print(f"[OK] Index cached for faster loading next time.")
        return kb
    else:
        # If RAG is disabled, still store full content (but agents should use RAG)
        print("RAG disabled, but storing full content. Agents should use RAG for retrieval.")
        return CandidateKnowledgeBase(raw_report_content=combined_text)


# ------------------------------------------------------------------
# Shared helpers
# ------------------------------------------------------------------

def _load_cached_raw_content(cache_dir: Path) -> str:
    """Load previously cached raw content text, with graceful fallback."""
    raw_content_path = cache_dir / "raw_content.txt"
    if raw_content_path.exists():
        try:
            with open(raw_content_path, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"[OK] Loaded cached raw content ({len(content)} chars)")
            return content
        except Exception as e:
            print(_safe_print(f"[WARN] Could not load cached raw content: {e}"))
            return "Content loaded from cache (raw content not available)."
    return "Content loaded from cache (raw content not cached)."


# ------------------------------------------------------------------
# Structured MongoDB v5 loader (new — loads alongside PDF/RAG)
# ------------------------------------------------------------------

def enrich_knowledge_base_with_structured_data(
    kb: CandidateKnowledgeBase,
    user_id: str,
    mongodb_uri: Optional[str] = None,
    db_name: Optional[str] = None,
) -> CandidateKnowledgeBase:
    """
    Load structured data from all MongoDB v5 collections for a user
    and attach it to the existing CandidateKnowledgeBase.

    This is additive — it does NOT replace the existing RAG/PDF data.
    If MongoDB is unreachable or the collections are empty, the KB is
    returned unchanged (graceful degradation).

    Args:
        kb:          Existing knowledge base (with RAG already loaded).
        user_id:     MongoDB user _id (string).
        mongodb_uri: Override for MONGODB_URI env var.
        db_name:     Override for MONGODB_DB_NAME env var.

    Returns:
        The same CandidateKnowledgeBase with structured_profile populated.
    """
    try:
        from app.knowledge.mongodb_service import MongoDBService
    except ImportError as e:
        logger.warning("MongoDBService not importable, skipping structured data: %s", e)
        return kb

    try:
        service = MongoDBService(uri=mongodb_uri, db_name=db_name)
        profile = service.load_candidate_profile(user_id)
        service.close()

        # Only set if we actually got data
        has_data = any(v is not None for v in profile.values())
        if has_data:
            kb.structured_profile = profile
            non_none = sum(1 for v in profile.values() if v is not None)
            print(f"[OK] Loaded structured v5 data: {non_none} collections populated for user {user_id}")
        else:
            print(f"[INFO] No structured v5 data found for user {user_id}")

    except Exception as e:
        print(_safe_print(f"[WARN] Could not load structured v5 data: {e}"))
        logger.warning("Structured data loading failed for user %s: %s", user_id, e)

    return kb


def load_full_knowledge_base(
    user_id: Optional[str] = None,
    mongodb_uri: Optional[str] = None,
    db_name: Optional[str] = None,
    collection_name: Optional[str] = None,
    storage_mode: str = "gridfs",
    use_rag: bool = True,
) -> CandidateKnowledgeBase:
    """
    Combined loader: loads PDF reports via existing RAG pipeline AND
    structured v5 data from all MongoDB collections.

    This is the recommended entry point for new code. Existing callers
    of load_knowledge_base_from_mongodb() are unaffected.
    """
    # Step 1: existing PDF/RAG path (unchanged)
    kb = load_knowledge_base_from_mongodb(
        mongodb_uri=mongodb_uri,
        db_name=db_name,
        collection_name=collection_name,
        storage_mode=storage_mode,
        use_rag=use_rag,
    )

    # Step 2: enrich with structured v5 data if user_id is available
    if user_id:
        kb = enrich_knowledge_base_with_structured_data(
            kb,
            user_id=user_id,
            mongodb_uri=mongodb_uri,
            db_name=db_name,
        )

    return kb
