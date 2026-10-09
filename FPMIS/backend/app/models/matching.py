"""
FPMIS - Missing Person and Body Matching Models (Module 5)
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer, Numeric, Date, Time
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .base import Base


class MissingPerson(Base):
    """Missing persons reports for matching"""
    __tablename__ = "missing_persons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    report_number = Column(String(50), unique=True, nullable=False)
    reported_by = Column(String(255), nullable=False)
    reporter_relation = Column(String(100))
    reporter_phone = Column(String(20))
    reporter_address = Column(Text)
    
    name = Column(String(255), nullable=False)
    alias = Column(String(255))
    
    age_years = Column(Integer)
    age_approximate = Column(Boolean, default=False)
    gender = Column(String(20))
    
    height_cm_min = Column(Numeric(5, 2))
    height_cm_max = Column(Numeric(5, 2))
    weight_kg_min = Column(Numeric(5, 2))
    weight_kg_max = Column(Numeric(5, 2))
    build = Column(String(50))
    complexion = Column(String(50))
    hair_color = Column(String(50))
    hair_style = Column(String(100))
    eye_color = Column(String(50))
    
    identification_marks = Column(Text)
    scars = Column(Text)
    tattoos = Column(Text)
    birthmarks = Column(Text)
    dental_features = Column(Text)
    deformities = Column(Text)
    
    last_seen_date = Column(Date, nullable=False)
    last_seen_time = Column(Time)
    last_seen_location = Column(Text)
    last_seen_district = Column(String(100))
    last_seen_state = Column(String(100))
    last_seen_wearing = Column(Text)
    
    medical_conditions = Column(Text)
    medications = Column(Text)
    mental_health_notes = Column(Text)
    
    photo_recent = Column(String(500))
    photo_additional = Column(Text)
    
    status = Column(String(50), default='active')
    matched_case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"))
    
    police_station = Column(String(255))
    fir_number = Column(String(100))
    investigating_officer = Column(String(255))
    officer_phone = Column(String(20))
    
    entered_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    source = Column(String(100))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    match_results = relationship("BodyMatchResult", back_populates="missing_person")

    def to_dict(self):
        return {
            "id": str(self.id), "report_number": self.report_number,
            "name": self.name, "age_years": self.age_years, "gender": self.gender,
            "height_cm_min": float(self.height_cm_min) if self.height_cm_min else None,
            "height_cm_max": float(self.height_cm_max) if self.height_cm_max else None,
            "identification_marks": self.identification_marks,
            "last_seen_date": self.last_seen_date.isoformat() if self.last_seen_date else None,
            "last_seen_location": self.last_seen_location,
            "last_seen_district": self.last_seen_district,
            "status": self.status,
            "photo_recent": self.photo_recent
        }


class BodyMatchResult(Base):
    """Matching scores between unidentified bodies and missing persons"""
    __tablename__ = "body_match_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False)
    missing_person_id = Column(UUID(as_uuid=True), ForeignKey("missing_persons.id"), nullable=False)
    
    match_score_percent = Column(Numeric(5, 2), nullable=False)
    confidence_level = Column(String(20))
    
    score_breakdown = Column(JSONB)
    
    status = Column(String(50), default='pending')
    
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_at = Column(DateTime(timezone=True))
    review_notes = Column(Text)
    
    confirmed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    confirmed_at = Column(DateTime(timezone=True))
    confirmation_method = Column(String(100))
    
    algorithm_version = Column(String(50))
    matched_at = Column(DateTime(timezone=True), server_default=func.now())
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    case = relationship("Case", back_populates="match_results")
    missing_person = relationship("MissingPerson", back_populates="match_results")

    def to_dict(self):
        return {
            "id": str(self.id),
            "case_id": str(self.case_id),
            "missing_person_id": str(self.missing_person_id),
            "match_score_percent": float(self.match_score_percent),
            "confidence_level": self.confidence_level,
            "score_breakdown": self.score_breakdown,
            "status": self.status,
            "confirmation_method": self.confirmation_method,
            "matched_at": self.matched_at.isoformat() if self.matched_at else None
        }

    @staticmethod
    def calculate_match_score(missing_person, deceased_info):
        """
        Calculate match score between missing person and unidentified body
        Returns dict with score, percentage, and breakdown
        """
        score = 0
        max_score = 0
        breakdown = {}
        
        max_score += 20
        if missing_person.gender and deceased_info.gender:
            if missing_person.gender == deceased_info.gender:
                score += 20
                breakdown["gender"] = {"score": 20, "max": 20, "match": True}
            else:
                breakdown["gender"] = {"score": 0, "max": 20, "match": False}
                return {
                    "score": 0,
                    "percentage": 0,
                    "confidence": "low",
                    "breakdown": breakdown,
                    "reason": "Gender mismatch"
                }
        
        max_score += 15
        if missing_person.age_years and deceased_info.age_years:
            age_diff = abs(missing_person.age_years - deceased_info.age_years)
            if age_diff <= 2:
                score += 15
                breakdown["age"] = {"score": 15, "max": 15, "difference": age_diff}
            elif age_diff <= 5:
                score += 10
                breakdown["age"] = {"score": 10, "max": 15, "difference": age_diff}
            elif age_diff <= 10:
                score += 5
                breakdown["age"] = {"score": 5, "max": 15, "difference": age_diff}
            else:
                breakdown["age"] = {"score": 0, "max": 15, "difference": age_diff}
        
        max_score += 15
        if deceased_info.height_cm:
            deceased_height = float(deceased_info.height_cm)
            mp_height_min = float(missing_person.height_cm_min) if missing_person.height_cm_min else None
            mp_height_max = float(missing_person.height_cm_max) if missing_person.height_cm_max else None
            
            if mp_height_min and mp_height_max:
                if mp_height_min <= deceased_height <= mp_height_max:
                    score += 15
                    breakdown["height"] = {"score": 15, "max": 15, "in_range": True}
                elif abs(deceased_height - mp_height_min) <= 5 or abs(deceased_height - mp_height_max) <= 5:
                    score += 10
                    breakdown["height"] = {"score": 10, "max": 15, "in_range": False, "close": True}
                else:
                    breakdown["height"] = {"score": 0, "max": 15, "in_range": False}
        
        max_score += 10
        if missing_person.build and deceased_info.build:
            if missing_person.build == deceased_info.build:
                score += 10
                breakdown["build"] = {"score": 10, "max": 10, "match": True}
            else:
                breakdown["build"] = {"score": 0, "max": 10, "match": False}
        
        max_score += 10
        if missing_person.hair_color and deceased_info.hair_color:
            if missing_person.hair_color.lower() == deceased_info.hair_color.lower():
                score += 10
                breakdown["hair_color"] = {"score": 10, "max": 10, "match": True}
            else:
                breakdown["hair_color"] = {"score": 0, "max": 10, "match": False}
        
        max_score += 20
        mp_marks = (missing_person.identification_marks or "").lower()
        dec_marks = (deceased_info.identification_marks or "").lower()
        if mp_marks and dec_marks:
            mp_words = set(mp_marks.split())
            dec_words = set(dec_marks.split())
            common = mp_words.intersection(dec_words)
            if len(common) >= 3:
                score += 20
                breakdown["identification_marks"] = {"score": 20, "max": 20, "common_keywords": list(common)}
            elif len(common) >= 1:
                score += 10
                breakdown["identification_marks"] = {"score": 10, "max": 20, "common_keywords": list(common)}
            else:
                breakdown["identification_marks"] = {"score": 0, "max": 20, "common_keywords": []}
        
        percentage = round((score / max_score) * 100, 1) if max_score > 0 else 0
        
        if percentage >= 80:
            confidence = "high"
        elif percentage >= 60:
            confidence = "medium"
        else:
            confidence = "low"
        
        return {
            "score": score,
            "max_score": max_score,
            "percentage": percentage,
            "confidence": confidence,
            "breakdown": breakdown
        }
