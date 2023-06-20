from fastapi import APIRouter
from app.schemas import NoticesBaseSchema
from app.serializers.noticesSerializer import noticeEntity, noticesListEntity
from app.database import Notices


router = APIRouter()

@router.get("/")
async def get_notices():
    pipeline = [
        {'$match': {}},
    ]
    notices = noticesListEntity(Notices.aggregate(pipeline))
    return {'notices': notices}

