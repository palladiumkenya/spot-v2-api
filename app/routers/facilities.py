from fastapi import FastAPI, BackgroundTasks, APIRouter
from app.api.facilities import get_all_facilities


router = APIRouter()

@router.get('/')
async def start_periodic_task(background_tasks: BackgroundTasks):
    background_tasks.add_task(get_all_facilities)
    return {"message": "Started Pulling Facilities"}