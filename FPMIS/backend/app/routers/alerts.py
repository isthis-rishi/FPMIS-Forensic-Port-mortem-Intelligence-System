"""
FPMIS - Alerts & Pattern Detection Routes
Module 8: Pattern-Based Alerts
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from app.models import Alert, AlertRule, Case, AutopsyReport, DeceasedInfo, User, get_db
from app.core import get_current_user, require_admin, require_staff

router = APIRouter(prefix="/alerts", tags=["Alerts & Pattern Detection"])



class AlertResponse(BaseModel):
    id: UUID
    rule_id: Optional[UUID] = None
    alert_type: str
    title: str
    description: Optional[str] = None
    severity: str
    case_ids: Optional[List[UUID]] = None
    region: Optional[str] = None
    pattern_details: Optional[str] = None
    status: str
    generated_at: datetime

    class Config:
        from_attributes = True


class AlertRuleResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    rule_type: str
    parameters: dict
    severity: str
    is_active: bool

    class Config:
        from_attributes = True


class AlertRuleCreate(BaseModel):
    name: str = Field(..., min_length=2)
    description: Optional[str] = None
    rule_type: str = Field(..., pattern="^(cluster|unusual_cause|unidentified|trend|custom)$")
    parameters: dict
    severity: str = Field("medium", pattern="^(low|medium|high|critical)$")


class MessageResponse(BaseModel):
    message: str
    success: bool = True


class AlertStats(BaseModel):
    total: int
    new: int
    investigating: int
    resolved: int
    by_severity: dict



def detect_cluster_alerts(db: Session, days: int = 30, min_cases: int = 3) -> List[dict]:
    """Detect clusters of similar deaths in same region"""
    
    alerts = []
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    clusters = db.query(
        DeceasedInfo.district,
        AutopsyReport.cause_of_death_immediate,
        func.count(Case.id).label('count'),
        func.array_agg(Case.id).label('case_ids')
    ).join(
        Case, DeceasedInfo.case_id == Case.id
    ).join(
        AutopsyReport, AutopsyReport.case_id == Case.id
    ).filter(
        Case.created_at >= cutoff_date,
        Case.is_deleted == False,
        DeceasedInfo.district.isnot(None),
        AutopsyReport.cause_of_death_immediate.isnot(None)
    ).group_by(
        DeceasedInfo.district,
        AutopsyReport.cause_of_death_immediate
    ).having(
        func.count(Case.id) >= min_cases
    ).all()
    
    for cluster in clusters:
        alerts.append({
            "alert_type": "cluster",
            "title": f"Death Cluster: {cluster.cause_of_death_immediate}",
            "description": f"{cluster.count} deaths with similar cause in {cluster.district} in last {days} days",
            "severity": "high" if cluster.count >= 5 else "medium",
            "region": cluster.district,
            "case_ids": list(cluster.case_ids),
            "pattern_details": f"Cause: {cluster.cause_of_death_immediate}, Count: {cluster.count}"
        })
    
    return alerts


def detect_unusual_cause_alerts(db: Session, keywords: List[str] = None) -> List[dict]:
    """Detect unusual causes of death (poisoning, etc.)"""
    
    if keywords is None:
        keywords = ["poison", "cyanide", "arsenic", "organophosphate", "thallium", "mercury", "overdose"]
    
    alerts = []
    
    cutoff_date = datetime.utcnow() - timedelta(days=7)
    
    for keyword in keywords:
        cases = db.query(Case, AutopsyReport).join(
            AutopsyReport, AutopsyReport.case_id == Case.id
        ).filter(
            Case.created_at >= cutoff_date,
            Case.is_deleted == False,
            AutopsyReport.cause_of_death_immediate.ilike(f"%{keyword}%")
        ).all()
        
        for case, autopsy in cases:
            alerts.append({
                "alert_type": "unusual_cause",
                "title": f"Unusual Cause Detected: {keyword.title()}",
                "description": f"Suspected {keyword} involvement in case {case.case_number}",
                "severity": "critical",
                "case_ids": [case.id],
                "pattern_details": f"Cause: {autopsy.cause_of_death_immediate}"
            })
    
    return alerts


def detect_unidentified_alerts(db: Session, days_threshold: int = 7) -> List[dict]:
    """Detect bodies unidentified for too long"""
    
    alerts = []
    cutoff_date = datetime.utcnow() - timedelta(days=days_threshold)
    
    unidentified = db.query(Case, DeceasedInfo).join(
        DeceasedInfo, DeceasedInfo.case_id == Case.id
    ).filter(
        Case.created_at <= cutoff_date,
        Case.is_deleted == False,
        Case.status != 'closed',
        DeceasedInfo.is_identified == False
    ).all()
    
    for case, deceased in unidentified:
        days_unidentified = (datetime.utcnow() - case.created_at).days
        alerts.append({
            "alert_type": "unidentified",
            "title": f"Unidentified Body: {days_unidentified} days",
            "description": f"Case {case.case_number} has been unidentified for {days_unidentified} days",
            "severity": "medium" if days_unidentified < 14 else "high",
            "case_ids": [case.id],
            "pattern_details": f"Gender: {deceased.gender}, Age: {deceased.age_years}"
        })
    
    return alerts



@router.get("", response_model=List[AlertResponse])
def list_alerts(
    status: Optional[str] = Query(None, pattern="^(new|viewed|investigating|resolved|dismissed)$"),
    severity: Optional[str] = Query(None, pattern="^(low|medium|high|critical)$"),
    alert_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all alerts with optional filters"""
    
    query = db.query(Alert)
    
    if status:
        query = query.filter(Alert.status == status)
    if severity:
        query = query.filter(Alert.severity == severity)
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    
    return query.order_by(Alert.generated_at.desc()).limit(limit).all()


