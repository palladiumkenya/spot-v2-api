from fastapi import BackgroundTasks, APIRouter, HTTPException
from app.api.facilities import get_all_facilities
from app.database import Facility
from app.serializers.facilitySerializer import facilityEntity

router = APIRouter()

@router.get('/update_facilities')
async def start_periodic_task(background_tasks: BackgroundTasks):
    background_tasks.add_task(get_all_facilities)
    return {"message": "Started Pulling Facilities"}

@router.get('/{code}')
async def start_periodic_task(code: int):
    try:
        facility = facilityEntity(Facility.find_one({"mfl_code": code}))
        return {"facility": facility}
    except TypeError as e:
        raise HTTPException(status_code=404, detail="Facility not found") from e 