"""
FPMIS - Decomposition Logging Model (Module 3)
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .base import Base


class DecompositionLog(Base):
    """Track decomposition stages over time"""
    __tablename__ = "decomposition_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    
    stage = Column(String(50), nullable=False)
    stage_numeric = Column(Integer)
    
    temperature_celsius = Column(Numeric(5, 2))
    humidity_percent = Column(Numeric(5, 2))
    weather_condition = Column(String(100))
    location_type = Column(String(50))
    sun_exposure = Column(String(50))
    
    skin_changes = Column(Text)
    discoloration = Column(Text)
    bloating_level = Column(String(20))
    purging_present = Column(Boolean)
    marbling_present = Column(Boolean)
    skin_slippage = Column(Boolean)
    
    insect_activity_present = Column(Boolean)
    insect_types = Column(Text)
    maggot_mass_present = Column(Boolean)
    maggot_stage = Column(String(50))
    
    odor_level = Column(String(20))
    animal_activity = Column(Text)
    additional_observations = Column(Text)
    
    photo_references = Column(Text)
    
    logged_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    logged_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    case = relationship("Case", back_populates="decomposition_logs")
    logged_by_user = relationship("User", back_populates="decomposition_logs")

    STAGES = {
        1: "fresh",
        2: "early_decomposition",
        3: "bloat",
        4: "active_decay",
        5: "advanced_decay",
        6: "dry_remains",
        7: "skeletonization"
    }
    
    STAGE_DESCRIPTIONS = {
        "fresh": "No visible signs of decomposition. Body appears normal.",
        "early_decomposition": "Slight discoloration, early bloating beginning.",
        "bloat": "Full bloating, marbling visible, purging may begin.",
        "active_decay": "Significant tissue breakdown, strong odor, heavy insect activity.",
        "advanced_decay": "Most soft tissue gone, bones becoming exposed.",
        "dry_remains": "Mostly skeletal with some dried tissue remaining.",
        "skeletonization": "Only bones remain, all soft tissue decomposed."
    }

    def to_dict(self):
        return {
            "id": str(self.id), "case_id": str(self.case_id),
            "stage": self.stage, "stage_numeric": self.stage_numeric,
            "temperature_celsius": float(self.temperature_celsius) if self.temperature_celsius else None,
            "humidity_percent": float(self.humidity_percent) if self.humidity_percent else None,
            "location_type": self.location_type,
            "insect_activity_present": self.insect_activity_present,
            "maggot_mass_present": self.maggot_mass_present,
            "odor_level": self.odor_level,
            "additional_observations": self.additional_observations,
            "logged_at": self.logged_at.isoformat() if self.logged_at else None
        }

    @classmethod
    def get_stage_number(cls, stage_name):
        """Convert stage name to numeric value"""
        for num, name in cls.STAGES.items():
            if name == stage_name:
                return num
        return None

    @classmethod
    def get_stage_description(cls, stage_name):
        """Get description for a decomposition stage"""
        return cls.STAGE_DESCRIPTIONS.get(stage_name, "Unknown stage")
