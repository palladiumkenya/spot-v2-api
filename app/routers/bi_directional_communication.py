import asyncio
from fastapi import APIRouter, WebSocket
from app.serializers.profileSerializer import profileStatusListEntity
from app.serializers.manifestSerializer import manifestStatusListEntity
from app.database import Profiles, Manifests

router = APIRouter()

@router.websocket("/dockets/{code}")
async def get_status(code: int, websocket: WebSocket):
    await websocket.accept()
    while True:
        profiles = profileStatusListEntity(Profiles.find({"mfl_code": code}))
        await websocket.send_json({'dockets': profiles})
        await asyncio.sleep(300)


@router.websocket("/extracts/{code}")
async def get_extracts_progress(code: int, websocket: WebSocket):
    pipeline = [
        {"$match": {"is_current": True, "mfl_code": code}},
        {"$lookup": {
            "from": "extracts",
            "let": {
                    "manifest_id_field": "$manifest_id",
                    "extract_id_field": "$extract_id",
                    "mfl_code_field": "$mfl_code",
            },
            "pipeline": [
                {
                    "$match": {
                        "$expr": {
                            "$and": [
                                {"$eq": ["$manifest_id",
                                        "$$manifest_id_field"]},
                                {"$eq": ["$extract_id",
                                        "$$extract_id_field"]},
                                {"$eq": ["$mfl_code",
                                        "$$mfl_code_field"]},
                            ],
                        },
                    },
                },
            ],
            "as": "extracts",
        },
        },
        {
            "$unwind": {
                "path": "$extracts",
                "preserveNullAndEmptyArrays": True
            }
        },
        {"$lookup": {
            "from": "facilities",
            "localField": "mfl_code",
                    "foreignField": "mfl_code",
                    "as": "facility_info"
        }},
        {"$unwind": "$facility_info"},
        {"$lookup": {
            "from": "dockets",
            "let": {"extractId": "$extract_id"},
            "pipeline": [
                {"$match": {
                    "$expr": {"$in": ["$$extractId", "$extracts.id"]}
                }},
                {"$project": {
                    "display": {
                        "$arrayElemAt": [
                            {"$filter": {
                                "input": "$extracts",
                                "cond": {"$eq": ["$$this.id", "$$extractId"]}
                            }},
                            0
                        ]
                    }
                }}
            ],
            "as": "extract_info"
        }},
        {"$unwind": "$extract_info"},
        {"$lookup": {
            "from": "dockets",
            "localField": "docket_id",
                    "foreignField": "_id",
                    "as": "docket_info"
        }},
        {"$unwind": "$docket_info"},
        {"$addFields": {
            "status": {
                "$switch": {
                    "branches": [
                        {
                            "case": {"$eq": ["$extracts.queued", "$expected"]},
                            "then": "Processed"
                        },
                        {
                            "case": {"$eq": ["$extracts.received", "$expected"]},
                            "then": "Queued For Processing"
                        },
                        {
                            "case": {"$eq": ["$extracts.received", 0]},
                            "then": "Upload In Progress..."
                        }
                    ],
                    "default": "Upload In Progress..."
                }
            }
        }},
        {"$group": {
            "_id": {
                "facility": "$facility_info._id",
                "docket": "$docket_info._id"
            },
            "docket": {"$first": "$docket_info.display"},
            "mfl_code": {"$first": "$facility_info.mfl_code"},
            "extracts": {
                "$push": {
                    "code": {"$toString": "$mfl_code"},
                    "facility": "$facility_info.name",
                    "docket": "$docket_info.display",
                    "extract_display_name": "$extract_info.display.display",
                    "status": "$status",
                    "expected": "$expected",
                    "received": {"$ifNull": ["$extracts.received", 0]},
                    "queued": {"$ifNull": ["$extracts.queued", 0]},
                    "rank": "$extract_info.display.rank",
                    "updated_at": "$updated_at"
                }
            }
        }},
        {"$sort": {"documents.rank": 1}}
    ]
    
    await websocket.accept()
    while True:
        extracts = manifestStatusListEntity(Manifests.aggregate(pipeline))
        await websocket.send_json({'extracts': extracts})
        await asyncio.sleep(300)