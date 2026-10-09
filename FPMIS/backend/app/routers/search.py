"""
FPMIS - Search & Intelligence Database Routes
Module 6: Searchable Case Database
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date, timedelta
from pydantic import BaseModel, Field

from app.models import Case, DeceasedInfo, AutopsyReport, User, get_db
from app.core import get_current_user

router = APIRouter(prefix="/search", tags=["Search & Intelligence"])



class SearchFilters(BaseModel):
    keyword: Optional[str] = None
    status: Optional[str] = None
    case_type: Optional[str] = None
    institution_id: Optional[UUID] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    gender: Optional[str] = None
    age_min: Optional[int] = Field(None, ge=0)
    age_max: Optional[int] = Field(None, le=150)
    is_identified: Optional[bool] = None
    district: Optional[str] = None
    manner_of_death: Optional[str] = None
    cause_keyword: Optional[str] = None


class SearchResult(BaseModel):
    id: UUID
    case_number: str
    status: str
    case_type: Optional[str] = None
    created_at: datetime
    deceased_name: Optional[str] = None
    deceased_age: Optional[int] = None
    deceased_gender: Optional[str] = None
    is_identified: bool = False
    district: Optional[str] = None
    cause_of_death: Optional[str] = None
    manner_of_death: Optional[str] = None

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    page: int
    page_size: int
    filters_applied: dict


class StatsSummary(BaseModel):
    total_cases: int
    by_status: dict
    by_manner_of_death: dict
    by_gender: dict
    by_district: List[dict]
    identified_vs_unidentified: dict
    recent_30_days: int



@router.post("", response_model=SearchResponse)
def advanced_search(
    filters: SearchFilters,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", pattern="^(created_at|case_number|age)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Advanced search with multiple filters"""
    
    query = db.query(Case).outerjoin(
        DeceasedInfo, DeceasedInfo.case_id == Case.id
    ).outerjoin(
        AutopsyReport, AutopsyReport.case_id == Case.id
    ).filter(Case.is_deleted == False)
    
    filters_applied = {}
    
    if filters.keyword:
        keyword = f"%{filters.keyword}%"
        query = query.filter(
            or_(
                Case.case_number.ilike(keyword),
                Case.fir_number.ilike(keyword),
                DeceasedInfo.name.ilike(keyword),
                DeceasedInfo.identification_marks.ilike(keyword),
                AutopsyReport.cause_of_death_immediate.ilike(keyword)
            )
        )
        filters_applied["keyword"] = filters.keyword
    
    if filters.status:
        query = query.filter(Case.status == filters.status)
        filters_applied["status"] = filters.status
    
    if filters.case_type:
        query = query.filter(Case.case_type == filters.case_type)
        filters_applied["case_type"] = filters.case_type
    
    if filters.institution_id:
        query = query.filter(Case.institution_id == filters.institution_id)
        filters_applied["institution_id"] = str(filters.institution_id)
    
    if filters.date_from:
        query = query.filter(Case.created_at >= datetime.combine(filters.date_from, datetime.min.time()))
        filters_applied["date_from"] = filters.date_from.isoformat()
    
    if filters.date_to:
        query = query.filter(Case.created_at <= datetime.combine(filters.date_to, datetime.max.time()))
        filters_applied["date_to"] = filters.date_to.isoformat()
    
    if filters.gender:
        query = query.filter(DeceasedInfo.gender == filters.gender)
        filters_applied["gender"] = filters.gender
    
    if filters.age_min is not None:
        query = query.filter(DeceasedInfo.age_years >= filters.age_min)
        filters_applied["age_min"] = filters.age_min
    
    if filters.age_max is not None:
        query = query.filter(DeceasedInfo.age_years <= filters.age_max)
        filters_applied["age_max"] = filters.age_max
    
    if filters.is_identified is not None:
        query = query.filter(DeceasedInfo.is_identified == filters.is_identified)
        filters_applied["is_identified"] = filters.is_identified
    
    if filters.district:
        query = query.filter(DeceasedInfo.district.ilike(f"%{filters.district}%"))
        filters_applied["district"] = filters.district
    
    if filters.manner_of_death:
        query = query.filter(AutopsyReport.manner_of_death == filters.manner_of_death)
        filters_applied["manner_of_death"] = filters.manner_of_death
    
    if filters.cause_keyword:
        cause_kw = f"%{filters.cause_keyword}%"
        query = query.filter(
            or_(
                AutopsyReport.cause_of_death_immediate.ilike(cause_kw),
                AutopsyReport.cause_of_death_antecedent.ilike(cause_kw)
            )
        )
        filters_applied["cause_keyword"] = filters.cause_keyword
    
    total = query.count()
    
    if sort_by == "created_at":
        sort_col = Case.created_at
    elif sort_by == "case_number":
        sort_col = Case.case_number
    else:
        sort_col = Case.created_at
    
    if sort_order == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())
    
    cases = query.offset((page - 1) * page_size).limit(page_size).all()
    
    results = []
    for case in cases:
        deceased = db.query(DeceasedInfo).filter(DeceasedInfo.case_id == case.id).first()
        autopsy = db.query(AutopsyReport).filter(AutopsyReport.case_id == case.id).first()
        
        results.append(SearchResult(
            id=case.id,
            case_number=case.case_number,
            status=case.status,
            case_type=case.case_type,
            created_at=case.created_at,
            deceased_name=deceased.name if deceased else None,
            deceased_age=deceased.age_years if deceased else None,
            deceased_gender=deceased.gender if deceased else None,
            is_identified=deceased.is_identified if deceased else False,
            district=deceased.district if deceased else None,
            cause_of_death=autopsy.cause_of_death_immediate if autopsy else None,
            manner_of_death=autopsy.manner_of_death if autopsy else None
        ))
    
    return SearchResponse(
        results=results,
        total=total,
        page=page,
        page_size=page_size,
        filters_applied=filters_applied
    )


