"""
IKSCBandhan MongoDB Schema v5 — Pydantic models for all 38 collections.
"""

from .base import MongoModel, TimestampMixin, Gender, StatusEnum, PlatformEnum, FlagType

# Core user data
from .user import UserDocument, AuthInfo, ProfileInfo, LocationInfo, SubscriptionInfo
from .primary_data import (
    PrimaryDataDocument, IdentityInfo, EducationEntry, CurrentJob, PastJob,
    FinancialInfo, ForeignTravelEntry, Achievement, DocumentEntry,
)
from .secondary_data import (
    SecondaryDataDocument, FacebookData, InstagramData, LinkedInData,
    TwitterData, YouTubeData, PortfolioData, AIDigitalAnalysis,
)
from .tertiary_data import (
    TertiaryDataDocument, ReferenceEntry, ReferenceResponse,
    AggregatedTertiaryInsights,
)
from .operational_data import (
    OperationalDataDocument, PsychometricsData, DISCScores, WPDScores,
    RelationshipReadiness, AnterbhayaScores, JeevanYogScores,
    AudioRecording, ToneAnalysis, ElevatorPitch, BehaviorAnalysis, CVData,
)
from .family_data import (
    FamilyDataDocument, ParentProfile, GrandparentProfile, SiblingProfile,
    CloseRelative, AncestryInfo, FamilyFinancials, UpbringingInfo,
)
from .marriage_data import (
    MarriageDataDocument, BioData, KundaliInfo, HoroscopeInfo,
    MatrimonyProfile, PartnerPreferences, ProfileMedia,
)
from .medical_data import (
    MedicalDataDocument, BloodInfo, PhysicalInfo, FitnessLifestyle,
    ChronicCondition, AllergyEntry, Medication, MentalHealthInfo,
    HereditaryRisk, HygieneInfo,
)
from .ideal_usecase import (
    IdealUsecaseDocument, IDISCIdeal, WPDIdeal, AnterbhayaIdeal,
    ValuesIdeal, HabitsIdeal, AIIdealProfile,
)

# Workflow: cases, reports, assessments
from .case_data import (
    CaseDataDocument, CandidateBio, CandidateSecondary, CompatibilityScores,
    MeetingEntry, DiscussionQuestion, CaseDecision,
)
from .reports import (
    ReportDocument, AntarBahyaData, DISCReportData, BandhanReportData,
    JeevanYogData, JeevanSamvadData, SahajivanData,
)
from .assessments import AssessmentDocument, AssessmentQuestion, AssessmentScores

# Sessions & logs
from .sessions_logs import (
    AgentLogDocument, AgentChainEntry, DecisionGate,
    OrchestratorSessionDocument, OrchestratorOutput,
    CounsellingSessionDocument, SessionRecording,
)

# Customer journey & communications
from .journey_comms import (
    CustomerJourneyDocument, JourneyMilestones, FollowupTracking,
    CommunicationDocument, EmailComm, CallComm,
    ExternalMemoryDocument,
)

# Career Compass vertical
from .career_compass import (
    CareerCompassProfileDocument, CareerSessionDocument, CareerReportDocument,
    SkillsCC, CareerGoals, SkillGapReport, CareerPathReport, MarketFitReport,
)

# Bandhan vertical
from .bandhan import (
    BandhanContextDocument, PreMarriageContext, CompatTestContext,
    MarriageCompatibilityDocument, CompatScores,
    MarriageHappinessDocument, HappinessDimensions, HappinessAIInsights,
    DivorceConflictDocument, RootCauseAnalysis,
    CoupleSessionDocument,
)

# Customer engagement automation
from .engagement import (
    WebQuizDocument, QuizScores, AIProfileSnapshot,
    EmailSequenceDocument, SequenceEmail,
    CallAutomationDocument, AICallBrief,
    LeadFunnelDocument, EmailStats, CallStats,
    AutomationRuleDocument, RuleTrigger, RuleAction,
)

# Individual journey (pre-marriage)
from .individual_journey import (
    IndividualJourneyDocument, Phase1SelfUnderstanding, Phase2CounsellorTraining,
    Phase3CandidateEvaluation, Phase4Decision,
    SessionScriptDocument, ScriptTurn, ScriptAIAnalysis,
    BioDataProfileDocument, BioDataContent, AISuggestion, AIAuthenticity,
    MeetingPrepDocument, QuestionToAsk, AnswerPattern, MeetingGuidance,
    CandidateBioReceivedDocument, ExtractedBioFields, SocialScrapeData, OneToOneComparison,
    MeetingSessionDocument, MeetingScriptTurn, MeetingAIAnalysis,
    ProposalDecisionDocument, AIFinalAssessment, UserDecision,
)


# ---------------------------------------------------------------------------
# Collection name → Document model mapping (used by MongoDBService)
# ---------------------------------------------------------------------------
COLLECTION_MODEL_MAP = {
    "users": UserDocument,
    "primary_data": PrimaryDataDocument,
    "secondary_data": SecondaryDataDocument,
    "tertiary_data": TertiaryDataDocument,
    "operational_data": OperationalDataDocument,
    "family_data": FamilyDataDocument,
    "marriage_data": MarriageDataDocument,
    "medical_data": MedicalDataDocument,
    "ideal_usecase_data": IdealUsecaseDocument,
    "case_data": CaseDataDocument,
    "reports": ReportDocument,
    "assessments": AssessmentDocument,
    "ai_agents_log": AgentLogDocument,
    "orchestrator_sessions": OrchestratorSessionDocument,
    "counselling_sessions": CounsellingSessionDocument,
    "customer_journey": CustomerJourneyDocument,
    "communications": CommunicationDocument,
    "external_memory": ExternalMemoryDocument,
    "career_compass_profiles": CareerCompassProfileDocument,
    "career_sessions": CareerSessionDocument,
    "career_reports": CareerReportDocument,
    "bandhan_product_context": BandhanContextDocument,
    "marriage_compatibility_assessments": MarriageCompatibilityDocument,
    "marriage_happiness_index": MarriageHappinessDocument,
    "divorce_conflict_resolution": DivorceConflictDocument,
    "couple_sessions": CoupleSessionDocument,
    "web_quiz": WebQuizDocument,
    "email_automation_sequences": EmailSequenceDocument,
    "call_automation_log": CallAutomationDocument,
    "lead_funnel_tracker": LeadFunnelDocument,
    "automation_rules": AutomationRuleDocument,
    "individual_journey_tracker": IndividualJourneyDocument,
    "counsellor_session_scripts": SessionScriptDocument,
    "bio_data_profiles": BioDataProfileDocument,
    "meeting_preparation_training": MeetingPrepDocument,
    "candidate_bio_received": CandidateBioReceivedDocument,
    "meeting_sessions": MeetingSessionDocument,
    "proposal_decisions": ProposalDecisionDocument,
}
