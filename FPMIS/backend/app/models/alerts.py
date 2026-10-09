"""
FPMIS - Alert and Pattern Detection Models (Module 8)
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .base import Base


class AlertRule(Base):
    """Define what patterns trigger alerts"""
    __tablename__ = "alert_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    rule_type = Column(String(50), nullable=False)
    
    parameters = Column(JSONB, nullable=False)
    """
    Example parameters:
    
    Cluster:
    {"min_cases": 3, "time_window_days": 30, "region_level": "district", "cause_similarity": true}
    
    Unusual cause:
    {"keywords": ["cyanide", "arsenic", "thallium"], "notify_immediately": true}
    
    Unidentified:
    {"days_threshold": 7}
    
    Trend:
    {"threshold_multiplier": 2, "baseline_days": 30}
    """
    
    severity = Column(String(20), default='medium')
    
    is_active = Column(Boolean, default=True)
    
    notify_roles = Column(ARRAY(String))
    notify_emails = Column(ARRAY(String))
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    alerts = relationship("Alert", back_populates="rule")

    DEFAULT_RULES = [
        {
            "name": "Death Cluster Detection",
            "description": "Alerts when 3+ deaths with similar cause occur in same district within 30 days",
            "rule_type": "cluster",
            "parameters": {"min_cases": 3, "time_window_days": 30, "region_level": "district", "cause_similarity": True},
            "severity": "high"
        },
        {
            "name": "Poison/Toxin Alert",
            "description": "Immediate alert for suspected poisoning cases",
            "rule_type": "unusual_cause",
            "parameters": {"keywords": ["poison", "cyanide", "arsenic", "organophosphate", "thallium", "mercury"], "notify_immediately": True},
            "severity": "critical"
        },
        {
            "name": "Unidentified Body Alert",
            "description": "Alert for bodies unidentified after 7 days",
            "rule_type": "unidentified",
            "parameters": {"days_threshold": 7},
            "severity": "medium"
        },
        {
            "name": "Mass Casualty Trend",
            "description": "Alert when daily deaths exceed 2x normal average",
            "rule_type": "trend",
            "parameters": {"threshold_multiplier": 2, "baseline_days": 30},
            "severity": "high"
        }
    ]

    def to_dict(self):
        return {
            "id": str(self.id), "name": self.name, "description": self.description,
            "rule_type": self.rule_type, "parameters": self.parameters,
            "severity": self.severity, "is_active": self.is_active,
            "notify_roles": self.notify_roles
        }


class Alert(Base):
    """Generated alerts when patterns detected"""
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    rule_id = Column(UUID(as_uuid=True), ForeignKey("alert_rules.id"))
    
    alert_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    severity = Column(String(20), nullable=False)
    
    case_ids = Column(ARRAY(UUID(as_uuid=True)))
    region = Column(String(255))
    
    detection_parameters = Column(JSONB)
    pattern_details = Column(Text)
    
    status = Column(String(50), default='new')
    
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    viewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    viewed_at = Column(DateTime(timezone=True))
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    resolved_at = Column(DateTime(timezone=True))
    resolution_notes = Column(Text)
    
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    rule = relationship("AlertRule", back_populates="alerts")
    notifications = relationship("AlertNotification", back_populates="alert", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": str(self.id), "rule_id": str(self.rule_id) if self.rule_id else None,
            "alert_type": self.alert_type, "title": self.title,
            "description": self.description, "severity": self.severity,
            "case_ids": [str(cid) for cid in self.case_ids] if self.case_ids else [],
            "region": self.region, "status": self.status,
            "pattern_details": self.pattern_details,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None
        }


class AlertNotification(Base):
    """Track who was notified about alerts"""
    __tablename__ = "alert_notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    alert_id = Column(UUID(as_uuid=True), ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    notification_method = Column(String(50))
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    alert = relationship("Alert", back_populates="notifications")

    def to_dict(self):
        return {
            "id": str(self.id), "alert_id": str(self.alert_id),
            "user_id": str(self.user_id), "notification_method": self.notification_method,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "read_at": self.read_at.isoformat() if self.read_at else None
        }


class SavedComparison(Base):
    """Saved case comparisons (Module 7)"""
    __tablename__ = "saved_comparisons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    name = Column(String(255))
    description = Column(Text)
    
    case_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=False)
    
    comparison_fields = Column(ARRAY(String))
    
    comparison_result_json = Column(JSONB)
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": str(self.id), "name": self.name, "description": self.description,
            "case_ids": [str(cid) for cid in self.case_ids] if self.case_ids else [],
            "comparison_fields": self.comparison_fields,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class AuditLog(Base):
    """Track all system changes for compliance"""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user_email = Column(String(255))
    user_role = Column(String(50))
    
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True))
    
    old_values = Column(JSONB)
    new_values = Column(JSONB)
    description = Column(Text)
    
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    performed_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "id": str(self.id), "user_id": str(self.user_id) if self.user_id else None,
            "user_email": self.user_email, "action": self.action,
            "entity_type": self.entity_type,
            "entity_id": str(self.entity_id) if self.entity_id else None,
            "description": self.description,
            "performed_at": self.performed_at.isoformat() if self.performed_at else None
        }
