from fastapi import APIRouter
from app.serializers.profileSerializer import profileListEntity
from app.database import Profiles


router = APIRouter()

@router.get("/")
async def get_profiles():
    # pipeline = [
    #     {
    #         "$match": { "is_current": True }
    #     },
    #     {
    #         "$lookup": {
    #             "from": "facility",
    #             "localField": "mfl_code",
    #             "foreignField": "code",
    #             "as": "facility_info"
    #         }
    #     },
    #     {
    #         "$unwind": "$facility_info"
    #     },
    #     {
    #         "$lookup": {
    #             "from": "docket",
    #             "localField": "docket_id",
    #             "foreignField": "_id",
    #             "as": "docket_info"
    #         }
    #     },
    #     {
    #         "$unwind": "$docket_info"
    #     },
    #     {
    #         "$addFields": {
    #         "status": {
    #             "$cond": [
    #             { "$eq": ["$queued", "$received"] },
    #             "Processed",
    #             {
    #                 "$cond": [
    #                     { "$eq": ["$received", "$expected"] },
    #                     "Upload Complete",
    #                     {
    #                         "$cond": [
    #                             { "$eq": ["$received", 0] },
    #                             "Upload Not Started",
    #                             "Upload In Progress..."
    #                         ]
    #                     }
    #                 ]
    #             }
    #             ]
    #         }
    #         }
    #     },
    #     {
    #         "$project": {
    #             "code": { "$toString": "$mfl_code" },
    #             "facility": "$facility_info.name",
    #             "partner": "$facility_info.partner",
    #             "county": "$facility_info.county",
    #             "subcounty": "$facility_info.subcounty",
    #             "docket": "$docket_info.name",
    #             "received": "$received",
    #             "expected": "$expected",
    #             "queued": "$queued",
    #             "status": 1,
    #             "updated": ""
    #         }
    #     }
        # ]
    profiles = profileListEntity(Profiles.aggregate([]))
    return {'profiles': profiles}

