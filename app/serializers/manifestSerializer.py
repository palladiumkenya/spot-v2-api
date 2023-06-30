def extractEntity(document) -> dict:
    return {
        "code": int(document["code"]),
        "facility": document["facility"],
        "docket": document["docket"],
        "extract_display_name": document["extract_display_name"],
        "status": document["status"],
        "received": document["received"],
        "expected": document["expected"],
        "queued": document["queued"],
        "rank": document["rank"],
        "updated_at": document["updated_at"]
    }

def extractListEntity(documents) -> list:
    return [extractEntity(document) for document in documents]

def manifestEntity(manifest) -> dict:
    return {
        "docket": manifest["docket"],
        "mfl_code": manifest["mfl_code"],
        "documents": extractListEntity(manifest["documents"])
    }

def manifestListEntity(manifests) -> list:
    return [manifestEntity(manifest) for manifest in manifests]

