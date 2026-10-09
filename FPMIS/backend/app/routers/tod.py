"""
FPMIS - Time of Death Estimation Routes
Module 2: TOD Calculator
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from decimal import Decimal

from app.models import Case, TimeOfDeathEstimation, User, get_db
from app.core import get_current_user, require_doctor

router = APIRouter(prefix="/cases/{case_id}/tod", tags=["Time of Death"])



class TODInput(BaseModel):
    """Input parameters for TOD calculation"""
    body_temperature_celsius: Optional[Decimal] = Field(None, ge=0, le=45)
    ambient_temperature_celsius: Optional[Decimal] = Field(None, ge=-20, le=60)
    body_weight_kg: Optional[Decimal] = Field(None, ge=1, le=300)
    clothing_description: Optional[str] = None
    body_position: Optional[str] = None
    environment: Optional[str] = Field(None, pattern="^(indoor|outdoor|water|buried|enclosed_space)$")
    
    rigor_mortis_jaw: Optional[int] = Field(None, ge=0, le=4)
    rigor_mortis_neck: Optional[int] = Field(None, ge=0, le=4)
    rigor_mortis_upper_limbs: Optional[int] = Field(None, ge=0, le=4)
    rigor_mortis_lower_limbs: Optional[int] = Field(None, ge=0, le=4)
    
    livor_mortis_present: Optional[bool] = None
    livor_mortis_color: Optional[str] = None
    livor_mortis_distribution: Optional[str] = None
    livor_mortis_fixed: Optional[bool] = None
    
    corneal_opacity: Optional[int] = Field(None, ge=0, le=4)
    tache_noire: Optional[bool] = None
    decomposition_started: Optional[bool] = None
    insect_activity: Optional[str] = None


class TODManualAdjust(BaseModel):
    """Manual adjustment to TOD"""
    manual_tod_min_hours: Decimal
    manual_tod_max_hours: Decimal
    adjustment_reason: str


class TODResponse(BaseModel):
    id: UUID
    case_id: UUID
    
    body_temperature_celsius: Optional[Decimal] = None
    ambient_temperature_celsius: Optional[Decimal] = None
    rigor_mortis_overall: Optional[int] = None
    livor_mortis_present: Optional[bool] = None
    livor_mortis_fixed: Optional[bool] = None
    
    estimated_tod_min_hours: Optional[Decimal] = None
    estimated_tod_max_hours: Optional[Decimal] = None
    estimated_tod_datetime_min: Optional[datetime] = None
    estimated_tod_datetime_max: Optional[datetime] = None
    confidence_level: Optional[str] = None
    calculation_reasoning: Optional[str] = None
    
    is_manually_adjusted: bool = False
    manual_adjustment_reason: Optional[str] = None
    
    calculated_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    message: str
    success: bool = True



def calculate_tod(input_data: TODInput, examination_time: datetime) -> dict:
    """
    Calculate estimated time of death based on input parameters
    Returns dict with results and reasoning
    """
    
    reasoning_parts = []
    estimates = []
    
    if input_data.body_temperature_celsius and input_data.ambient_temperature_celsius:
        body_temp = float(input_data.body_temperature_celsius)
        ambient_temp = float(input_data.ambient_temperature_celsius)
        
        if body_temp < 37:
            temp_drop = 37 - body_temp
            
            weight = float(input_data.body_weight_kg) if input_data.body_weight_kg else 70
            
            if weight < 50:
                cooling_rate = 1.5
            elif weight > 90:
                cooling_rate = 0.8
            else:
                cooling_rate = 1.2
            
            if input_data.environment == "water":
                cooling_rate *= 2
            elif input_data.environment == "outdoor" and ambient_temp < 10:
                cooling_rate *= 1.3
            
            hours_from_temp = temp_drop / cooling_rate
            estimates.append(("temperature", hours_from_temp - 2, hours_from_temp + 2))
            reasoning_parts.append(
                f"Body temp {body_temp}°C (drop of {temp_drop:.1f}°C) suggests ~{hours_from_temp:.1f} hours"
            )
    
    rigor_values = [
        input_data.rigor_mortis_jaw,
        input_data.rigor_mortis_neck,
        input_data.rigor_mortis_upper_limbs,
        input_data.rigor_mortis_lower_limbs
    ]
    rigor_values = [v for v in rigor_values if v is not None]
    
    if rigor_values:
        avg_rigor = sum(rigor_values) / len(rigor_values)
        
        rigor_ranges = {
            0: (0, 2, "Not present - very recent death"),
            1: (2, 6, "Developing - 2-6 hours"),
            2: (6, 12, "Full rigor - 6-12 hours"),
            3: (12, 24, "Passing - 12-24 hours"),
            4: (24, 48, "Absent (passed) - 24-48 hours")
        }
        
        rigor_stage = round(avg_rigor)
        r_min, r_max, r_desc = rigor_ranges.get(rigor_stage, (0, 48, "Unknown"))
        estimates.append(("rigor", r_min, r_max))
        reasoning_parts.append(f"Rigor mortis stage {rigor_stage} ({r_desc})")
    
    if input_data.livor_mortis_present is not None:
        if not input_data.livor_mortis_present:
            estimates.append(("livor", 0, 2))
            reasoning_parts.append("Livor mortis not present - very recent death (0-2 hours)")
        elif input_data.livor_mortis_fixed:
            estimates.append(("livor", 8, 48))
            reasoning_parts.append("Livor mortis fixed - at least 8 hours since death")
        else:
            estimates.append(("livor", 2, 8))
            reasoning_parts.append("Livor mortis present but not fixed - 2-8 hours")
    
    if input_data.corneal_opacity is not None:
        cornea_ranges = {
            0: (0, 3, "Clear - recent death"),
            1: (2, 6, "Slight haze"),
            2: (6, 12, "Moderate opacity"),
            3: (12, 24, "Marked opacity"),
            4: (24, 48, "Complete opacity")
        }
        c_min, c_max, c_desc = cornea_ranges.get(input_data.corneal_opacity, (0, 48, "Unknown"))
        estimates.append(("cornea", c_min, c_max))
        reasoning_parts.append(f"Corneal opacity level {input_data.corneal_opacity} ({c_desc})")
    
    if input_data.decomposition_started:
        estimates.append(("decomp", 24, 96))
        reasoning_parts.append("Decomposition started - likely 24+ hours")
    
    if not estimates:
        return {
            "min_hours": 0,
            "max_hours": 48,
            "confidence": "low",
            "reasoning": "Insufficient data for accurate estimation"
        }
    
    min_hours = max(e[1] for e in estimates)
    max_hours = min(e[2] for e in estimates)
    
    if min_hours > max_hours:
        all_mins = [e[1] for e in estimates]
        all_maxs = [e[2] for e in estimates]
        min_hours = sum(all_mins) / len(all_mins)
        max_hours = sum(all_maxs) / len(all_maxs)
    
    if len(estimates) >= 3 and (max_hours - min_hours) < 6:
        confidence = "high"
    elif len(estimates) >= 2 and (max_hours - min_hours) < 12:
        confidence = "medium"
    else:
        confidence = "low"
    
    tod_max = examination_time - timedelta(hours=float(min_hours))
    tod_min = examination_time - timedelta(hours=float(max_hours))
    
    reasoning = ". ".join(reasoning_parts)
    reasoning += f". Estimated death occurred {min_hours:.1f}-{max_hours:.1f} hours before examination."
    
    return {
        "min_hours": round(min_hours, 1),
        "max_hours": round(max_hours, 1),
        "tod_datetime_min": tod_min,
        "tod_datetime_max": tod_max,
        "confidence": confidence,
        "reasoning": reasoning
    }



@router.post("", response_model=TODResponse, status_code=status.HTTP_201_CREATED)
def calculate_time_of_death(
    case_id: UUID,
    tod_input: TODInput,
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """Calculate time of death for a case"""
    
    case = db.query(Case).filter(Case.id == case_id, Case.is_deleted == False).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    existing = db.query(TimeOfDeathEstimation).filter(TimeOfDeathEstimation.case_id == case_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="TOD estimation already exists. Use PUT to update.")
    
    examination_time = case.body_received_at or datetime.utcnow()
    result = calculate_tod(tod_input, examination_time)
    
    rigor_values = [
        tod_input.rigor_mortis_jaw,
        tod_input.rigor_mortis_neck,
        tod_input.rigor_mortis_upper_limbs,
        tod_input.rigor_mortis_lower_limbs
    ]
    rigor_values = [v for v in rigor_values if v is not None]
    rigor_overall = round(sum(rigor_values) / len(rigor_values)) if rigor_values else None
    
    tod = TimeOfDeathEstimation(
        case_id=case_id,
        calculated_by=current_user.id,
        calculated_at=datetime.utcnow(),
        
        body_temperature_celsius=tod_input.body_temperature_celsius,
        ambient_temperature_celsius=tod_input.ambient_temperature_celsius,
        body_weight_kg=tod_input.body_weight_kg,
        clothing_description=tod_input.clothing_description,
        body_position=tod_input.body_position,
        environment=tod_input.environment,
        
        rigor_mortis_jaw=tod_input.rigor_mortis_jaw,
        rigor_mortis_neck=tod_input.rigor_mortis_neck,
        rigor_mortis_upper_limbs=tod_input.rigor_mortis_upper_limbs,
        rigor_mortis_lower_limbs=tod_input.rigor_mortis_lower_limbs,
        rigor_mortis_overall=rigor_overall,
        
        livor_mortis_present=tod_input.livor_mortis_present,
        livor_mortis_color=tod_input.livor_mortis_color,
        livor_mortis_distribution=tod_input.livor_mortis_distribution,
        livor_mortis_fixed=tod_input.livor_mortis_fixed,
        
        corneal_opacity=tod_input.corneal_opacity,
        tache_noire=tod_input.tache_noire,
        decomposition_started=tod_input.decomposition_started,
        insect_activity=tod_input.insect_activity,
        
        estimated_tod_min_hours=Decimal(str(result["min_hours"])),
        estimated_tod_max_hours=Decimal(str(result["max_hours"])),
        estimated_tod_datetime_min=result["tod_datetime_min"],
        estimated_tod_datetime_max=result["tod_datetime_max"],
        confidence_level=result["confidence"],
        calculation_reasoning=result["reasoning"],
        calculation_method="FPMIS Rule-Based v1.0"
    )
    
    db.add(tod)
    db.commit()
    db.refresh(tod)
    
    return tod


@router.get("", response_model=TODResponse)
def get_time_of_death(
    case_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get TOD estimation for a case"""
    
    tod = db.query(TimeOfDeathEstimation).filter(TimeOfDeathEstimation.case_id == case_id).first()
    if not tod:
        raise HTTPException(status_code=404, detail="TOD estimation not found")
    
    return tod


