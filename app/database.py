from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import mongo_client
import pymongo
from app.config.config import settings

print('Connecting to MongoDB...')
client = mongo_client.MongoClient(settings.MONGODB_URL)
print('Connected to MongoDB...')

db = client[settings.DB]
Facility = db.facilities
Facility.create_index([("mfl_code", pymongo.ASCENDING)], unique=True)
Notices = db.notices
Notices.create_index([("rank", pymongo.ASCENDING)], unique=False)
Indicators = db.indicators
Indicators.create_index([("created_at", pymongo.DESCENDING)], unique=False)
Dockets = db.dockets
Dockets.create_index([("name", pymongo.ASCENDING)], unique=True)
Manifests = db.manifests
FacilityMetrics = db.facility_metrics
Profiles = db.profiles_vw
