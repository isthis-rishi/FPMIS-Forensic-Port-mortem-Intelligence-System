"""
FPMIS - Time of Death Estimation Model (Module 2)
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .base import Base


class TimeOfDeathEstimation(Base):
    """TOD calculation inputs and results"""
    __tablename__ = "time_of_death_estimations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    body_temperature_celsius = Column(Numeric(4, 2))
    ambient_temperature_celsius = Column(Numeric(4, 2))
    body_weight_kg = Column(Numeric(5, 2))
    clothing_description = Column(String(255))
    body_position = Column(String(100))
    environment = Column(String(50))
    
    rigor_mortis_jaw = Column(Integer)
    rigor_mortis_neck = Column(Integer)
    rigor_mortis_upper_limbs = Column(Integer)
    rigor_mortis_lower_limbs = Column(Integer)
    rigor_mortis_overall = Column(Integer)
    
    livor_mortis_present = Column(Boolean)
    livor_mortis_color = Column(String(50))
    livor_mortis_distribution = Column(Text)
    livor_mortis_fixed = Column(Boolean)
    
    corneal_opacity = Column(Integer)
    tache_noire = Column(Boolean)
    decomposition_started = Column(Boolean)
    insect_activity = Column(Text)
    
    estimated_tod_min_hours = Column(Numeric(5, 2))
    estimated_tod_max_hours = Column(Numeric(5, 2))
    estimated_tod_datetime_min = Column(DateTime(timezone=True))
    estimated_tod_datetime_max = Column(DateTime(timezone=True))
    confidence_level = Column(String(20))
    
    calculation_method = Column(String(100))
    calculation_reasoning = Column(Text)
    calculation_parameters_json = Column(JSONB)
    
    is_manually_adjusted = Column(Boolean, default=False)
    manual_tod_min = Column(DateTime(timezone=True))
    manual_tod_max = Column(DateTime(timezone=True))
    manual_adjustment_reason = Column(Text)
    
    calculated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    case = relationship("Case", back_populates="tod_estimation")
    calculated_by_user = relationship("User", back_populates="tod_calculations")

    def to_dict(self):
        return {
            "id": str(self.id), "case_id": str(self.case_id),
            "body_temperature_celsius": float(self.body_temperature_celsius) if self.body_temperature_celsius else None,
            "ambient_temperature_celsius": float(self.ambient_temperature_celsius) if self.ambient_temperature_celsius else None,
            "rigor_mortis_overall": self.rigor_mortis_overall,
            "livor_mortis_present": self.livor_mortis_present,
            "livor_mortis_fixed": self.livor_mortis_fixed,
            "estimated_tod_min_hours": float(self.estimated_tod_min_hours) if self.estimated_tod_min_hours else None,
            "estimated_tod_max_hours": float(self.estimated_tod_max_hours) if self.estimated_tod_max_hours else None,
            "confidence_level": self.confidence_level,
            "calculation_reasoning": self.calculation_reasoning,
            "is_manually_adjusted": self.is_manually_adjusted
        }

    @staticmethod
    def calculate_tod(body_temp, ambient_temp, rigor_stage, livor_fixed, weight_kg=70):
        """
        Simple rule-based TOD calculation
        Returns dict with min_hours, max_hours, reasoning
        """
        
        if body_temp is None or ambient_temp is None:
            return {"min_hours": 0, "max_hours": 48, "confidence": "low", "reasoning": "Insufficient temperature data"}
        
        temp_drop = 37 - float(body_temp)
        
        if weight_kg and weight_kg < 50:
            cooling_rate = 1.5
        elif weight_kg and weight_kg > 80:
            cooling_rate = 0.9
        else:
            cooling_rate = 1.2
        
        hours_from_temp = temp_drop / cooling_rate if cooling_rate > 0 else 0
        
        rigor_ranges = {
            0: (0, 2),
            1: (2, 6),
            2: (6, 12),
            3: (12, 24),
            4: (24, 48)
        }
        rigor_min, rigor_max = rigor_ranges.get(rigor_stage, (0, 48))
        
        livor_min = 8 if livor_fixed else 0
        
        estimated_min = max(hours_from_temp - 3, rigor_min, livor_min, 0)
        estimated_max = max(hours_from_temp + 3, rigor_max)
        
        confidence = "high" if abs(hours_from_temp - (rigor_min + rigor_max) / 2) < 6 else "medium"
        
        reasoning = f"Based on body temp ({body_temp}°C, {temp_drop}°C drop), "
        reasoning += f"rigor mortis stage {rigor_stage}, "
        reasoning += f"livor mortis {'fixed' if livor_fixed else 'not fixed'}. "
        reasoning += f"Estimated {estimated_min:.1f}-{estimated_max:.1f} hours since death."
        
        return {
            "min_hours": round(estimated_min, 1),
            "max_hours": round(estimated_max, 1),
            "confidence": confidence,
            "reasoning": reasoning
        }
