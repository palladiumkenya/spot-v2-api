import httpx
from app import schemas
import ssl
from fastapi import Depends, HTTPException, status
from app.database import Facility
from datetime import datetime
from pymongo.errors import DuplicateKeyError

url = 'https://prod.kenyahmis.org:7001/facilities/get_mfl_data/all'

async def get_all_facilities():
    print(f'+ FACILITIES UPDATE + {datetime.utcnow()}')
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    async with httpx.AsyncClient(verify=ssl_context) as client:
        response = await client.get(url)
        data = response.json()

    facilities_data = [schemas.FacilityBaseSchema(**facility) for facility in data["facilities"]]

    documents = [facility.dict() for facility in facilities_data]
    
    for document in documents:
        Facility.update_one(
            {"mfl_code": document["mfl_code"]},
            {"$set": document},
            upsert=True
        )
    print(f'+ FACILITIES UPDATE DONE + {datetime.utcnow()}')
