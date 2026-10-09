"""
FPMIS - Case and Autopsy Models (Module 1)
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .base import Base


class Case(Base):
    """Main Case Table - Core of the entire system"""
    __tablename__ = "cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_number = Column(String(50), unique=True, nullable=False)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"), nullable=False)
    
    status = Column(String(50), default='open')
    priority = Column(String(20), default='normal')
    case_type = Column(String(50))
    
    police_station = Column(String(255))
    fir_number = Column(String(100))
    brought_by = Column(String(255))
    
    body_received_at = Column(DateTime(timezone=True))
    autopsy_started_at = Column(DateTime(timezone=True))
    autopsy_completed_at = Column(DateTime(timezone=True))
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assigned_doctor = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    institution = relationship("Institution", back_populates="cases")
    creator = relationship("User", back_populates="created_cases", foreign_keys=[created_by])
    doctor = relationship("User", back_populates="assigned_cases", foreign_keys=[assigned_doctor])
    deceased_info = relationship("DeceasedInfo", back_populates="case", uselist=False, cascade="all, delete-orphan")
    autopsy_report = relationship("AutopsyReport", back_populates="case", uselist=False, cascade="all, delete-orphan")
    tod_estimation = relationship("TimeOfDeathEstimation", back_populates="case", uselist=False, cascade="all, delete-orphan")
    injuries = relationship("Injury", back_populates="case", cascade="all, delete-orphan")
    evidence_items = relationship("EvidenceItem", back_populates="case", cascade="all, delete-orphan")
    decomposition_logs = relationship("DecompositionLog", back_populates="case", cascade="all, delete-orphan")
    match_results = relationship("BodyMatchResult", back_populates="case", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": str(self.id), "case_number": self.case_number, "status": self.status,
            "priority": self.priority, "case_type": self.case_type,
            "institution_id": str(self.institution_id), "police_station": self.police_station,
            "fir_number": self.fir_number, "body_received_at": self.body_received_at.isoformat() if self.body_received_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class DeceasedInfo(Base):
    """Information about the deceased person"""
    __tablename__ = "deceased_info"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    is_identified = Column(Boolean, default=False)
    name = Column(String(255))
    alias = Column(String(255))
    
    age_years = Column(Integer)
    age_months = Column(Integer)
    age_estimated = Column(Boolean, default=False)
    gender = Column(String(20))
    
    height_cm = Column(Numeric(5, 2))
    weight_kg = Column(Numeric(5, 2))
    build = Column(String(50))
    complexion = Column(String(50))
    hair_color = Column(String(50))
    hair_length = Column(String(50))
    eye_color = Column(String(50))
    
    identification_marks = Column(Text)
    dental_features = Column(Text)
    
    address = Column(Text)
    district = Column(String(100))
    state = Column(String(100))
    
    relative_name = Column(String(255))
    relative_relation = Column(String(100))
    relative_phone = Column(String(20))
    relative_address = Column(Text)
    
    id_proof_type = Column(String(50))
    id_proof_number = Column(String(100))
    
    photo_face = Column(String(500))
    photo_full_body = Column(String(500))
    photo_identification_marks = Column(String(500))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    case = relationship("Case", back_populates="deceased_info")

    def to_dict(self):
        return {
            "id": str(self.id), "case_id": str(self.case_id), "is_identified": self.is_identified,
            "name": self.name, "age_years": self.age_years, "gender": self.gender,
            "height_cm": float(self.height_cm) if self.height_cm else None,
            "weight_kg": float(self.weight_kg) if self.weight_kg else None,
            "build": self.build, "complexion": self.complexion,
            "identification_marks": self.identification_marks, "district": self.district
        }


class AutopsyReport(Base):
    """Complete autopsy findings"""
    __tablename__ = "autopsy_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), unique=True, nullable=False)
    performed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assisted_by = Column(Text)
    
    general_appearance = Column(Text)
    clothing_description = Column(Text)
    post_mortem_changes = Column(Text)
    external_injuries = Column(Text)
    
    head_face_findings = Column(Text)
    neck_findings = Column(Text)
    chest_findings = Column(Text)
    abdomen_findings = Column(Text)
    back_findings = Column(Text)
    upper_limbs_findings = Column(Text)
    lower_limbs_findings = Column(Text)
    genitalia_findings = Column(Text)
    
    scalp_skull = Column(Text)
    brain_findings = Column(Text)
    brain_weight_gm = Column(Numeric(6, 2))
    
    neck_structures = Column(Text)
    hyoid_bone = Column(Text)
    thyroid_cartilage = Column(Text)
    
    chest_cavity = Column(Text)
    lungs_findings = Column(Text)
    lungs_weight_left_gm = Column(Numeric(6, 2))
    lungs_weight_right_gm = Column(Numeric(6, 2))
    heart_findings = Column(Text)
    heart_weight_gm = Column(Numeric(6, 2))
    major_vessels = Column(Text)
    
    abdominal_cavity = Column(Text)
    liver_findings = Column(Text)
    liver_weight_gm = Column(Numeric(6, 2))
    spleen_findings = Column(Text)
    spleen_weight_gm = Column(Numeric(6, 2))
    kidneys_findings = Column(Text)
    kidneys_weight_left_gm = Column(Numeric(6, 2))
    kidneys_weight_right_gm = Column(Numeric(6, 2))
    stomach_contents = Column(Text)
    intestines_findings = Column(Text)
    
    bladder_findings = Column(Text)
    uterus_findings = Column(Text)
    prostate_findings = Column(Text)
    
    spine_findings = Column(Text)
    spinal_cord = Column(Text)
    
    cause_of_death_immediate = Column(String(500))
    cause_of_death_antecedent = Column(String(500))
    cause_of_death_underlying = Column(String(500))
    cause_of_death_contributing = Column(Text)
    manner_of_death = Column(String(50))
    
    special_dissections = Column(Text)
    samples_collected = Column(Text)
    doctors_remarks = Column(Text)
    
    is_finalized = Column(Boolean, default=False)
    finalized_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    case = relationship("Case", back_populates="autopsy_report")
    performed_by_user = relationship("User", back_populates="autopsy_reports")

    def to_dict(self):
        return {
            "id": str(self.id), "case_id": str(self.case_id),
            "cause_of_death_immediate": self.cause_of_death_immediate,
            "cause_of_death_antecedent": self.cause_of_death_antecedent,
            "cause_of_death_underlying": self.cause_of_death_underlying,
            "manner_of_death": self.manner_of_death,
            "is_finalized": self.is_finalized,
            "doctors_remarks": self.doctors_remarks
        }


class Injury(Base):
    """Individual injury documentation"""
    __tablename__ = "injuries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    
    injury_type = Column(String(50), nullable=False)
    body_region = Column(String(100), nullable=False)
    body_side = Column(String(20))
    
    length_cm = Column(Numeric(5, 2))
    width_cm = Column(Numeric(5, 2))
    depth_cm = Column(Numeric(5, 2))
    
    description = Column(Text)
    probable_weapon = Column(String(255))
    age_of_injury = Column(String(100))
    is_fatal = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    case = relationship("Case", back_populates="injuries")

    def to_dict(self):
        return {
            "id": str(self.id), "case_id": str(self.case_id),
            "injury_type": self.injury_type, "body_region": self.body_region,
            "body_side": self.body_side, "description": self.description,
            "length_cm": float(self.length_cm) if self.length_cm else None,
            "width_cm": float(self.width_cm) if self.width_cm else None,
            "depth_cm": float(self.depth_cm) if self.depth_cm else None,
            "probable_weapon": self.probable_weapon, "is_fatal": self.is_fatal
        }
