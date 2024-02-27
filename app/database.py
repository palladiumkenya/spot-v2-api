from pymongo import mongo_client
import pymongo
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config.config import settings

## MongoDB Connections
print('Connecting to MongoDB...')
client = mongo_client.MongoClient(settings.MONGODB_URL)
print('Connected to MongoDB...')

db = client[settings.DB]
Facility = db.facilities
Facility.create_index([("mfl_code", pymongo.ASCENDING)], unique=True)
Notices = db.notices
Notices.create_index([("rank", pymongo.ASCENDING)], unique=False)
Indicators = db.indicators
Indicators.create_index([("is_current", pymongo.DESCENDING),("created_at", pymongo.DESCENDING)], unique=False)
Dockets = db.dockets
Dockets.create_index([("name", pymongo.ASCENDING)], unique=True)
Manifests = db.manifests
Manifests.create_index([("is_current", pymongo.DESCENDING), ("created_at", pymongo.DESCENDING)])
Extracts = db.extracts
Extracts.create_index([("created_at", pymongo.DESCENDING)])
FacilityMetrics = db.facility_metrics
FacilityMetrics.create_index([("is_current", pymongo.DESCENDING), ("created_at", pymongo.DESCENDING)])
Profiles = db.profiles_vw
Handshake = db.handshake
SpotError = db.spot_errors
Log = db.messages_log
Error = db.error_log
DebugLog = db.debug_log

## MSSQL Connections
SQL_DATABASE_URL = f'mssql+pymssql://{settings.DB_MSSQL_USERNAME}:{settings.DB_MSSQL_PASS}@{settings.DB_MSSQL_HOST}:1433/{settings.DB_MSSQL}'

engine = create_engine(
    SQL_DATABASE_URL, echo=True, connect_args={}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

