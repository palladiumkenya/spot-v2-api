def indicatorEntity(indicator) -> dict:
    return {
        "id": str(indicator["_id"]),
        "mfl_code": int(indicator["mfl_code"]),
		"name": indicator["name"],
		"emr_value": indicator["emr_value"],
		"emr_indicator_date": indicator["emr_indicator_date"],
		"dwh_value": indicator["dwh_value"],
		"dwh_indicator_date": indicator["dwh_indicator_date"],
		"is_current": indicator["is_current"],
    }

def indicatorListEntity(indicators) -> list:
    return [indicatorEntity(indicator) for indicator in indicators]

