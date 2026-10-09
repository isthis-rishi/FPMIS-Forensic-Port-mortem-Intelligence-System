"""
FPMIS - Autopsy Report & Injuries Routes
Module 1: Autopsy Report Structuring
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime

from app.models import Case, AutopsyReport, Injury, User, get_db
from app.schemas.case import (
    AutopsyReportCreate, AutopsyReportUpdate, AutopsyReportResponse,
    InjuryCreate, InjuryResponse
)
from app.schemas.user import MessageResponse
from app.core import get_current_user, require_doctor

router = APIRouter(prefix="/cases/{case_id}", tags=["Autopsy & Injuries"])



@router.post("/autopsy", response_model=AutopsyReportResponse, status_code=status.HTTP_201_CREATED)
def create_autopsy_report(
    case_id: UUID,
    autopsy_data: AutopsyReportCreate,
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """Create autopsy report for a case"""
    
    case = db.query(Case).filter(Case.id == case_id, Case.is_deleted == False).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    existing = db.query(AutopsyReport).filter(AutopsyReport.case_id == case_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Autopsy report already exists for this case")
    
    autopsy = AutopsyReport(
        case_id=case_id,
        performed_by=current_user.id,
        **autopsy_data.model_dump()
    )
    
    case.status = "in_progress"
    case.autopsy_started_at = datetime.utcnow()
    
    db.add(autopsy)
    db.commit()
    db.refresh(autopsy)
    
    return autopsy


@router.get("/autopsy", response_model=AutopsyReportResponse)
def get_autopsy_report(
    case_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get autopsy report for a case"""
    
    autopsy = db.query(AutopsyReport).filter(AutopsyReport.case_id == case_id).first()
    if not autopsy:
        raise HTTPException(status_code=404, detail="Autopsy report not found")
    
    return autopsy


@router.put("/autopsy", response_model=AutopsyReportResponse)
def update_autopsy_report(
    case_id: UUID,
    autopsy_data: AutopsyReportUpdate,
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """Update autopsy report"""
    
    autopsy = db.query(AutopsyReport).filter(AutopsyReport.case_id == case_id).first()
    if not autopsy:
        raise HTTPException(status_code=404, detail="Autopsy report not found")
    
    if autopsy.is_finalized:
        raise HTTPException(status_code=400, detail="Cannot edit finalized autopsy report")
    
    update_data = autopsy_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(autopsy, field, value)
    
    db.commit()
    db.refresh(autopsy)
    
    return autopsy


@router.post("/autopsy/finalize", response_model=AutopsyReportResponse)
def finalize_autopsy_report(
    case_id: UUID,
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """Finalize autopsy report (locks it from further edits)"""
    
    autopsy = db.query(AutopsyReport).filter(AutopsyReport.case_id == case_id).first()
    if not autopsy:
        raise HTTPException(status_code=404, detail="Autopsy report not found")
    
    if autopsy.is_finalized:
        raise HTTPException(status_code=400, detail="Autopsy report already finalized")
    
    if not autopsy.cause_of_death_immediate:
        raise HTTPException(status_code=400, detail="Cause of death is required to finalize")
    
    if not autopsy.manner_of_death:
        raise HTTPException(status_code=400, detail="Manner of death is required to finalize")
    
    autopsy.is_finalized = True
    autopsy.finalized_at = datetime.utcnow()
    
    case = db.query(Case).filter(Case.id == case_id).first()
    case.status = "completed"
    case.autopsy_completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(autopsy)
    
    return autopsy



@router.post("/injuries", response_model=InjuryResponse, status_code=status.HTTP_201_CREATED)
def add_injury(
    case_id: UUID,
    injury_data: InjuryCreate,
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """Add an injury to a case"""
    
    case = db.query(Case).filter(Case.id == case_id, Case.is_deleted == False).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    injury = Injury(case_id=case_id, **injury_data.model_dump())
    db.add(injury)
    db.commit()
    db.refresh(injury)
    
    return injury


@router.get("/injuries", response_model=List[InjuryResponse])
def list_injuries(
    case_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all injuries for a case"""
    
    injuries = db.query(Injury).filter(Injury.case_id == case_id).all()
    return injuries


@router.get("/injuries/{injury_id}", response_model=InjuryResponse)
def get_injury(
    case_id: UUID,
    injury_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific injury details"""
    
    injury = db.query(Injury).filter(
        Injury.id == injury_id,
        Injury.case_id == case_id
    ).first()
    
    if not injury:
        raise HTTPException(status_code=404, detail="Injury not found")
    
    return injury


@router.delete("/injuries/{injury_id}", response_model=MessageResponse)
def delete_injury(
    case_id: UUID,
    injury_id: UUID,
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """Delete an injury"""
    
    injury = db.query(Injury).filter(
        Injury.id == injury_id,
        Injury.case_id == case_id
    ).first()
    
    if not injury:
        raise HTTPException(status_code=404, detail="Injury not found")
    
    db.delete(injury)
    db.commit()
    
    return MessageResponse(message="Injury deleted successfully")
