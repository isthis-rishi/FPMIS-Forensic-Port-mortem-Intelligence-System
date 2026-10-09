"""
FPMIS - Missing Person & Body Matching Routes
Module 5: Body Identification
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date
from pydantic import BaseModel, Field
from decimal import Decimal

from app.models import MissingPerson, BodyMatchResult, Case, DeceasedInfo, User, get_db
from app.core import get_current_user, require_staff

router = APIRouter(tags=["Missing Persons & Matching"])



class MissingPersonCreate(BaseModel):
    reported_by: str = Field(..., min_length=2)
    reporter_relation: Optional[str] = None
    reporter_phone: Optional[str] = None
    reporter_address: Optional[str] = None
    
    name: str = Field(..., min_length=2)
    alias: Optional[str] = None
    age_years: Optional[int] = Field(None, ge=0, le=150)
    age_approximate: bool = False
    gender: Optional[str] = Field(None, pattern="^(male|female|transgender|unknown)$")
    
    height_cm_min: Optional[Decimal] = None
    height_cm_max: Optional[Decimal] = None
    weight_kg_min: Optional[Decimal] = None
    weight_kg_max: Optional[Decimal] = None
    build: Optional[str] = None
    complexion: Optional[str] = None
    hair_color: Optional[str] = None
    hair_style: Optional[str] = None
    eye_color: Optional[str] = None
    
    identification_marks: Optional[str] = None
    scars: Optional[str] = None
    tattoos: Optional[str] = None
    birthmarks: Optional[str] = None
    dental_features: Optional[str] = None
    deformities: Optional[str] = None
    
    last_seen_date: date
    last_seen_location: Optional[str] = None
    last_seen_district: Optional[str] = None
    last_seen_state: Optional[str] = None
    last_seen_wearing: Optional[str] = None
    
    medical_conditions: Optional[str] = None
    
    police_station: Optional[str] = None
    fir_number: Optional[str] = None


class MissingPersonResponse(BaseModel):
    id: UUID
    report_number: str
    name: str
    age_years: Optional[int] = None
    gender: Optional[str] = None
    height_cm_min: Optional[Decimal] = None
    height_cm_max: Optional[Decimal] = None
    identification_marks: Optional[str] = None
    last_seen_date: date
    last_seen_location: Optional[str] = None
    last_seen_district: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class MatchResultResponse(BaseModel):
    id: Optional[UUID] = None
    case_id: UUID
    missing_person_id: UUID
    match_score_percent: Decimal
    confidence_level: Optional[str] = None
    score_breakdown: Optional[dict] = None
    status: str
    matched_at: datetime
    
    missing_person_name: Optional[str] = None
    case_number: Optional[str] = None

    class Config:
        from_attributes = True


class MatchConfirm(BaseModel):
    confirmation_method: str = Field(..., description="DNA, visual, dental, fingerprint, etc.")
    notes: Optional[str] = None


class MessageResponse(BaseModel):
    message: str
    success: bool = True



def generate_report_number(db: Session) -> str:
    """Generate unique missing person report number"""
    year = datetime.now().year
    prefix = f"MP/{year}/"
    
    latest = db.query(MissingPerson).filter(
        MissingPerson.report_number.like(f"{prefix}%")
    ).order_by(MissingPerson.report_number.desc()).first()
    
    if latest:
        last_num = int(latest.report_number.split("/")[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f"{prefix}{str(new_num).zfill(5)}"


def calculate_match_score(missing: MissingPerson, deceased: DeceasedInfo) -> dict:
    """Calculate match score between missing person and deceased"""
    
    score = 0
    max_score = 0
    breakdown = {}
    
    max_score += 20
    if missing.gender and deceased.gender:
        if missing.gender == deceased.gender:
            score += 20
            breakdown["gender"] = {"score": 20, "max": 20, "match": True}
        else:
            breakdown["gender"] = {"score": 0, "max": 20, "match": False, "reason": "Gender mismatch"}
            return {"score": 0, "max_score": 100, "percentage": 0, "confidence": "low", "breakdown": breakdown}
    
    max_score += 15
    if missing.age_years and deceased.age_years:
        age_diff = abs(missing.age_years - deceased.age_years)
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
    if deceased.height_cm and (missing.height_cm_min or missing.height_cm_max):
        d_height = float(deceased.height_cm)
        m_min = float(missing.height_cm_min) if missing.height_cm_min else d_height - 10
        m_max = float(missing.height_cm_max) if missing.height_cm_max else d_height + 10
        
        if m_min <= d_height <= m_max:
            score += 15
            breakdown["height"] = {"score": 15, "max": 15, "in_range": True}
        elif abs(d_height - m_min) <= 5 or abs(d_height - m_max) <= 5:
            score += 8
            breakdown["height"] = {"score": 8, "max": 15, "close": True}
        else:
            breakdown["height"] = {"score": 0, "max": 15, "in_range": False}
    
    max_score += 10
    if missing.build and deceased.build:
        if missing.build.lower() == deceased.build.lower():
            score += 10
            breakdown["build"] = {"score": 10, "max": 10, "match": True}
        else:
            breakdown["build"] = {"score": 0, "max": 10, "match": False}
    
    max_score += 10
    if missing.hair_color and deceased.hair_color:
        if missing.hair_color.lower() == deceased.hair_color.lower():
            score += 10
            breakdown["hair_color"] = {"score": 10, "max": 10, "match": True}
        else:
            breakdown["hair_color"] = {"score": 0, "max": 10, "match": False}
    
    max_score += 10
    if missing.complexion and deceased.complexion:
        if missing.complexion.lower() == deceased.complexion.lower():
            score += 10
            breakdown["complexion"] = {"score": 10, "max": 10, "match": True}
        else:
            breakdown["complexion"] = {"score": 0, "max": 10, "match": False}
    
    max_score += 20
    mp_marks = " ".join(filter(None, [
        missing.identification_marks, missing.scars, 
        missing.tattoos, missing.birthmarks
    ])).lower()
    dec_marks = (deceased.identification_marks or "").lower()
    
    if mp_marks and dec_marks:
        mp_words = set(mp_marks.split())
        dec_words = set(dec_marks.split())
        common = mp_words.intersection(dec_words)
        
        common = common - {"the", "a", "an", "on", "in", "at", "and", "or", "of"}
        
        if len(common) >= 3:
            score += 20
            breakdown["marks"] = {"score": 20, "max": 20, "common": list(common)[:5]}
        elif len(common) >= 1:
            score += 10
            breakdown["marks"] = {"score": 10, "max": 20, "common": list(common)}
        else:
            breakdown["marks"] = {"score": 0, "max": 20, "common": []}
    
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



@router.post("/missing-persons", response_model=MissingPersonResponse, status_code=status.HTTP_201_CREATED)
def create_missing_person(
    mp_data: MissingPersonCreate,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Register a new missing person report"""
    
    report_number = generate_report_number(db)
    
    mp = MissingPerson(
        report_number=report_number,
        entered_by=current_user.id,
        status="active",
        **mp_data.model_dump()
    )
    
    db.add(mp)
    db.commit()
    db.refresh(mp)
    
    return mp


