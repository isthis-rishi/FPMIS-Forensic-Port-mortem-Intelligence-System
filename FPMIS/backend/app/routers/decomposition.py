"""
FPMIS - Decomposition Logging Routes
Module 3: Decomposition & Environmental Tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from decimal import Decimal

from app.models import Case, DecompositionLog, User, get_db
from app.core import get_current_user, require_staff

router = APIRouter(prefix="/cases/{case_id}/decomposition", tags=["Decomposition"])



class DecompositionCreate(BaseModel):
    stage: str = Field(..., pattern="^(fresh|early_decomposition|bloat|active_decay|advanced_decay|dry_remains|skeletonization)$")
    
    temperature_celsius: Optional[Decimal] = Field(None, ge=-20, le=60)
    humidity_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    weather_condition: Optional[str] = None
    location_type: Optional[str] = Field(None, pattern="^(indoor|outdoor|water|buried|vehicle|other)$")
    sun_exposure: Optional[str] = Field(None, pattern="^(none|partial|full)$")
    
    skin_changes: Optional[str] = None
    discoloration: Optional[str] = None
    bloating_level: Optional[str] = None
    purging_present: Optional[bool] = None
    marbling_present: Optional[bool] = None
    skin_slippage: Optional[bool] = None
    
    insect_activity_present: Optional[bool] = None
    insect_types: Optional[str] = None
    maggot_mass_present: Optional[bool] = None
    maggot_stage: Optional[str] = None
    
    odor_level: Optional[str] = Field(None, pattern="^(none|slight|moderate|strong|overwhelming)$")
    animal_activity: Optional[str] = None
    additional_observations: Optional[str] = None


class DecompositionResponse(BaseModel):
    id: UUID
    case_id: UUID
    stage: str
    stage_numeric: Optional[int] = None
    temperature_celsius: Optional[Decimal] = None
    humidity_percent: Optional[Decimal] = None
    location_type: Optional[str] = None
    insect_activity_present: Optional[bool] = None
    maggot_mass_present: Optional[bool] = None
    odor_level: Optional[str] = None
    additional_observations: Optional[str] = None
    logged_by: UUID
    logged_at: datetime

    class Config:
        from_attributes = True


class StageInfo(BaseModel):
    stage: str
    stage_numeric: int
    description: str
    typical_timeframe: str


class MessageResponse(BaseModel):
    message: str
    success: bool = True



STAGES = {
    "fresh": {
        "numeric": 1,
        "description": "No visible signs of decomposition. Body appears normal. Algor mortis (cooling) and livor mortis beginning.",
        "typical_timeframe": "0-24 hours"
    },
    "early_decomposition": {
        "numeric": 2,
        "description": "Slight skin discoloration (greenish on abdomen). Early bloating may begin. Skin slip starting.",
        "typical_timeframe": "1-3 days"
    },
    "bloat": {
        "numeric": 3,
        "description": "Significant bloating due to gas buildup. Skin marbling visible. Purging of fluids may occur. Strong odor.",
        "typical_timeframe": "3-7 days"
    },
    "active_decay": {
        "numeric": 4,
        "description": "Major tissue breakdown. Heavy insect activity. Maggot masses present. Skin breaking down. Very strong odor.",
        "typical_timeframe": "1-3 weeks"
    },
    "advanced_decay": {
        "numeric": 5,
        "description": "Most soft tissue gone. Bones becoming exposed. Decreased insect activity. Cartilage decomposing.",
        "typical_timeframe": "3-6 weeks"
    },
    "dry_remains": {
        "numeric": 6,
        "description": "Mostly skeletal with some dried skin/tissue remaining. Minimal odor. Hair and nails may still be present.",
        "typical_timeframe": "1-6 months"
    },
    "skeletonization": {
        "numeric": 7,
        "description": "Only bones remain. All soft tissue decomposed. Bones may show weathering.",
        "typical_timeframe": "6+ months"
    }
}



@router.post("", response_model=DecompositionResponse, status_code=status.HTTP_201_CREATED)
def log_decomposition(
    case_id: UUID,
    log_data: DecompositionCreate,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Add a new decomposition observation log"""
    
    case = db.query(Case).filter(Case.id == case_id, Case.is_deleted == False).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    stage_info = STAGES.get(log_data.stage, {})
    stage_numeric = stage_info.get("numeric", 0)
    
    log = DecompositionLog(
        case_id=case_id,
        logged_by=current_user.id,
        logged_at=datetime.utcnow(),
        stage_numeric=stage_numeric,
        **log_data.model_dump()
    )
    
    db.add(log)
    db.commit()
    db.refresh(log)
    
    return log


@router.get("", response_model=List[DecompositionResponse])
def list_decomposition_logs(
    case_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all decomposition logs for a case (chronological)"""
    
    logs = db.query(DecompositionLog).filter(
        DecompositionLog.case_id == case_id
    ).order_by(DecompositionLog.logged_at.asc()).all()
    
    return logs


@router.get("/latest", response_model=DecompositionResponse)
def get_latest_decomposition(
    case_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the most recent decomposition log"""
    
    log = db.query(DecompositionLog).filter(
        DecompositionLog.case_id == case_id
    ).order_by(DecompositionLog.logged_at.desc()).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="No decomposition logs found")
    
    return log


@router.get("/stages", response_model=List[StageInfo])
def get_decomposition_stages():
    """Get list of all decomposition stages with descriptions"""
    
    return [
        StageInfo(
            stage=stage,
            stage_numeric=info["numeric"],
            description=info["description"],
            typical_timeframe=info["typical_timeframe"]
        )
        for stage, info in STAGES.items()
    ]


@router.delete("/{log_id}", response_model=MessageResponse)
def delete_decomposition_log(
    case_id: UUID,
    log_id: UUID,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Delete a decomposition log"""
    
    log = db.query(DecompositionLog).filter(
        DecompositionLog.id == log_id,
        DecompositionLog.case_id == case_id
    ).first()
    
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    
    db.delete(log)
    db.commit()
    
    return MessageResponse(message="Decomposition log deleted")
