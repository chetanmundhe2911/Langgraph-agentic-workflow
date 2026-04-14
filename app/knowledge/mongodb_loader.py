"""
MongoDB PDF Loader
Fetches PDF files from MongoDB (GridFS or regular collection) and extracts text.
"""
import io
import os
from typing import List, Dict, Any, Optional, Tuple
from pypdf import PdfReader
from pymongo import MongoClient
from gridfs import GridFS


def _safe_print(s: str) -> str:
    return s.encode("ascii", "replace").decode("ascii")


class MongoDBPDFLoader:
    """
    Loads PDF documents from MongoDB.
    Supports two storage modes:
      - GridFS (default): standard MongoDB file storage across fs.files / fs.chunks
      - Collection: PDFs stored as binary data in a regular collection field
    """

    def __init__(
        self,
        uri: Optional[str] = None,
        db_name: Optional[str] = None,
        collection_name: Optional[str] = None,
        storage_mode: str = "gridfs",
        file_field: str = "file_data",
        filename_field: str = "filename",
    ):
        """
        Args:
            uri: MongoDB connection string. Falls back to MONGODB_URI env var.
            db_name: Database name. Falls back to MONGODB_DB_NAME env var.
            collection_name: Collection or GridFS bucket name.
                             Falls back to MONGODB_COLLECTION env var.
                             Defaults to "reports" if nothing is set.
            storage_mode: "gridfs" (default) or "collection".
            file_field: Field name holding binary PDF data (collection mode only).
            filename_field: Field name holding the original filename.
        """
        self.uri = uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = db_name or os.getenv("MONGODB_DB_NAME", "premarriage")
        self.collection_name = collection_name or os.getenv("MONGODB_COLLECTION", "reports")
        self.storage_mode = storage_mode.lower()
        self.file_field = file_field
        self.filename_field = filename_field

        self._client: Optional[MongoClient] = None
        self._db = None

    def connect(self) -> None:
        """Establish connection to MongoDB."""
        if self._client is not None:
            return
        print(f"Connecting to MongoDB: {self._mask_uri(self.uri)}")
        self._client = MongoClient(self.uri, serverSelectionTimeoutMS=10000)
        self._db = self._client[self.db_name]
        # Trigger a quick check so connection errors surface early
        self._client.admin.command("ping")
        print(f"Connected to database '{self.db_name}'")

    def close(self) -> None:
        if self._client:
            self._client.close()
            self._client = None
            self._db = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_pdfs(self) -> List[Dict[str, Any]]:
        """
        List available PDF files with metadata (no content downloaded yet).
        Returns list of dicts with keys: filename, _id, upload_date, length.
        """
        self.connect()
        results: List[Dict[str, Any]] = []

        if self.storage_mode == "gridfs":
            fs = GridFS(self._db, collection=self.collection_name)
            for grid_file in fs.find({"filename": {"$regex": r"\.pdf$", "$options": "i"}}):
                results.append({
                    "_id": str(grid_file._id),
                    "filename": grid_file.filename,
                    "upload_date": grid_file.upload_date.isoformat() if grid_file.upload_date else None,
                    "length": grid_file.length,
                })
        else:
            col = self._db[self.collection_name]
            for doc in col.find(
                {self.filename_field: {"$regex": r"\.pdf$", "$options": "i"}},
                {self.filename_field: 1, "upload_date": 1, "updated_at": 1},
            ):
                results.append({
                    "_id": str(doc["_id"]),
                    "filename": doc.get(self.filename_field, "unknown.pdf"),
                    "upload_date": str(doc.get("upload_date") or doc.get("updated_at", "")),
                    "length": 0,
                })

        return results

    def fetch_pdfs(self) -> List[Dict[str, Any]]:
        """
        Download all PDF files and extract text content.
        Returns list of dicts: {filename, content, length, _id, upload_date}.
        """
        self.connect()
        documents: List[Dict[str, Any]] = []

        if self.storage_mode == "gridfs":
            documents = self._fetch_from_gridfs()
        else:
            documents = self._fetch_from_collection()

        return documents

    def get_files_metadata(self) -> List[Dict[str, Any]]:
        """
        Return lightweight metadata suitable for RAG cache validation.
        Uses _id + upload_date as the cache key (replaces local file mtime).
        """
        pdf_list = self.list_pdfs()
        return [
            {
                "filename": p["filename"],
                "mtime": p.get("upload_date", p["_id"]),
            }
            for p in pdf_list
        ]

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fetch_from_gridfs(self) -> List[Dict[str, Any]]:
        fs = GridFS(self._db, collection=self.collection_name)
        results: List[Dict[str, Any]] = []

        for grid_file in fs.find({"filename": {"$regex": r"\.pdf$", "$options": "i"}}):
            filename = grid_file.filename
            print(_safe_print(f"  Downloading from GridFS: {filename}"))
            try:
                pdf_bytes = grid_file.read()
                text = self._extract_text(pdf_bytes, filename)
                if text.strip():
                    results.append({
                        "filename": filename,
                        "content": text,
                        "length": len(text),
                        "_id": str(grid_file._id),
                        "upload_date": grid_file.upload_date.isoformat() if grid_file.upload_date else None,
                    })
                    print(_safe_print(f"  [OK] Extracted {len(text)} characters from {filename}"))
                else:
                    print(_safe_print(f"  [WARN] No text extracted from {filename}"))
            except Exception as e:
                print(_safe_print(f"  [X] Error processing {filename}: {e}"))
        return results

    def _fetch_from_collection(self) -> List[Dict[str, Any]]:
        col = self._db[self.collection_name]
        results: List[Dict[str, Any]] = []

        for doc in col.find({self.filename_field: {"$regex": r"\.pdf$", "$options": "i"}}):
            filename = doc.get(self.filename_field, "unknown.pdf")
            print(_safe_print(f"  Downloading from collection: {filename}"))
            try:
                pdf_bytes = doc.get(self.file_field)
                if pdf_bytes is None:
                    print(_safe_print(f"  [WARN] No binary data in field '{self.file_field}' for {filename}"))
                    continue
                if not isinstance(pdf_bytes, bytes):
                    pdf_bytes = bytes(pdf_bytes)

                text = self._extract_text(pdf_bytes, filename)
                if text.strip():
                    results.append({
                        "filename": filename,
                        "content": text,
                        "length": len(text),
                        "_id": str(doc["_id"]),
                        "upload_date": str(doc.get("upload_date") or doc.get("updated_at", "")),
                    })
                    print(_safe_print(f"  [OK] Extracted {len(text)} characters from {filename}"))
                else:
                    print(_safe_print(f"  [WARN] No text extracted from {filename}"))
            except Exception as e:
                print(_safe_print(f"  [X] Error processing {filename}: {e}"))
        return results

    @staticmethod
    def _extract_text(pdf_bytes: bytes, filename: str) -> str:
        """Extract text from in-memory PDF bytes."""
        reader = PdfReader(io.BytesIO(pdf_bytes))
        pages_text = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages_text)

    @staticmethod
    def _mask_uri(uri: str) -> str:
        """Hide credentials in the URI for safe logging."""
        if "@" in uri:
            scheme_end = uri.find("://") + 3
            at_pos = uri.index("@")
            return uri[:scheme_end] + "***:***" + uri[at_pos:]
        return uri
