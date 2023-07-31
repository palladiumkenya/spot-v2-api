from fastapi import APIRouter
from app.serializers.facilityMetricsSerializer import facilityMetricsListEntity
from app.database import FacilityMetrics


router = APIRouter()

@router.get("/{code}")
async def get_notices(code: int):
    pipeline = [
        {'$match': {"mfl_code": code, "is_current": True}},
    ]
    metrics = facilityMetricsListEntity(FacilityMetrics.aggregate(pipeline))
    return {'metrics': metrics}

