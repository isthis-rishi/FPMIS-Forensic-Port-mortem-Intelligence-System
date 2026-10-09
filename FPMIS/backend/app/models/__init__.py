"""
FPMIS - SQLAlchemy Models
All models for the Forensic Post-Mortem Intelligence System
"""

from .base import Base, engine, SessionLocal, get_db, create_tables, drop_tables

from .user import User, Institution

from .case import Case, DeceasedInfo, AutopsyReport, Injury

from .tod import TimeOfDeathEstimation

from .decomposition import DecompositionLog

from .evidence import EvidenceItem, ChainOfCustody

from .matching import MissingPerson, BodyMatchResult

from .alerts import AlertRule, Alert, AlertNotification, SavedComparison, AuditLog


ALL_MODELS = [
    Institution,
    User,
    Case,
    DeceasedInfo,
    AutopsyReport,
    Injury,
    TimeOfDeathEstimation,
    DecompositionLog,
    EvidenceItem,
    ChainOfCustody,
    MissingPerson,
    BodyMatchResult,
    AlertRule,
    Alert,
    AlertNotification,
    SavedComparison,
    AuditLog,
]

__all__ = [
    "Base",
    "engine", 
    "SessionLocal",
    "get_db",
    "create_tables",
    "drop_tables",
    
    "Institution",
    "User",
    "Case",
    "DeceasedInfo",
    "AutopsyReport",
    "Injury",
    "TimeOfDeathEstimation",
    "DecompositionLog",
    "EvidenceItem",
    "ChainOfCustody",
    "MissingPerson",
    "BodyMatchResult",
    "AlertRule",
    "Alert",
    "AlertNotification",
    "SavedComparison",
    "AuditLog",
    
    "ALL_MODELS",
]
