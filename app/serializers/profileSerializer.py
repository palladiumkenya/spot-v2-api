def profileEntity(profile) -> dict:
    return {
        "facility": profile["facility"],
        "partner": profile["partner"],
        "county": profile["county"],
        "subcounty": profile["subcounty"],
        "docket": profile["docket"],
        "totalReceived": profile["totalReceived"],
        "totalExpected": profile["totalExpected"],
        "totalQueued": profile["totalQueued"],
        "status": profile["status"],
        "updated": profile["updated"]
    }

def profileListEntity(profiles) -> list:
    return [profileEntity(profile) for profile in profiles]

