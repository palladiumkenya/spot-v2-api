def facilityEntity(facility) -> dict:
    return {
        "mfl_code": int(facility["mfl_code"]),
		"subcounty": facility["subcounty"],
		"county": facility["county"],
		"partner": facility["partner"],
		"owner": facility["owner"],
		"agency": facility["agency"],
		"lat": facility.get("lat", 0),
		"lon": facility.get("lon", 0),
        "name": facility["name"],
        # "created_at": facility["created_at"],
        # "updated_at": facility["updated_at"]
    }

def facilityListEntity(facilities) -> list:
    return [facilityEntity(facility) for facility in facilities]

