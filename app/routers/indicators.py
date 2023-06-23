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
	dwh_values = [item["dwh_value"] for item in indicators]
	emr_values = [item["emr_value"] for item in indicators]
	names = [item["name"] for item in indicators]
	dwh_dates = [item["dwh_indicator_date"] for item in indicators]
	emr_dates = [item["emr_indicator_date"] for item in indicators]
	result = {
		"dwh_values": dwh_values,
		"emr_values": emr_values,
		"names": names,
		"dwh_dates": dwh_dates,
		"emr_dates": emr_dates
	}

	return {'indicators': result}