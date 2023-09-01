def profileEntity(profile) -> dict:
    return {
        "facility": profile["facility"],
        "mfl_code": profile["mfl_code"],
        "agency": profile["agency"],
        "partner": profile["partner"],
        "county": profile["county"],
        "subcounty": profile["subcounty"],
        "docket": profile["docket"],
        "totalReceived": profile["totalReceived"],
        "totalExpected": profile["totalExpected"],
        "totalQueued": profile["totalQueued"],
        "status": profile["status"],
        "updated": profile["updated_at"],
        "log_date": profile["log_date"],
        "upload_mode": profile["upload_mode"],
    }

def profileListEntity(profiles) -> list:
    return [profileEntity(profile) for profile in profiles]

def profileStatusEntity(profile) -> dict:
    return {
        "facility": profile["facility"],
        "mfl_code": profile["mfl_code"],
        "agency": profile["agency"],
        "partner": profile["partner"],
        "county": profile["county"],
        "subcounty": profile["subcounty"],
        "docket": profile["docket"],
        "status": profile["status"],
        "updated": str(profile["updated_at"])
    }

def profileStatusListEntity(profiles) -> list:
    return [profileStatusEntity(profile) for profile in profiles]