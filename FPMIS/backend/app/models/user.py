"""
FPMIS - User and Institution Models
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .base import Base


class Institution(Base):
    """Institutions: Hospitals, Labs, Medical Colleges, Mortuaries"""
    __tablename__ = "institutions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    address = Column(Text)
    district = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    phone = Column(String(20))
    email = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    users = relationship("User", back_populates="institution")
    cases = relationship("Case", back_populates="institution")

    def to_dict(self):
        return {
            "id": str(self.id), "name": self.name, "type": self.type,
            "address": self.address, "district": self.district, "state": self.state,
            "pincode": self.pincode, "phone": self.phone, "email": self.email,
            "is_active": self.is_active
        }


class User(Base):
    """System users with role-based access control"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.id"))
    phone = Column(String(20))
    designation = Column(String(100))
    license_number = Column(String(100))
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    institution = relationship("Institution", back_populates="users")
    created_cases = relationship("Case", back_populates="creator", foreign_keys="Case.created_by")
    assigned_cases = relationship("Case", back_populates="doctor", foreign_keys="Case.assigned_doctor")
    autopsy_reports = relationship("AutopsyReport", back_populates="performed_by_user")
    collected_evidence = relationship("EvidenceItem", back_populates="collector", foreign_keys="EvidenceItem.collected_by")
    held_evidence = relationship("EvidenceItem", back_populates="holder", foreign_keys="EvidenceItem.current_holder")
    tod_calculations = relationship("TimeOfDeathEstimation", back_populates="calculated_by_user")
    decomposition_logs = relationship("DecompositionLog", back_populates="logged_by_user")

    def to_dict(self):
        return {
            "id": str(self.id), "email": self.email, "full_name": self.full_name,
            "role": self.role, "institution_id": str(self.institution_id) if self.institution_id else None,
            "phone": self.phone, "designation": self.designation,
            "license_number": self.license_number, "is_active": self.is_active
        }

    def has_role(self, *roles):
        return self.role in roles
