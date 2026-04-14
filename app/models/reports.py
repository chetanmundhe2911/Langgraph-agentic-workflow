"""Collection: reports — All AI-generated reports: AntarBahya, DISC, Bandhan, JeevanYog/Samvad, Sahajivan."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field
from .base import MongoModel


class AntarBahyaData(MongoModel):
    inner_world_score: Optional[float] = None
    outer_world_score: Optional[float] = None
    alignment_score: Optional[float] = None
    key_insights: List[str] = Field(default_factory=list)


class DISCReportData(MongoModel):
    D_score: Optional[float] = None
    I_score: Optional[float] = None
    S_score: Optional[float] = None
    C_score: Optional[float] = None
    primary_type: Optional[str] = None
    communication_tips: List[str] = Field(default_factory=list)


class BandhanReportData(MongoModel):
    compatibility_summary: Optional[str] = None
    compatibility_score: Optional[float] = None
    strengths: List[str] = Field(default_factory=list)
    growth_areas: List[str] = Field(default_factory=list)


class JeevanYogData(MongoModel):
    life_path_score: Optional[float] = None
    purpose_alignment: Optional[str] = None
    astro_yog_summary: Optional[str] = None


class JeevanSamvadData(MongoModel):
    communication_score: Optional[float] = None
    conflict_resolution_score: Optional[float] = None
    conversation_themes: List[str] = Field(default_factory=list)


class SahajivanData(MongoModel):
    daily_life_score: Optional[float] = None
    habit_compatibility: Optional[float] = None
    lifestyle_narrative: Optional[str] = None


class SecondaryReportLink(MongoModel):
    candidate_bio_id: Optional[str] = None


class ReportDocument(MongoModel):
    """MongoDB collection: reports"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    case_id: Optional[str] = None
    report_type: Optional[str] = None  # antarbahya | disc | bandhan | jeevan_yog | jeevan_samvad | sahajivan
    version: Optional[str] = None
    generated_at: Optional[datetime] = None
    generated_by_agent: Optional[str] = None
    status: Optional[str] = None  # draft | complete | reviewed | delivered
    json_data: Optional[Dict[str, Any]] = None
    prompt_used: Optional[str] = None
    summary_text: Optional[str] = None
    pdf_url: Optional[str] = None
    antarbahya_data: Optional[AntarBahyaData] = None
    disc_data: Optional[DISCReportData] = None
    bandhan_data: Optional[BandhanReportData] = None
    jeevan_yog_data: Optional[JeevanYogData] = None
    jeevan_samvad_data: Optional[JeevanSamvadData] = None
    sahajivan_data: Optional[SahajivanData] = None
    secondary_report: Optional[SecondaryReportLink] = None
    delivered_at: Optional[datetime] = None
    viewed_at: Optional[datetime] = None
    downloaded_at: Optional[datetime] = None