@router.get("/stats", response_model=AlertStats)
def get_alert_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get alert statistics"""
    
    total = db.query(Alert).count()
    new = db.query(Alert).filter(Alert.status == "new").count()
    investigating = db.query(Alert).filter(Alert.status == "investigating").count()
    resolved = db.query(Alert).filter(Alert.status == "resolved").count()
    
    by_severity = {}
    for sev in ["low", "medium", "high", "critical"]:
        by_severity[sev] = db.query(Alert).filter(
            Alert.severity == sev,
            Alert.status.in_(["new", "investigating"])
        ).count()
    
    return AlertStats(
        total=total,
        new=new,
        investigating=investigating,
        resolved=resolved,
        by_severity=by_severity
    )


@router.post("/detect", response_model=List[AlertResponse])
def run_alert_detection(
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Run alert detection algorithms and create new alerts"""
    
    all_alerts = []
    
    cluster_alerts = detect_cluster_alerts(db)
    unusual_alerts = detect_unusual_cause_alerts(db)
    unidentified_alerts = detect_unidentified_alerts(db)
    
    all_detected = cluster_alerts + unusual_alerts + unidentified_alerts
    
    for alert_data in all_detected:
        existing = db.query(Alert).filter(
            Alert.alert_type == alert_data["alert_type"],
            Alert.title == alert_data["title"],
            Alert.generated_at >= datetime.utcnow() - timedelta(hours=24)
        ).first()
        
        if not existing:
            alert = Alert(
                alert_type=alert_data["alert_type"],
                title=alert_data["title"],
                description=alert_data["description"],
                severity=alert_data["severity"],
                region=alert_data.get("region"),
                case_ids=alert_data.get("case_ids"),
                pattern_details=alert_data.get("pattern_details"),
                status="new",
                generated_at=datetime.utcnow()
            )
            db.add(alert)
            all_alerts.append(alert)
    
    db.commit()
    
    for alert in all_alerts:
        db.refresh(alert)
    
    return all_alerts


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get alert details"""
    
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    if alert.status == "new":
        alert.status = "viewed"
        alert.viewed_by = current_user.id
        alert.viewed_at = datetime.utcnow()
        db.commit()
    
    return alert


@router.put("/{alert_id}/status", response_model=AlertResponse)
def update_alert_status(
    alert_id: UUID,
    new_status: str = Query(..., pattern="^(investigating|resolved|dismissed)$"),
    notes: Optional[str] = None,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Update alert status"""
    
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.status = new_status
    
    if new_status == "investigating":
        alert.assigned_to = current_user.id
    elif new_status == "resolved":
        alert.resolved_by = current_user.id
        alert.resolved_at = datetime.utcnow()
        alert.resolution_notes = notes
    
    db.commit()
    db.refresh(alert)
    
    return alert



@router.get("/rules", response_model=List[AlertRuleResponse])
def list_alert_rules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all alert rules"""
    
    return db.query(AlertRule).all()


@router.post("/rules", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
def create_alert_rule(
    rule_data: AlertRuleCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new alert rule (admin only)"""
    
    rule = AlertRule(
        created_by=current_user.id,
        is_active=True,
        **rule_data.model_dump()
    )
    
    db.add(rule)
    db.commit()
    db.refresh(rule)
    
    return rule


@router.put("/rules/{rule_id}/toggle", response_model=AlertRuleResponse)
def toggle_alert_rule(
    rule_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Enable/disable an alert rule"""
    
    rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    rule.is_active = not rule.is_active
    db.commit()
    db.refresh(rule)
    
    return rule