@router.put("", response_model=TODResponse)
def update_time_of_death(
    case_id: UUID,
    tod_input: TODInput,
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """Recalculate TOD with new parameters"""
    
    tod = db.query(TimeOfDeathEstimation).filter(TimeOfDeathEstimation.case_id == case_id).first()
    if not tod:
        raise HTTPException(status_code=404, detail="TOD estimation not found. Use POST to create.")
    
    case = db.query(Case).filter(Case.id == case_id).first()
    examination_time = case.body_received_at or datetime.utcnow()
    
    result = calculate_tod(tod_input, examination_time)
    
    input_data = tod_input.model_dump(exclude_unset=True)
    for field, value in input_data.items():
        setattr(tod, field, value)
    
    tod.estimated_tod_min_hours = Decimal(str(result["min_hours"]))
    tod.estimated_tod_max_hours = Decimal(str(result["max_hours"]))
    tod.estimated_tod_datetime_min = result["tod_datetime_min"]
    tod.estimated_tod_datetime_max = result["tod_datetime_max"]
    tod.confidence_level = result["confidence"]
    tod.calculation_reasoning = result["reasoning"]
    tod.calculated_at = datetime.utcnow()
    tod.is_manually_adjusted = False
    
    db.commit()
    db.refresh(tod)
    
    return tod


@router.post("/adjust", response_model=TODResponse)
def manually_adjust_tod(
    case_id: UUID,
    adjustment: TODManualAdjust,
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """Manually adjust TOD estimation"""
    
    tod = db.query(TimeOfDeathEstimation).filter(TimeOfDeathEstimation.case_id == case_id).first()
    if not tod:
        raise HTTPException(status_code=404, detail="TOD estimation not found")
    
    case = db.query(Case).filter(Case.id == case_id).first()
    examination_time = case.body_received_at or datetime.utcnow()
    
    tod_max = examination_time - timedelta(hours=float(adjustment.manual_tod_min_hours))
    tod_min = examination_time - timedelta(hours=float(adjustment.manual_tod_max_hours))
    
    tod.is_manually_adjusted = True
    tod.manual_tod_min = tod_min
    tod.manual_tod_max = tod_max
    tod.manual_adjustment_reason = adjustment.adjustment_reason
    tod.estimated_tod_min_hours = adjustment.manual_tod_min_hours
    tod.estimated_tod_max_hours = adjustment.manual_tod_max_hours
    tod.estimated_tod_datetime_min = tod_min
    tod.estimated_tod_datetime_max = tod_max
    tod.calculation_reasoning = f"Manually adjusted: {adjustment.adjustment_reason}"
    
    db.commit()
    db.refresh(tod)
    
    return tod