@router.get("/quick", response_model=SearchResponse)
def quick_search(
    q: str = Query(..., min_length=2, description="Search query"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Quick search by keyword"""
    
    filters = SearchFilters(keyword=q)
    return advanced_search(filters, page, page_size, "created_at", "desc", current_user, db)


@router.get("/stats", response_model=StatsSummary)
def get_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get database statistics summary"""
    
    total_cases = db.query(Case).filter(Case.is_deleted == False).count()
    
    by_status = {}
    for status in ["open", "in_progress", "pending_review", "completed", "closed"]:
        by_status[status] = db.query(Case).filter(
            Case.status == status,
            Case.is_deleted == False
        ).count()
    
    by_manner = {}
    for manner in ["natural", "accident", "suicide", "homicide", "undetermined", "pending"]:
        by_manner[manner] = db.query(AutopsyReport).filter(
            AutopsyReport.manner_of_death == manner
        ).count()
    
    by_gender = {}
    for gender in ["male", "female", "transgender", "unknown"]:
        by_gender[gender] = db.query(DeceasedInfo).filter(
            DeceasedInfo.gender == gender
        ).count()
    
    district_counts = db.query(
        DeceasedInfo.district,
        func.count(DeceasedInfo.id).label('count')
    ).filter(
        DeceasedInfo.district.isnot(None)
    ).group_by(
        DeceasedInfo.district
    ).order_by(
        func.count(DeceasedInfo.id).desc()
    ).limit(10).all()
    
    by_district = [{"district": d.district, "count": d.count} for d in district_counts]
    
    identified = db.query(DeceasedInfo).filter(DeceasedInfo.is_identified == True).count()
    unidentified = db.query(DeceasedInfo).filter(DeceasedInfo.is_identified == False).count()
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent = db.query(Case).filter(
        Case.created_at >= thirty_days_ago,
        Case.is_deleted == False
    ).count()
    
    return StatsSummary(
        total_cases=total_cases,
        by_status=by_status,
        by_manner_of_death=by_manner,
        by_gender=by_gender,
        by_district=by_district,
        identified_vs_unidentified={"identified": identified, "unidentified": unidentified},
        recent_30_days=recent
    )


@router.get("/unidentified", response_model=List[SearchResult])
def get_unidentified_bodies(
    days: int = Query(None, ge=1, description="Filter by days since admission"),
    district: Optional[str] = None,
    gender: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of unidentified bodies"""
    
    query = db.query(Case).join(
        DeceasedInfo, DeceasedInfo.case_id == Case.id
    ).filter(
        Case.is_deleted == False,
        DeceasedInfo.is_identified == False
    )
    
    if days:
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = query.filter(Case.created_at <= cutoff)
    
    if district:
        query = query.filter(DeceasedInfo.district.ilike(f"%{district}%"))
    
    if gender:
        query = query.filter(DeceasedInfo.gender == gender)
    
    cases = query.order_by(Case.created_at.desc()).limit(100).all()
    
    results = []
    for case in cases:
        deceased = db.query(DeceasedInfo).filter(DeceasedInfo.case_id == case.id).first()
        
        results.append(SearchResult(
            id=case.id,
            case_number=case.case_number,
            status=case.status,
            case_type=case.case_type,
            created_at=case.created_at,
            deceased_name=None,
            deceased_age=deceased.age_years if deceased else None,
            deceased_gender=deceased.gender if deceased else None,
            is_identified=False,
            district=deceased.district if deceased else None,
            cause_of_death=None,
            manner_of_death=None
        ))
    
    return results
