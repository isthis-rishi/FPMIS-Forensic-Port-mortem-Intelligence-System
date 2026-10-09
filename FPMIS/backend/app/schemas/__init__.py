"""
FPMIS - Pydantic Schemas
Request/Response validation models
"""

from .user import (
    InstitutionCreate,
    InstitutionUpdate,
    InstitutionResponse,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserWithInstitution,
    LoginRequest,
    TokenResponse,
    PasswordChange,
    PasswordReset,
    MessageResponse,
    ErrorResponse,
)

from .case import (
    DeceasedInfoCreate,
    DeceasedInfoUpdate,
    DeceasedInfoResponse,
    InjuryCreate,
    InjuryResponse,
    AutopsyReportCreate,
    AutopsyReportUpdate,
    AutopsyReportResponse,
    CaseCreate,
    CaseUpdate,
    CaseResponse,
    CaseDetailResponse,
    CaseListResponse,
)

__all__ = [
    "InstitutionCreate",
    "InstitutionUpdate", 
    "InstitutionResponse",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserWithInstitution",
    "LoginRequest",
    "TokenResponse",
    "PasswordChange",
    "PasswordReset",
    "MessageResponse",
    "ErrorResponse",
    "DeceasedInfoCreate",
    "DeceasedInfoUpdate",
    "DeceasedInfoResponse",
    "InjuryCreate",
    "InjuryResponse",
    "AutopsyReportCreate",
    "AutopsyReportUpdate",
    "AutopsyReportResponse",
    "CaseCreate",
    "CaseUpdate",
    "CaseResponse",
    "CaseDetailResponse",
    "CaseListResponse",
]
