from fastapi import APIRouter, BackgroundTasks
from app.serializers.noticeSerializer import noticesListEntity
from app.database import Notices, Profiles
from app.api.publish_complete import send_to_rabbitmq


router = APIRouter()

@router.get("/")
async def get_notices():
    pipeline = [
        {'$match': {}},
    ]
    notices = noticesListEntity(Notices.aggregate(pipeline))
    return {'notices': notices}


@router.get('/update_notices')
async def start_periodic_task(background_tasks: BackgroundTasks):
    manifest = Profiles.find({})

    for item in manifest:
        if item and item.get("totalExpected") == item.get("totalReceived") == item.get("totalQueued"):
            message = str({"Facility": item['facility'], "MFL Code": item['mfl_code'],
                        "Docket": item['docket'], "Message": "complete!"})
            # background_tasks = BackgroundTasks()
            print(message)
            # send_to_rabbitmq(message)
            print("da")
            background_tasks.add_task(send_to_rabbitmq, message)
    return {"message": "Started sending notices"}
