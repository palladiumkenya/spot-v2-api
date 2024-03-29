from typing import Optional, List
from pydantic import BaseModel, Field
# from bson.objectid import ObjectId
from datetime import datetime
from bson import ObjectId

class FacilityBaseSchema(BaseModel):
    id: str
    mfl_code: int
    name: str
    subcounty: str = Field(..., alias='_subcounty')
    county: str = Field(..., alias='_county')
    partner: Optional[str] = Field(None, alias="_partner")
    owner: Optional[str] = Field(None, alias="_owner")
    agency: Optional[str] = Field(None, alias="_agency")
    lat: Optional[float] = None
    lon: Optional[float] = None

    class Config:
        # extra = 'allow'
        orm_mode = True

class NoticesBaseSchema(BaseModel):
    rank: int
    message: str
    title: str
    level: str

    class Config:
        extra = 'allow'
        orm_mode = True

class IndicatorsBaseSchema(BaseModel):
    mfl_code: int
    facility_manifest_id: Optional[str] = ''
    name: str
    emr_value: str
    emr_indicator_date: datetime
    dwh_value: Optional[str] = None
    dwh_indicator_date: Optional[datetime] = None
    created_at: datetime = datetime.now()
    is_current: bool = True

    class Config:
        extra = 'allow'
        orm_mode = True
        json_encoders = {ObjectId: str}

class ExtractSchema(BaseModel):
    id: str = Field(alias='id')
    name: str
    display: str
    isPatient: bool
    rank: int
    
    class Config:
        orm_mode = True

class DocketSchema(BaseModel):
    name: str
    display: str
    extracts: List[ExtractSchema]

class ProfilesSchema(BaseModel):
    mfl_code: int
    docket_id: str
    stage: str
    session: Optional[str] = None
    is_current: bool
    created_at: datetime = datetime.now()

class ManifestsSchema(BaseModel):
    manifest_id: str
    mfl_code: int
    docket_id: Optional[ObjectId] = None
    extract_id: str
    session: Optional[str] = None
    expected: Optional[int] = 0
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    receivedDate: Optional[datetime] = None
    queuedDate: Optional[datetime] = None
    is_current: Optional[bool] = True
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    log_date: Optional[datetime] = None
    log_id: Optional[ObjectId] = None
    
    class Config:
        arbitrary_types_allowed = True
        extra = 'allow'
        orm_mode = True
        json_encoders = {ObjectId: str}
