"""
FPMIS - API Routers
All route modules
"""

from .auth import router as auth_router
from .cases import router as cases_router
from .autopsy import router as autopsy_router
from .evidence import router as evidence_router
from .tod import router as tod_router
from .decomposition import router as decomposition_router
from .matching import router as matching_router
from .alerts import router as alerts_router
from .search import router as search_router

__all__ = [
    "auth_router",
    "cases_router",
    "autopsy_router",
    "evidence_router",
    "tod_router",
    "decomposition_router",
    "matching_router",
    "alerts_router",
    "search_router",
]
