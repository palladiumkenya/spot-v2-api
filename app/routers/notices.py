from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from app.serializers.noticeSerializer import noticesListEntity
from app.serializers.facilitySerializer import facilityListEntity
from app.database import Notices, Profiles, Facility, get_db
from app.api.publish_complete import send_to_rabbitmq
from app.api.dwh_indicators import fetch_and_post, get_period


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
            message = str({"Facility": item['facility'], "MFL Code": item['mfl_code'], "Docket": item['docket'],
                            "indicator_date": get_period()[2].strftime('%Y-%m-%d'), "Message": "complete!"})
            
            background_tasks.add_task(send_to_rabbitmq, message)
    return {"message": "Started sending notices"}


@router.get('/livesync')
async def pull_dwh_indicators(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    facilities = facilityListEntity(Facility.find())
    period = get_period()
    month = period[0]
    year = period[1]

    for facility in facilities:
        print(f'starting {facility["mfl_code"]}')
        
        background_tasks.add_task(fetch_and_post,
            db, facility, f"SELECT SUM(Tested) as value FROM Reporting.dbo.AggregateHTSUptake WHERE MFLCode = {facility['mfl_code']} and year = {year} and month = {month}", 'HTS_TESTED')
        background_tasks.add_task(fetch_and_post,
            db, facility, f"SELECT SUM(Positive) as value FROM Reporting.dbo.AggregateHTSUptake WHERE MFLCode = {facility['mfl_code']} and year = {year} and month = {month}", 'HTS_TESTED_POS')
        background_tasks.add_task(fetch_and_post,
            db, facility, f"SELECT SUM(patients_startedART) as value FROM Reporting.dbo.AggregateTxNew WHERE MFLCode = {facility['mfl_code']} and StartARTYearMonth = '{year}-{month}'", 'TX_NEW')
        background_tasks.add_task(fetch_and_post,
            db, facility, f"SELECT SUM(CountClientsTXCur) as value FROM Reporting.dbo.AggregateTXCurr WHERE MFLCode = {facility['mfl_code']}", 'TX_CURR')
        
        print(f'finishing {facility["mfl_code"]}')

    return {"message": "Started sending dwh indicators"}
