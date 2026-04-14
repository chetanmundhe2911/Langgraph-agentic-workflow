"""
MongoDBService — Structured CRUD for all 38 IKSCBandhan collections.

Provides:
  - load_candidate_profile(user_id)  → dict of all user-linked collection documents
  - get / insert / update for any collection
  - Agent logging helpers
  - Backward compatible: sits alongside existing MongoDBPDFLoader
"""
import os
import logging
from typing import Optional, Dict, Any, List, Type
from datetime import datetime

try:
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError
except ImportError:
    MongoClient = None  # type: ignore
    PyMongoError = Exception  # type: ignore

from app.models import COLLECTION_MODEL_MAP, MongoModel
from app.models.sessions_logs import AgentLogDocument, OrchestratorSessionDocument

logger = logging.getLogger(__name__)

# Collections that have a user_id foreign key (one document per user)
USER_LINKED_COLLECTIONS = [
    "primary_data",
    "secondary_data",
    "tertiary_data",
    "operational_data",
    "family_data",
    "marriage_data",
    "medical_data",
    "ideal_usecase_data",
    "customer_journey",
    "bandhan_product_context",
    "individual_journey_tracker",
]


class MongoDBService:
    """
    Centralised MongoDB service for all IKSCBandhan collections.
    Uses COLLECTION_MODEL_MAP to validate and parse documents.
    """

    def __init__(
        self,
        uri: Optional[str] = None,
        db_name: Optional[str] = None,
    ):
        if MongoClient is None:
            raise ImportError(
                "pymongo is required for MongoDBService. Install via: pip install pymongo"
            )
        self.uri = uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = db_name or os.getenv("MONGODB_DB_NAME", "premarriage")
        self._client: Optional[MongoClient] = None
        self._db = None

    @property
    def client(self) -> MongoClient:
        if self._client is None:
            self._client = MongoClient(self.uri)
        return self._client

    @property
    def db(self):
        if self._db is None:
            self._db = self.client[self.db_name]
        return self._db

    def close(self):
        if self._client:
            self._client.close()
            self._client = None
            self._db = None

    # ------------------------------------------------------------------
    # Generic CRUD
    # ------------------------------------------------------------------

    def get_collection(self, collection_name: str):
        return self.db[collection_name]

    def find_one(
        self,
        collection_name: str,
        query: dict,
        model_cls: Optional[Type[MongoModel]] = None,
    ) -> Optional[MongoModel]:
        """Find a single document and optionally parse into Pydantic model."""
        doc = self.db[collection_name].find_one(query)
        if doc is None:
            return None
        cls = model_cls or COLLECTION_MODEL_MAP.get(collection_name)
        if cls:
            return cls.from_mongo(doc)
        return doc

    def find_many(
        self,
        collection_name: str,
        query: dict,
        model_cls: Optional[Type[MongoModel]] = None,
        limit: int = 100,
    ) -> list:
        cursor = self.db[collection_name].find(query).limit(limit)
        cls = model_cls or COLLECTION_MODEL_MAP.get(collection_name)
        if cls:
            return [cls.from_mongo(doc) for doc in cursor]
        return list(cursor)

    def insert_one(self, collection_name: str, document: MongoModel) -> str:
        result = self.db[collection_name].insert_one(document.to_mongo())
        return str(result.inserted_id)

    def update_one(
        self,
        collection_name: str,
        query: dict,
        update: dict,
        upsert: bool = False,
    ):
        return self.db[collection_name].update_one(query, update, upsert=upsert)

    # ------------------------------------------------------------------
    # Load full candidate profile (all user-linked collections)
    # ------------------------------------------------------------------

    def load_candidate_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Load all user-linked collection documents for a given user_id.
        Returns a dict keyed by collection name → Pydantic model instance (or None).
        """
        from bson import ObjectId

        profile: Dict[str, Any] = {}

        # Load user document (uses _id)
        try:
            user_query = {"_id": ObjectId(user_id)}
        except Exception:
            user_query = {"_id": user_id}

        profile["user"] = self.find_one("users", user_query)

        # Load all user_id-linked collections
        for coll_name in USER_LINKED_COLLECTIONS:
            try:
                profile[coll_name] = self.find_one(coll_name, {"user_id": user_id})
            except PyMongoError as e:
                logger.warning("Failed to load %s for user %s: %s", coll_name, user_id, e)
                profile[coll_name] = None

        # Load multi-document collections (latest / active)
        profile["reports"] = self.find_many("reports", {"user_id": user_id}, limit=20)
        profile["assessments"] = self.find_many("assessments", {"user_id": user_id}, limit=10)
        profile["counselling_sessions"] = self.find_many(
            "counselling_sessions", {"user_id": user_id}, limit=20
        )
        profile["case_data"] = self.find_many(
            "case_data", {"user_id": user_id, "status": {"$in": ["active", "completed"]}}, limit=10
        )

        return profile

    def load_candidate_profile_as_text(self, user_id: str) -> str:
        """
        Load all structured data and render as a readable text block
        suitable for feeding into agent prompts alongside RAG content.
        """
        profile = self.load_candidate_profile(user_id)
        parts: List[str] = []

        for key, value in profile.items():
            if value is None:
                continue
            if isinstance(value, list):
                if not value:
                    continue
                parts.append(f"\n--- {key.upper()} ({len(value)} records) ---")
                for i, item in enumerate(value[:5]):
                    if hasattr(item, "model_dump"):
                        parts.append(f"  [{i+1}] {_model_to_summary(item)}")
            elif hasattr(value, "model_dump"):
                parts.append(f"\n--- {key.upper()} ---")
                parts.append(_model_to_summary(value))

        return "\n".join(parts) if parts else ""

    # ------------------------------------------------------------------
    # Agent execution logging
    # ------------------------------------------------------------------

    def log_agent_execution(
        self,
        session_id: str,
        user_id: str,
        agent_name: str,
        status: str = "running",
        input_data_sources: Optional[List[str]] = None,
        input_snapshot: Optional[Dict[str, Any]] = None,
        output_result: Optional[Dict[str, Any]] = None,
        model_used: Optional[str] = None,
        tokens_used: Optional[int] = None,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None,
    ) -> str:
        log = AgentLogDocument(
            session_id=session_id,
            user_id=user_id,
            agent_name=agent_name,
            status=status,
            execution_start=datetime.utcnow(),
            input_data_sources=input_data_sources or [],
            input_snapshot=input_snapshot,
            output_result=output_result,
            model_used=model_used,
            tokens_used=tokens_used,
            error_message=error_message,
            duration_ms=duration_ms,
        )
        return self.insert_one("ai_agents_log", log)

    def start_orchestrator_session(
        self,
        user_id: str,
        trigger: str = "user_chat",
        case_id: Optional[str] = None,
    ) -> str:
        session = OrchestratorSessionDocument(
            user_id=user_id,
            case_id=case_id,
            trigger=trigger,
            started_at=datetime.utcnow(),
            status="running",
        )
        return self.insert_one("orchestrator_sessions", session)

    def complete_orchestrator_session(
        self,
        session_id: str,
        status: str = "completed",
        agent_chain: Optional[list] = None,
        final_summary: Optional[str] = None,
    ):
        from bson import ObjectId
        update_data: Dict[str, Any] = {
            "completed_at": datetime.utcnow(),
            "status": status,
        }
        if agent_chain:
            update_data["agent_chain"] = agent_chain
        if final_summary:
            update_data["output.final_summary"] = final_summary

        try:
            query = {"_id": ObjectId(session_id)}
        except Exception:
            query = {"_id": session_id}

        self.update_one("orchestrator_sessions", query, {"$set": update_data})


def _model_to_summary(model: MongoModel, max_depth: int = 2) -> str:
    """Convert a Pydantic model to a compact text summary for prompt injection."""
    data = model.model_dump(exclude_none=True, exclude={"id"})
    lines = []
    for key, val in data.items():
        if isinstance(val, dict):
            nested_parts = [f"{k}: {v}" for k, v in val.items() if v is not None]
            if nested_parts:
                lines.append(f"  {key}: {'; '.join(nested_parts[:10])}")
        elif isinstance(val, list):
            if val:
                preview = val[:5]
                lines.append(f"  {key}: {preview}{'...' if len(val) > 5 else ''}")
        else:
            lines.append(f"  {key}: {val}")
    return "\n".join(lines)
