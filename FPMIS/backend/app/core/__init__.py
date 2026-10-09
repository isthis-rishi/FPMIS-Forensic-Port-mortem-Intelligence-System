"""
FPMIS - Core Module
Configuration and security utilities
"""

from .config import settings
from .security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token,
    get_current_user,
    get_current_active_user,
    require_roles,
    require_admin,
    require_doctor,
    require_staff,
)

__all__ = [
    "settings",
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "decode_token",
    "get_current_user",
    "get_current_active_user",
    "require_roles",
    "require_admin",
    "require_doctor",
    "require_staff",
]
