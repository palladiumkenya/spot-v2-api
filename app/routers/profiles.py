from fastapi import APIRouter
from app.serializers.profileSerializer import profileListEntity
from app.database import Profiles


router = APIRouter()

@router.get("/")
async def get_profiles():
    profiles = profileListEntity(Profiles.aggregate([]))
    return {'profiles': profiles}

