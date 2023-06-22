from fastapi import APIRouter
from app.serializers.indicatorSerializer import indicatorListEntity
from app.database import Indicators


router = APIRouter()

@router.get("/")
async def get_indicators_current():
    pipeline = [
        {'$match': {"is_current": True}},
    ]
    indicators = indicatorListEntity(Indicators.aggregate(pipeline))
    return {'indicators': indicators}

@router.get("/{code}")
async def get_facility_indicators_current(code: int):
    pipeline = [
        {'$match': {"is_current": True, "mfl_code": code}},
    ]
    indicators = indicatorListEntity(Indicators.aggregate(pipeline))
    return {'indicators': indicators}