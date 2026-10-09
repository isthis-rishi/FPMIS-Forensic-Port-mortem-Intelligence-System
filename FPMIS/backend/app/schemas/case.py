"""
FPMIS - Case & Autopsy Schemas
Pydantic models for Module 1
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal



class DeceasedInfoBase(BaseModel):
    is_identified: bool = False
    name: Optional[str] = None
    alias: Optional[str] = None
    age_years: Optional[int] = Field(None, ge=0, le=150)
    age_months: Optional[int] = Field(None, ge=0, le=11)
    age_estimated: bool = False
    gender: Optional[str] = Field(None, pattern="^(male|female|transgender|unknown)$")
    height_cm: Optional[Decimal] = None
    weight_kg: Optional[Decimal] = None
    build: Optional[str] = None
    complexion: Optional[str] = None
    hair_color: Optional[str] = None
    hair_length: Optional[str] = None
    eye_color: Optional[str] = None
    identification_marks: Optional[str] = None
    dental_features: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    relative_name: Optional[str] = None
    relative_relation: Optional[str] = None
    relative_phone: Optional[str] = None
    id_proof_type: Optional[str] = None
    id_proof_number: Optional[str] = None


class DeceasedInfoCreate(DeceasedInfoBase):
    pass


class DeceasedInfoUpdate(DeceasedInfoBase):
    pass


class DeceasedInfoResponse(DeceasedInfoBase):
    id: UUID
    case_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True



class InjuryBase(BaseModel):
    injury_type: str = Field(..., pattern="^(abrasion|bruise|laceration|incised_wound|stab_wound|gunshot_wound|burn|fracture|dislocation|bite_mark|ligature_mark|defense_wound|other)$")
    body_region: str
    body_side: Optional[str] = Field(None, pattern="^(left|right|midline|bilateral)$")
    length_cm: Optional[Decimal] = None
    width_cm: Optional[Decimal] = None
    depth_cm: Optional[Decimal] = None
    description: Optional[str] = None
    probable_weapon: Optional[str] = None
    age_of_injury: Optional[str] = None
    is_fatal: bool = False


class InjuryCreate(InjuryBase):
    pass


class InjuryResponse(InjuryBase):
    id: UUID
    case_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True



class AutopsyReportBase(BaseModel):
    assisted_by: Optional[str] = None
    general_appearance: Optional[str] = None
    clothing_description: Optional[str] = None
    post_mortem_changes: Optional[str] = None
    external_injuries: Optional[str] = None
    
    head_face_findings: Optional[str] = None
    neck_findings: Optional[str] = None
    chest_findings: Optional[str] = None
    abdomen_findings: Optional[str] = None
    back_findings: Optional[str] = None
    upper_limbs_findings: Optional[str] = None
    lower_limbs_findings: Optional[str] = None
    genitalia_findings: Optional[str] = None
    
    scalp_skull: Optional[str] = None
    brain_findings: Optional[str] = None
    brain_weight_gm: Optional[Decimal] = None
    
    neck_structures: Optional[str] = None
    hyoid_bone: Optional[str] = None
    thyroid_cartilage: Optional[str] = None
    
    chest_cavity: Optional[str] = None
    lungs_findings: Optional[str] = None
    lungs_weight_left_gm: Optional[Decimal] = None
    lungs_weight_right_gm: Optional[Decimal] = None
    heart_findings: Optional[str] = None
    heart_weight_gm: Optional[Decimal] = None
    major_vessels: Optional[str] = None
    
    abdominal_cavity: Optional[str] = None
    liver_findings: Optional[str] = None
    liver_weight_gm: Optional[Decimal] = None
    spleen_findings: Optional[str] = None
    spleen_weight_gm: Optional[Decimal] = None
    kidneys_findings: Optional[str] = None
    kidneys_weight_left_gm: Optional[Decimal] = None
    kidneys_weight_right_gm: Optional[Decimal] = None
    stomach_contents: Optional[str] = None
    intestines_findings: Optional[str] = None
    
    bladder_findings: Optional[str] = None
    uterus_findings: Optional[str] = None
    prostate_findings: Optional[str] = None
    spine_findings: Optional[str] = None
    spinal_cord: Optional[str] = None
    
    cause_of_death_immediate: Optional[str] = None
    cause_of_death_antecedent: Optional[str] = None
    cause_of_death_underlying: Optional[str] = None
    cause_of_death_contributing: Optional[str] = None
    manner_of_death: Optional[str] = Field(None, pattern="^(natural|accident|suicide|homicide|undetermined|pending)$")
    
    special_dissections: Optional[str] = None
    samples_collected: Optional[str] = None
    doctors_remarks: Optional[str] = None


class AutopsyReportCreate(AutopsyReportBase):
    pass


class AutopsyReportUpdate(AutopsyReportBase):
    is_finalized: Optional[bool] = None


class AutopsyReportResponse(AutopsyReportBase):
    id: UUID
    case_id: UUID
    performed_by: UUID
    is_finalized: bool
    finalized_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True



class CaseBase(BaseModel):
    case_type: Optional[str] = Field(None, pattern="^(medico_legal|natural_death|accident|crime|mass_disaster|unknown)$")
    priority: str = Field("normal", pattern="^(low|normal|high|urgent)$")
    police_station: Optional[str] = None
    fir_number: Optional[str] = None
    brought_by: Optional[str] = None
    body_received_at: Optional[datetime] = None


class CaseCreate(CaseBase):
    institution_id: UUID
    deceased_info: Optional[DeceasedInfoCreate] = None


class CaseUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(open|in_progress|pending_review|completed|closed)$")
    priority: Optional[str] = Field(None, pattern="^(low|normal|high|urgent)$")
    case_type: Optional[str] = None
    police_station: Optional[str] = None
    fir_number: Optional[str] = None
    assigned_doctor: Optional[UUID] = None
    autopsy_started_at: Optional[datetime] = None
    autopsy_completed_at: Optional[datetime] = None


class CaseResponse(CaseBase):
    id: UUID
    case_number: str
    institution_id: UUID
    status: str
    created_by: UUID
    assigned_doctor: Optional[UUID] = None
    autopsy_started_at: Optional[datetime] = None
    autopsy_completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CaseDetailResponse(CaseResponse):
    deceased_info: Optional[DeceasedInfoResponse] = None
    autopsy_report: Optional[AutopsyReportResponse] = None
    injuries: List[InjuryResponse] = []


class CaseListResponse(BaseModel):
    cases: List[CaseResponse]
    total: int
    page: int
    page_size: int
