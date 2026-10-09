"""
FPMIS - Case Management Routes
CRUD operations for cases (Module 1)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from uuid import UUID
from datetime import datetime

from app.models import Case, DeceasedInfo, User, get_db
from app.schemas import (
    CaseCreate, CaseUpdate, CaseResponse, CaseDetailResponse, CaseListResponse,
    DeceasedInfoCreate, DeceasedInfoUpdate, DeceasedInfoResponse,
    MessageResponse
)
from app.core import get_current_user, require_staff

router = APIRouter(prefix="/cases", tags=["Cases"])


def generate_case_number(db: Session) -> str:
    """Generate unique case number: FPMIS/YYYY/NNNNN"""
    year = datetime.now().year
    prefix = f"FPMIS/{year}/"
    
    latest = db.query(Case).filter(
        Case.case_number.like(f"{prefix}%")
    ).order_by(Case.case_number.desc()).first()
    
    if latest:
        last_num = int(latest.case_number.split("/")[-1])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f"{prefix}{str(new_num).zfill(5)}"


@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(
    case_data: CaseCreate,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Create a new case"""
    
    case_number = generate_case_number(db)
    
    new_case = Case(
        case_number=case_number,
        institution_id=case_data.institution_id,
        case_type=case_data.case_type,
        priority=case_data.priority,
        police_station=case_data.police_station,
        fir_number=case_data.fir_number,
        brought_by=case_data.brought_by,
        body_received_at=case_data.body_received_at,
        created_by=current_user.id,
        status="open"
    )
    
    db.add(new_case)
    db.flush()
    
    if case_data.deceased_info:
        deceased = DeceasedInfo(
            case_id=new_case.id,
            **case_data.deceased_info.model_dump()
        )
        db.add(deceased)
    
    db.commit()
    db.refresh(new_case)
    
    return new_case


@router.get("", response_model=CaseListResponse)
def list_cases(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    case_type: Optional[str] = None,
    search: Optional[str] = None,
    institution_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List cases with filtering and pagination"""
    
    query = db.query(Case).filter(Case.is_deleted == False)
    
    if status:
        query = query.filter(Case.status == status)
    if priority:
        query = query.filter(Case.priority == priority)
    if case_type:
        query = query.filter(Case.case_type == case_type)
    if institution_id:
        query = query.filter(Case.institution_id == institution_id)
    
    if search:
        query = query.filter(
            or_(
                Case.case_number.ilike(f"%{search}%"),
                Case.fir_number.ilike(f"%{search}%"),
                Case.police_station.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    
    cases = query.order_by(Case.created_at.desc())\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    return CaseListResponse(
        cases=cases,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{case_id}", response_model=CaseDetailResponse)
def get_case(
    case_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get case details with deceased info and autopsy report"""
    
    case = db.query(Case).filter(
        Case.id == case_id,
        Case.is_deleted == False
    ).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    return case


@router.put("/{case_id}", response_model=CaseResponse)
def update_case(
    case_id: UUID,
    case_data: CaseUpdate,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Update case details"""
    
    case = db.query(Case).filter(
        Case.id == case_id,
        Case.is_deleted == False
    ).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    update_data = case_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(case, field, value)
    
    db.commit()
    db.refresh(case)
    
    return case


@router.delete("/{case_id}", response_model=MessageResponse)
def delete_case(
    case_id: UUID,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Soft delete a case"""
    
    case = db.query(Case).filter(
        Case.id == case_id,
        Case.is_deleted == False
    ).first()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    case.is_deleted = True
    case.deleted_at = datetime.utcnow()
    db.commit()
    
    return MessageResponse(message="Case deleted successfully")



@router.post("/{case_id}/deceased", response_model=DeceasedInfoResponse, status_code=status.HTTP_201_CREATED)
def create_deceased_info(
    case_id: UUID,
    deceased_data: DeceasedInfoCreate,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Add deceased information to a case"""
    
    case = db.query(Case).filter(Case.id == case_id, Case.is_deleted == False).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    existing = db.query(DeceasedInfo).filter(DeceasedInfo.case_id == case_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Deceased info already exists for this case")
    
    deceased = DeceasedInfo(case_id=case_id, **deceased_data.model_dump())
    db.add(deceased)
    db.commit()
    db.refresh(deceased)
    
    return deceased


@router.put("/{case_id}/deceased", response_model=DeceasedInfoResponse)
def update_deceased_info(
    case_id: UUID,
    deceased_data: DeceasedInfoUpdate,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Update deceased information"""
    
    deceased = db.query(DeceasedInfo).filter(DeceasedInfo.case_id == case_id).first()
    if not deceased:
        raise HTTPException(status_code=404, detail="Deceased info not found")
    
    update_data = deceased_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(deceased, field, value)
    
    db.commit()
    db.refresh(deceased)
    
    return deceased
