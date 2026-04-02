from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.schemas import AnalyticsSummary
from models.enums import UserRole
from services.analytics_service import AnalyticsService
from decorators.auth import require_role

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/summary", response_model=AnalyticsSummary)
def get_analytics_summary(
    db: Session = Depends(get_db),
    admin=Depends(require_role(UserRole.ADMIN))
):
    analytics_service = AnalyticsService(db)
    return analytics_service.get_summary()
