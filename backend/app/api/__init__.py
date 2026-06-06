from fastapi import APIRouter

from .auth import router as auth_router
from .templates import router as templates_router
from .records import router as records_router
from .plans import router as plans_router
from .audit import router as audit_router
from .overview import router as overview_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["认证"])
api_router.include_router(templates_router, prefix="/templates", tags=["随访模板"])
api_router.include_router(records_router, prefix="/records", tags=["随访记录"])
api_router.include_router(plans_router, prefix="/plans", tags=["回访计划"])
api_router.include_router(audit_router, prefix="/audit", tags=["审计与告警"])
api_router.include_router(overview_router, prefix="/overview", tags=["患者概览"])
