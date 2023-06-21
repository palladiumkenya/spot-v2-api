from typing import Optional
from pydantic import BaseModel, Field
from bson.objectid import ObjectId
from datetime import datetime

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
    id: str
    rank: int
    message: str
    title: str
    level: str

    class Config:
        extra = 'allow'
        orm_mode = True

class IndicatorsBaseSchema(BaseModel):
    mfl_code: int
    facility_manifest_id: str
    name: str
    emr_value: str
    emr_indicator_date: datetime
    dwh_value: Optional[str] = None
    dwh_indicator_date: Optional[datetime] = None
    created_at: datetime = datetime.now().isoformat()
    is_current: bool = True

    class Config:
        extra = 'allow'
        orm_mode = True
        json_encoders = {ObjectId: str}