"""
Knowledge Base for Multi-Agent Counseling System
Stores different types of data about the candidate for analysis by various specialized agents.

Backward compatible: legacy Pydantic classes are preserved so existing agents continue to work.
New structured MongoDB data (from app.models v5 schema) is available via `structured_profile`
and rendered into prompts via `get_structured_context()`.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

# ── Import v5 schema models for structured MongoDB data ─────────────
from app.models.primary_data import PrimaryDataDocument
from app.models.secondary_data import SecondaryDataDocument
from app.models.tertiary_data import TertiaryDataDocument
from app.models.operational_data import OperationalDataDocument
from app.models.family_data import FamilyDataDocument
from app.models.marriage_data import MarriageDataDocument
from app.models.medical_data import MedicalDataDocument
from app.models.ideal_usecase import IdealUsecaseDocument
from app.models.user import UserDocument


# =====================================================================
# Legacy models (kept as-is for backward compatibility with agents)
# =====================================================================

class PrimaryData(BaseModel):
    """Primary Data: Education and Bio Data"""
    name: str
    age: int
    education_level: str
    qualifications: List[str]
    profession: str
    employment_status: str
    income_range: Optional[str] = None
    location: Optional[str] = None
    bio_summary: Optional[str] = None


class SecondaryData(BaseModel):
    """Secondary Data: Social Media Information"""
    social_media_profiles: Dict[str, str] = Field(default_factory=dict)
    interests: List[str] = Field(default_factory=list)
    hobbies: List[str] = Field(default_factory=list)
    social_activity_patterns: Optional[str] = None
    online_personality_traits: List[str] = Field(default_factory=list)


class FamilyMember(BaseModel):
    """Family Member Information"""
    relationship: str  # father, mother, sibling, etc.
    name: str
    age: Optional[int] = None
    profession: Optional[str] = None
    relationship_quality: Optional[str] = None
    influence_level: Optional[str] = None


class FamilyData(BaseModel):
    """Family Data: Father, Mother, Close Relatives"""
    family_members: List[FamilyMember] = Field(default_factory=list)
    family_values: List[str] = Field(default_factory=list)
    family_background: Optional[str] = None
    cultural_background: Optional[str] = None
    socioeconomic_status: Optional[str] = None


class FriendColleague(BaseModel):
    """Friend or Colleague Information"""
    name: str
    relationship_type: str  # friend, colleague, mentor, etc.
    known_duration: Optional[str] = None
    interaction_frequency: Optional[str] = None
    feedback_summary: Optional[str] = None


class TertiaryData(BaseModel):
    """Tertiary Data: Information from Friends and Colleagues"""
    friends_colleagues: List[FriendColleague] = Field(default_factory=list)
    personality_insights: List[str] = Field(default_factory=list)
    social_behavior_patterns: List[str] = Field(default_factory=list)
    relationship_history: Optional[str] = None


class PsychometricReport(BaseModel):
    """Psychometric Assessment Report"""
    personality_type: Optional[str] = None
    big_five_scores: Optional[Dict[str, float]] = None
    emotional_intelligence_score: Optional[float] = None
    communication_style: Optional[str] = None
    conflict_resolution_style: Optional[str] = None
    relationship_readiness_score: Optional[float] = None
    detailed_report: Optional[str] = None


class MedicalReport(BaseModel):
    """Medical Report"""
    general_health_status: str
    medical_conditions: List[str] = Field(default_factory=list)
    mental_health_status: Optional[str] = None
    fitness_level: Optional[str] = None
    health_notes: Optional[str] = None


class BodyLanguageAnalysis(BaseModel):
    """Body Language Analysis"""
    communication_confidence: Optional[str] = None
    eye_contact_patterns: Optional[str] = None
    posture_analysis: Optional[str] = None
    gesture_patterns: Optional[str] = None
    overall_body_language_summary: Optional[str] = None


class OperationalData(BaseModel):
    """Operational Data: Psychometric, Medical, Body Language"""
    psychometric_report: PsychometricReport
    medical_report: MedicalReport
    body_language: BodyLanguageAnalysis


# =====================================================================
# Domain → Structured collection mapping (used by get_structured_context)
# =====================================================================

AGENT_DOMAIN_DATA_MAP: Dict[str, List[str]] = {
    "behaviour_psychology": ["operational_data", "tertiary_data", "secondary_data"],
    "career_profession": ["primary_data", "secondary_data", "operational_data"],
    "medical_lifestyle": ["medical_data", "operational_data"],
    "health_wellness": ["medical_data", "operational_data", "family_data"],
    "family_dynamics": ["family_data", "marriage_data", "primary_data"],
    "character_values": ["ideal_usecase_data", "tertiary_data", "operational_data", "marriage_data"],
    "education_readiness": ["primary_data", "operational_data"],
    "social_philosophy": ["secondary_data", "tertiary_data", "ideal_usecase_data"],
    "hygiene_lifestyle": ["medical_data", "operational_data", "tertiary_data"],
    "life_philosophy": ["ideal_usecase_data", "operational_data", "family_data"],
    "religious_values": ["ideal_usecase_data", "marriage_data", "family_data"],
    "political_alignment": ["secondary_data", "ideal_usecase_data"],
}


# =====================================================================
# CandidateKnowledgeBase — expanded with structured data
# =====================================================================

class CandidateKnowledgeBase(BaseModel):
    """Complete Knowledge Base for a Candidate.

    Holds:
      - Legacy fields (primary_data, etc.) for backward compat
      - raw_report_content + rag_store for existing RAG pipeline
      - structured_profile: dict of v5 schema Pydantic models loaded from MongoDB
    """
    # Legacy fields (unchanged)
    primary_data: Optional[PrimaryData] = None
    secondary_data: Optional[SecondaryData] = None
    family_data: Optional[FamilyData] = None
    tertiary_data: Optional[TertiaryData] = None
    operational_data: Optional[OperationalData] = None
    raw_report_content: Optional[str] = None
    rag_store: Optional[Any] = None

    # ── New: structured MongoDB v5 data ──────────────────────────────
    structured_profile: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Full candidate profile loaded from all MongoDB collections (v5 schema). "
                    "Keys are collection names, values are Pydantic model instances.",
    )

    class Config:
        arbitrary_types_allowed = True

    # ------------------------------------------------------------------
    # get_summary — existing method, completely unchanged
    # ------------------------------------------------------------------

    def get_summary(
        self,
        max_length: int = 60000,
        agent_domain: Optional[str] = None,
        user_query: Optional[str] = None,
    ) -> str:
        """
        Generate a comprehensive summary of all data.
        Uses RAG if available to retrieve relevant chunks for specific agents.

        Args:
            max_length: Maximum character length for the summary (default: 60000 = ~15k tokens)
            agent_domain: Optional agent domain for RAG-based retrieval (e.g., "behaviour_psychology")
            user_query: Optional user query to focus RAG retrieval

        Returns:
            Summary string with relevant content
        """
        summary_parts = []

        # RAG is required - use it if agent domain is specified
        if agent_domain:
            if hasattr(self, "rag_store") and self.rag_store:
                print(f"Using RAG retrieval for agent: {agent_domain}")
                relevant_content = self.rag_store.get_summary_for_agent(
                    agent_domain=agent_domain,
                    user_query=user_query or "",
                )
                summary_parts.append(
                    f"REPORT CONTENT (RAG-retrieved for {agent_domain}):\n{relevant_content}\n"
                )
            else:
                raise ValueError(
                    f"RAG store not available for agent '{agent_domain}'. "
                    "Ensure RAG dependencies are installed: pip install faiss-cpu langchain-community"
                )

        # Standard summary (used if no agent domain specified, or for non-report content)
        if not summary_parts and self.raw_report_content:
            content = self.raw_report_content
            if len(content) > max_length:
                first_part = content[: int(max_length * 0.6)]
                last_part = content[-int(max_length * 0.4) :]
                truncated = (
                    first_part
                    + "\n\n[... MIDDLE CONTENT TRUNCATED FOR TOKEN LIMITS ...]\n\n"
                    + last_part
                )
                summary_parts.append(f"REPORT CONTENT:\n{truncated}\n")
            else:
                summary_parts.append(f"REPORT CONTENT:\n{content}\n")

        if self.primary_data:
            summary_parts.append(
                f"PRIMARY DATA:\nName: {self.primary_data.name}, Age: {self.primary_data.age}"
            )
            summary_parts.append(
                f"Education: {self.primary_data.education_level}, Profession: {self.primary_data.profession}"
            )

        if self.secondary_data:
            summary_parts.append(
                f"\nSECONDARY DATA:\nInterests: {', '.join(self.secondary_data.interests)}"
            )
            summary_parts.append(f"Hobbies: {', '.join(self.secondary_data.hobbies)}")

        if self.family_data:
            summary_parts.append(
                f"\nFAMILY DATA:\nFamily Members: {len(self.family_data.family_members)}"
            )
            summary_parts.append(
                f"Family Values: {', '.join(self.family_data.family_values)}"
            )

        if self.tertiary_data:
            summary_parts.append(
                f"\nTERTIARY DATA:\nPersonality Insights: {', '.join(self.tertiary_data.personality_insights)}"
            )

        if self.operational_data:
            summary_parts.append(
                f"\nOPERATIONAL DATA:\nPersonality Type: {self.operational_data.psychometric_report.personality_type}"
            )
            summary_parts.append(
                f"Health Status: {self.operational_data.medical_report.general_health_status}"
            )

        # ── Append structured v5 data if available ───────────────────
        structured_ctx = self.get_structured_context(agent_domain=agent_domain)
        if structured_ctx:
            summary_parts.append(structured_ctx)

        return "\n".join(summary_parts)

    # ------------------------------------------------------------------
    # NEW: get_structured_context — renders v5 MongoDB data as text
    # ------------------------------------------------------------------

    def get_structured_context(
        self,
        agent_domain: Optional[str] = None,
        max_length: int = 30000,
    ) -> str:
        """Render structured MongoDB v5 profile data as text for agent prompts.

        If agent_domain is provided, only the collections relevant to that agent
        are included (per AGENT_DOMAIN_DATA_MAP). Otherwise all collections.
        """
        if not self.structured_profile:
            return ""

        target_collections: Optional[List[str]] = None
        if agent_domain and agent_domain in AGENT_DOMAIN_DATA_MAP:
            target_collections = AGENT_DOMAIN_DATA_MAP[agent_domain]

        header = "\n=== STRUCTURED CANDIDATE DATA (MongoDB v5) ==="
        parts: List[str] = []

        for coll_name, value in self.structured_profile.items():
            if value is None:
                continue
            if target_collections and coll_name not in target_collections:
                continue

            if isinstance(value, list):
                if not value:
                    continue
                parts.append(f"\n--- {coll_name.upper()} ({len(value)} records) ---")
                for i, item in enumerate(value[:5]):
                    if hasattr(item, "model_dump"):
                        data = item.model_dump(exclude_none=True, exclude={"id"})
                        parts.append(f"  [{i+1}] {_compact_dict(data)}")
            elif hasattr(value, "model_dump"):
                data = value.model_dump(exclude_none=True, exclude={"id"})
                if data:
                    parts.append(f"\n--- {coll_name.upper()} ---")
                    parts.append(_compact_dict(data))

        if not parts:
            return ""

        text = header + "\n" + "\n".join(parts)
        if len(text) > max_length:
            text = text[:max_length] + "\n[... structured data truncated ...]"
        return text


def _compact_dict(d: dict, indent: int = 2, max_list: int = 5) -> str:
    """Recursively render a dict as compact readable text for prompts."""
    lines: List[str] = []
    prefix = " " * indent
    for k, v in d.items():
        if v is None:
            continue
        if isinstance(v, dict):
            nested = _compact_dict(v, indent + 2, max_list)
            if nested.strip():
                lines.append(f"{prefix}{k}:")
                lines.append(nested)
        elif isinstance(v, list):
            if not v:
                continue
            if all(isinstance(item, dict) for item in v):
                lines.append(f"{prefix}{k}: ({len(v)} items)")
                for i, item in enumerate(v[:max_list]):
                    lines.append(f"{prefix}  [{i+1}] {_flat_dict(item)}")
                if len(v) > max_list:
                    lines.append(f"{prefix}  ... and {len(v)-max_list} more")
            else:
                preview = v[:max_list]
                suffix = f" ... +{len(v)-max_list}" if len(v) > max_list else ""
                lines.append(f"{prefix}{k}: {preview}{suffix}")
        else:
            lines.append(f"{prefix}{k}: {v}")
    return "\n".join(lines)


def _flat_dict(d: dict) -> str:
    """Single-line summary of a dict."""
    parts = [f"{k}={v}" for k, v in d.items() if v is not None]
    return ", ".join(parts[:8])

