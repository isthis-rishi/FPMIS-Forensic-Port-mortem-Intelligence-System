"""
FPMIS - Evidence and Chain of Custody Models (Module 4)
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .base import Base


class EvidenceItem(Base):
    """Evidence collected from cases"""
    __tablename__ = "evidence_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    
    evidence_number = Column(String(50), nullable=False)
    barcode = Column(String(100))
    
    item_type = Column(String(50), nullable=False)
    item_name = Column(String(255), nullable=False)
    description = Column(Text)
    
    collected_from = Column(String(255))
    collection_method = Column(String(255))
    quantity = Column(String(100))
    condition_when_collected = Column(String(255))
    
    storage_location = Column(String(255))
    storage_requirements = Column(Text)
    
    status = Column(String(50), default='in_custody')
    
    sent_to_lab = Column(String(255))
    analysis_type = Column(String(255))
    analysis_result = Column(Text)
    analysis_report_reference = Column(String(255))
    
    collected_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    collected_at = Column(DateTime(timezone=True), nullable=False)
    
    current_holder = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    current_location = Column(String(255))
    
    disposal_date = Column(Date)
    disposal_method = Column(String(255))
    disposal_authorized_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    case = relationship("Case", back_populates="evidence_items")
    collector = relationship("User", back_populates="collected_evidence", foreign_keys=[collected_by])
    holder = relationship("User", back_populates="held_evidence", foreign_keys=[current_holder])
    chain_of_custody = relationship("ChainOfCustody", back_populates="evidence", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": str(self.id), "case_id": str(self.case_id),
            "evidence_number": self.evidence_number, "item_type": self.item_type,
            "item_name": self.item_name, "description": self.description,
            "status": self.status, "collected_from": self.collected_from,
            "storage_location": self.storage_location,
            "current_holder": str(self.current_holder) if self.current_holder else None,
            "current_location": self.current_location,
            "collected_at": self.collected_at.isoformat() if self.collected_at else None,
            "analysis_result": self.analysis_result
        }


class ChainOfCustody(Base):
    """Every evidence transfer recorded"""
    __tablename__ = "chain_of_custody"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evidence_id = Column(UUID(as_uuid=True), ForeignKey("evidence_items.id", ondelete="CASCADE"), nullable=False)
    
    action_type = Column(String(50), nullable=False)
    
    from_user = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    to_user = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    performed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    from_location = Column(String(255))
    to_location = Column(String(255))
    transfer_datetime = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    condition_at_transfer = Column(String(255))
    purpose = Column(Text)
    notes = Column(Text)
    
    received_signature_reference = Column(String(255))
    witness_name = Column(String(255))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    evidence = relationship("EvidenceItem", back_populates="chain_of_custody")
    from_user_rel = relationship("User", foreign_keys=[from_user])
    to_user_rel = relationship("User", foreign_keys=[to_user])
    performed_by_rel = relationship("User", foreign_keys=[performed_by])

    def to_dict(self):
        return {
            "id": str(self.id), "evidence_id": str(self.evidence_id),
            "action_type": self.action_type,
            "from_user": str(self.from_user) if self.from_user else None,
            "to_user": str(self.to_user) if self.to_user else None,
            "performed_by": str(self.performed_by),
            "from_location": self.from_location, "to_location": self.to_location,
            "transfer_datetime": self.transfer_datetime.isoformat() if self.transfer_datetime else None,
            "condition_at_transfer": self.condition_at_transfer,
            "purpose": self.purpose, "notes": self.notes
        }
