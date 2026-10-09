"""
FPMIS - User & Auth Schemas
Pydantic models for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime



class InstitutionBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    type: str = Field(..., pattern="^(hospital|medical_college|laboratory|mortuary|police_station|other)$")
    address: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class InstitutionCreate(InstitutionBase):
    pass


class InstitutionUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    address: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class InstitutionResponse(InstitutionBase):
    id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True



class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    role: str = Field(..., pattern="^(admin|forensic_doctor|lab_technician|mortuary_staff|investigator|viewer)$")
    institution_id: Optional[UUID] = None
    phone: Optional[str] = None
    designation: Optional[str] = None
    license_number: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    designation: Optional[str] = None
    license_number: Optional[str] = None
    institution_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: UUID
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserWithInstitution(UserResponse):
    institution: Optional[InstitutionResponse] = None



class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6, max_length=100)


class PasswordReset(BaseModel):
    email: EmailStr



class MessageResponse(BaseModel):
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    detail: str
    success: bool = False