@router.get("/missing-persons", response_model=List[MissingPersonResponse])
def list_missing_persons(
    status: Optional[str] = Query(None, pattern="^(active|found_alive|found_deceased|closed)$"),
    gender: Optional[str] = None,
    district: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List missing persons with filters"""
    
    query = db.query(MissingPerson)
    
    if status:
        query = query.filter(MissingPerson.status == status)
    if gender:
        query = query.filter(MissingPerson.gender == gender)
    if district:
        query = query.filter(MissingPerson.last_seen_district.ilike(f"%{district}%"))
    if search:
        query = query.filter(
            or_(
                MissingPerson.name.ilike(f"%{search}%"),
                MissingPerson.report_number.ilike(f"%{search}%")
            )
        )
    
    return query.order_by(MissingPerson.created_at.desc())\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()


@router.get("/missing-persons/{mp_id}", response_model=MissingPersonResponse)
def get_missing_person(
    mp_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get missing person details"""
    
    mp = db.query(MissingPerson).filter(MissingPerson.id == mp_id).first()
    if not mp:
        raise HTTPException(status_code=404, detail="Missing person not found")
    
    return mp



@router.post("/cases/{case_id}/find-matches", response_model=List[MatchResultResponse])
def find_matches_for_case(
    case_id: UUID,
    min_score: int = Query(30, ge=0, le=100, description="Minimum match score"),
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Find potential missing person matches for an unidentified body"""
    
    case = db.query(Case).filter(Case.id == case_id, Case.is_deleted == False).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    deceased = db.query(DeceasedInfo).filter(DeceasedInfo.case_id == case_id).first()
    if not deceased:
        raise HTTPException(status_code=400, detail="Deceased info not found")
    
    if deceased.is_identified:
        raise HTTPException(status_code=400, detail="Body is already identified")
    
    missing_persons = db.query(MissingPerson).filter(MissingPerson.status == "active").all()
    
    matches = []
    for mp in missing_persons:
        result = calculate_match_score(mp, deceased)
        
        if result["percentage"] >= min_score:
            existing = db.query(BodyMatchResult).filter(
                BodyMatchResult.case_id == case_id,
                BodyMatchResult.missing_person_id == mp.id
            ).first()
            
            if existing:
                existing.match_score_percent = Decimal(str(result["percentage"]))
                existing.confidence_level = result["confidence"]
                existing.score_breakdown = result["breakdown"]
                existing.matched_at = datetime.utcnow()
                match_obj = existing
            else:
                match_obj = BodyMatchResult(
                    case_id=case_id,
                    missing_person_id=mp.id,
                    match_score_percent=Decimal(str(result["percentage"])),
                    confidence_level=result["confidence"],
                    score_breakdown=result["breakdown"],
                    status="pending",
                    algorithm_version="FPMIS v1.0",
                    matched_at=datetime.utcnow()
                )
                db.add(match_obj)
                db.flush()
            
            matches.append({
                "id": match_obj.id,
                "case_id": case_id,
                "missing_person_id": mp.id,
                "match_score_percent": result["percentage"],
                "confidence_level": result["confidence"],
                "score_breakdown": result["breakdown"],
                "status": "pending",
                "matched_at": datetime.utcnow(),
                "missing_person_name": mp.name,
                "case_number": case.case_number
            })
    
    db.commit()
    
    matches.sort(key=lambda x: x["match_score_percent"], reverse=True)
    
    return matches


@router.get("/cases/{case_id}/matches", response_model=List[MatchResultResponse])
def get_case_matches(
    case_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all potential matches for a case"""
    
    matches = db.query(BodyMatchResult).filter(
        BodyMatchResult.case_id == case_id
    ).order_by(BodyMatchResult.match_score_percent.desc()).all()
    
    result = []
    for match in matches:
        mp = db.query(MissingPerson).filter(MissingPerson.id == match.missing_person_id).first()
        case = db.query(Case).filter(Case.id == match.case_id).first()
        
        result.append({
            **match.to_dict(),
            "missing_person_name": mp.name if mp else None,
            "case_number": case.case_number if case else None
        })
    
    return result


@router.post("/matches/{match_id}/confirm", response_model=MessageResponse)
def confirm_match(
    match_id: UUID,
    confirm_data: MatchConfirm,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Confirm a match between unidentified body and missing person"""
    
    match = db.query(BodyMatchResult).filter(BodyMatchResult.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    match.status = "confirmed"
    match.confirmed_by = current_user.id
    match.confirmed_at = datetime.utcnow()
    match.confirmation_method = confirm_data.confirmation_method
    match.review_notes = confirm_data.notes
    
    mp = db.query(MissingPerson).filter(MissingPerson.id == match.missing_person_id).first()
    mp.status = "found_deceased"
    mp.matched_case_id = match.case_id
    
    deceased = db.query(DeceasedInfo).filter(DeceasedInfo.case_id == match.case_id).first()
    deceased.is_identified = True
    deceased.name = mp.name
    
    db.query(BodyMatchResult).filter(
        BodyMatchResult.case_id == match.case_id,
        BodyMatchResult.id != match_id
    ).update({"status": "rejected"})
    
    db.commit()
    
    return MessageResponse(message=f"Match confirmed. {mp.name} identified.")


@router.post("/matches/{match_id}/reject", response_model=MessageResponse)
def reject_match(
    match_id: UUID,
    reason: Optional[str] = None,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Reject a potential match"""
    
    match = db.query(BodyMatchResult).filter(BodyMatchResult.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    match.status = "rejected"
    match.reviewed_by = current_user.id
    match.reviewed_at = datetime.utcnow()
    match.review_notes = reason
    
    db.commit()
    
    return MessageResponse(message="Match rejected")
