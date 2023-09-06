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
    indicator_metrics = indicatorListEntity(Indicators.find({"is_current": True}))

    # Create dictionaries of DWAPI versions and ETL dates using dictionary comprehensions
    dwapi_versions = {metric['mfl_code']: metric['value'] for metric in dwapi_metrics}
    
    # Initialize the dictionary to store indicator metrics for each facility
    indicator_metrics_dict = {}
    for metric in indicator_metrics:
        mfl_code = metric['mfl_code']
        metric_name = metric['name']
        metric_value = metric['emr_value']
        if mfl_code not in indicator_metrics_dict:
            indicator_metrics_dict[mfl_code] = {}
        indicator_metrics_dict[mfl_code][metric_name] = metric_value

    # Update profiles with DWAPI versions and ETL dates where available
    for profile in profiles:
        mfl_code = profile['mfl_code']
        if mfl_code in dwapi_versions:
            profile['dwapi_version'] = dwapi_versions[mfl_code]
        if mfl_code in indicator_metrics_dict:
            profile['indicator_metrics'] = indicator_metrics_dict[mfl_code]

    # Return the updated profiles
    return {'profiles': profiles}

