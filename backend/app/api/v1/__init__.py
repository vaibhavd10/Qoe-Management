from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.projects import router as projects_router
# Import other routers as they are created

router = APIRouter()

# Include authentication routes
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# Include project routes
router.include_router(projects_router, prefix="/projects", tags=["Projects"])

# Additional routers would be included here:
# router.include_router(documents_router, prefix="/documents", tags=["Documents"])
# router.include_router(adjustments_router, prefix="/adjustments", tags=["Adjustments"])
# router.include_router(questions_router, prefix="/questions", tags=["Questions"])
# router.include_router(reports_router, prefix="/reports", tags=["Reports"])
# router.include_router(users_router, prefix="/users", tags=["Users"])