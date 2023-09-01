from fastapi import APIRouter
from app.serializers.profileSerializer import profileListEntity
from app.serializers.facilityMetricsSerializer import facilityMetricsListEntity
from app.serializers.indicatorSerializer import indicatorListEntity
from app.database import Profiles, FacilityMetrics, Indicators


router = APIRouter()

@router.get("/")
async def get_profiles():
    # Retrieve profiles, facility metrics, and indicator metrics concurrently
    profiles = profileListEntity(Profiles.find())
    dwapi_metrics = facilityMetricsListEntity(FacilityMetrics.find({"is_current": True, 'metric': 'DWAPI Version'}))
    indicator_metrics = indicatorListEntity(Indicators.find({"is_current": True, 'name': 'EMR_ETL_Refresh'}))

    # Create dictionaries of DWAPI versions and ETL dates using dictionary comprehensions
    dwapi_versions = {metric['mfl_code']: metric['value'] for metric in dwapi_metrics}
    etl_dates = {metric['mfl_code']: metric['emr_value'] for metric in indicator_metrics}
    
    # Update profiles with DWAPI versions and ETL dates where available
    for profile in profiles:
        mfl_code = profile['mfl_code']
        if mfl_code in dwapi_versions:
            profile['dwapi_version'] = dwapi_versions[mfl_code]
        if mfl_code in etl_dates:
            profile['emr_etl_date'] = etl_dates[mfl_code]

    # Return the updated profiles
    return {'profiles': profiles}

