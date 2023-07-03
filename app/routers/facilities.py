from fastapi import BackgroundTasks, APIRouter
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
    pipeline = [
		{'$match': {"is_current": True, "mfl_code": code}},
	]
    facility = facilityEntity(Facility.find_one({"mfl_code": code}))
    return {"facility": facility}