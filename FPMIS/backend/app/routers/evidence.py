"""
FPMIS - Evidence & Chain of Custody Routes
Module 4: Evidence Tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

from app.models import Case, EvidenceItem, ChainOfCustody, User, get_db
from app.core import get_current_user, require_staff

router = APIRouter(tags=["Evidence & Chain of Custody"])



class EvidenceCreate(BaseModel):
    evidence_number: str = Field(..., min_length=1, max_length=50)
    item_type: str = Field(..., pattern="^(biological_sample|clothing|weapon|document|electronic|toxicology_sample|dna_sample|photograph|personal_belongings|other)$")
    item_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    collected_from: Optional[str] = None
    collection_method: Optional[str] = None
    quantity: Optional[str] = None
    condition_when_collected: Optional[str] = None
    storage_location: Optional[str] = None
    storage_requirements: Optional[str] = None


class EvidenceUpdate(BaseModel):
    item_name: Optional[str] = None
    description: Optional[str] = None
    storage_location: Optional[str] = None
    storage_requirements: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(in_custody|sent_for_analysis|in_analysis|analysis_complete|returned|disposed|lost)$")
    analysis_result: Optional[str] = None


class EvidenceResponse(BaseModel):
    id: UUID
    case_id: UUID
    evidence_number: str
    item_type: str
    item_name: str
    description: Optional[str] = None
    status: str
    collected_from: Optional[str] = None
    storage_location: Optional[str] = None
    current_location: Optional[str] = None
    collected_by: UUID
    collected_at: datetime
    analysis_result: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CustodyTransfer(BaseModel):
    to_user_id: UUID
    to_location: str
    purpose: Optional[str] = None
    notes: Optional[str] = None
    condition_at_transfer: Optional[str] = None


class CustodyLogResponse(BaseModel):
    id: UUID
    evidence_id: UUID
    action_type: str
    from_user: Optional[UUID] = None
    to_user: Optional[UUID] = None
    performed_by: UUID
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    transfer_datetime: datetime
    condition_at_transfer: Optional[str] = None
    purpose: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    message: str
    success: bool = True



@router.post("/cases/{case_id}/evidence", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
def create_evidence(
    case_id: UUID,
    evidence_data: EvidenceCreate,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Add new evidence to a case"""
    
    case = db.query(Case).filter(Case.id == case_id, Case.is_deleted == False).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    existing = db.query(EvidenceItem).filter(
        EvidenceItem.case_id == case_id,
        EvidenceItem.evidence_number == evidence_data.evidence_number
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Evidence number already exists for this case")
    
    evidence = EvidenceItem(
        case_id=case_id,
        collected_by=current_user.id,
        collected_at=datetime.utcnow(),
        current_holder=current_user.id,
        current_location=evidence_data.storage_location,
        status="in_custody",
        **evidence_data.model_dump()
    )
    
    db.add(evidence)
    db.flush()
    
    custody_log = ChainOfCustody(
        evidence_id=evidence.id,
        action_type="collected",
        to_user=current_user.id,
        performed_by=current_user.id,
        to_location=evidence_data.storage_location or "Collection site",
        condition_at_transfer=evidence_data.condition_when_collected,
        purpose="Initial collection",
        transfer_datetime=datetime.utcnow()
    )
    
    db.add(custody_log)
    db.commit()
    db.refresh(evidence)
    
    return evidence


@router.get("/cases/{case_id}/evidence", response_model=List[EvidenceResponse])
def list_evidence(
    case_id: UUID,
    status: Optional[str] = None,
    item_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all evidence for a case"""
    
    query = db.query(EvidenceItem).filter(EvidenceItem.case_id == case_id)
    
    if status:
        query = query.filter(EvidenceItem.status == status)
    if item_type:
        query = query.filter(EvidenceItem.item_type == item_type)
    
    return query.order_by(EvidenceItem.collected_at.desc()).all()


@router.get("/evidence/{evidence_id}", response_model=EvidenceResponse)
def get_evidence(
    evidence_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get evidence details"""
    
    evidence = db.query(EvidenceItem).filter(EvidenceItem.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    return evidence


@router.put("/evidence/{evidence_id}", response_model=EvidenceResponse)
def update_evidence(
    evidence_id: UUID,
    evidence_data: EvidenceUpdate,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Update evidence details"""
    
    evidence = db.query(EvidenceItem).filter(EvidenceItem.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    update_data = evidence_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(evidence, field, value)
    
    db.commit()
    db.refresh(evidence)
    
    return evidence



@router.post("/evidence/{evidence_id}/transfer", response_model=CustodyLogResponse)
def transfer_evidence(
    evidence_id: UUID,
    transfer_data: CustodyTransfer,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Transfer evidence to another user"""
    
    evidence = db.query(EvidenceItem).filter(EvidenceItem.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    if evidence.current_holder != current_user.id:
        if current_user.role != "admin":
            raise HTTPException(
                status_code=403, 
                detail="Only the current holder or admin can transfer evidence"
            )
    
    recipient = db.query(User).filter(User.id == transfer_data.to_user_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient user not found")
    
    custody_log = ChainOfCustody(
        evidence_id=evidence_id,
        action_type="transferred",
        from_user=evidence.current_holder,
        to_user=transfer_data.to_user_id,
        performed_by=current_user.id,
        from_location=evidence.current_location,
        to_location=transfer_data.to_location,
        purpose=transfer_data.purpose,
        notes=transfer_data.notes,
        condition_at_transfer=transfer_data.condition_at_transfer,
        transfer_datetime=datetime.utcnow()
    )
    
    evidence.current_holder = transfer_data.to_user_id
    evidence.current_location = transfer_data.to_location
    
    db.add(custody_log)
    db.commit()
    db.refresh(custody_log)
    
    return custody_log


@router.post("/evidence/{evidence_id}/send-to-lab", response_model=CustodyLogResponse)
def send_to_lab(
    evidence_id: UUID,
    lab_name: str = Query(..., description="Name of the laboratory"),
    analysis_type: str = Query(..., description="Type of analysis requested"),
    notes: Optional[str] = None,
    current_user: User = Depends(require_staff),
    db: Session = Depends(get_db)
):
    """Send evidence to laboratory for analysis"""
    
    evidence = db.query(EvidenceItem).filter(EvidenceItem.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    custody_log = ChainOfCustody(
        evidence_id=evidence_id,
        action_type="sent_for_analysis",
        from_user=evidence.current_holder,
        performed_by=current_user.id,
        from_location=evidence.current_location,
        to_location=lab_name,
        purpose=f"Analysis: {analysis_type}",
        notes=notes,
        transfer_datetime=datetime.utcnow()
    )
    
    evidence.status = "sent_for_analysis"
    evidence.sent_to_lab = lab_name
    evidence.analysis_type = analysis_type
    evidence.current_location = lab_name
    
    db.add(custody_log)
    db.commit()
    db.refresh(custody_log)
    
    return custody_log


@router.get("/evidence/{evidence_id}/chain", response_model=List[CustodyLogResponse])
def get_chain_of_custody(
    evidence_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get complete chain of custody for evidence"""
    
    evidence = db.query(EvidenceItem).filter(EvidenceItem.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    chain = db.query(ChainOfCustody).filter(
        ChainOfCustody.evidence_id == evidence_id
    ).order_by(ChainOfCustody.transfer_datetime.asc()).all()
    
    return chain


@router.get("/my-evidence", response_model=List[EvidenceResponse])
def get_my_evidence(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all evidence currently held by the logged-in user"""
    
    evidence = db.query(EvidenceItem).filter(
        EvidenceItem.current_holder == current_user.id,
        EvidenceItem.status.in_(["in_custody", "in_analysis"])
    ).all()
    
    return evidence
