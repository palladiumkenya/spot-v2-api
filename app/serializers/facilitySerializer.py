def facilityEntity(facility) -> dict:
    return {
        "id": str(facility["_id"]),
        "mfl_code": int(facility["mfl_code"]),
		"_subcounty": facility["_subcounty"],
		"_county": facility["_county"],
		"_partner": facility["_partner"],
		"_owner": facility["_owner"],
		"_agency": facility["_agency"],
		"lat": float(facility["lat"]),
		"lon": float(facility["lon"]),
        "name": facility["name"],
        "created_at": facility["created_at"],
        "updated_at": facility["updated_at"]
    }

def facilityListEntity(facilities) -> list:
    return [facilityEntity(facility) for facility in facilities]

