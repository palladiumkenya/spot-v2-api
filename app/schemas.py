from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class NoteBaseSchema(BaseModel):
    id: str | None = None
    title: str
    content: str
    category: str | None = None
    published: bool = False
    createdAt: datetime | None = None
    updatedAt: datetime | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class ListNoteResponse(BaseModel):
    status: str
    results: int
    notes: List[NoteBaseSchema]


class FACT_PMTCT_DHIS2Schema(BaseModel):
    
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class FACT_HTS_DHIS2(BaseModel):
    id: str | None = None
    DHISOrgId: str | None = None
    SiteCode: str | None = None
    FacilityName: str | None = None
    County: str | None = None
    SubCounty: str | None = None
    Ward: str | None = None
    ReportMonth_Year: str | None = None
    Tested_Total: int | None = None
    Positive_Total: int | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None
    Tested_1_9: int | None = None
    Tested_10_14_M: int | None = None
    Tested_10_14_F: int | None = None
    Tested_15_19_M: int | None = None
    Tested_15_19_F: int | None = None
    Tested_20_24_M: int | None = None
    Tested_20_24_F: int | None = None
    Tested_25_Plus_M: int | None = None
    Tested_25_Plus_F: int | None = None
    Positive_1_9: int | None = None
    Positive_10_14_M: int | None = None
    Positive_10_14_F: int | None = None
    Positive_15_19_M: int | None = None
    Positive_15_19_F: int | None = None
    Positive_20_24_M: int | None = None
    Positive_20_24_F: int | None = None
    Positive_25_Plus_M: int | None = None
    Positive_25_Plus_F: int | None = None
    
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class FACT_CT_DHIS2(BaseModel):
    County: Optional[str]
    SubCounty: Optional[str]
    Ward: Optional[str]
    DHISOrgId: Optional[str]
    FacilityName: Optional[str]
    SiteCode: Optional[str]
    ReportMonth_Year: str
    Enrolled_Total: Optional[int]
    StartedART_Total: Optional[int]
    CurrentOnART_Total: Optional[int]
    CTX_Total: Optional[int]
    OnART_12Months: Optional[int]
    NetCohort_12Months: Optional[int]
    VLSuppression_12Months: Optional[int]
    VLResultAvail_12Months: Optional[int]
    Start_ART_Under_1: Optional[int]
    Start_ART_1_9: Optional[int]
    Start_ART_10_14_M: Optional[int]
    Start_ART_10_14_F: Optional[int]
    Start_ART_15_19_M: Optional[int]
    Start_ART_15_19_F: Optional[int]
    Start_ART_20_24_M: Optional[int]
    Start_ART_20_24_F: Optional[int]
    Start_ART_25_Plus_M: Optional[int]
    Start_ART_25_Plus_F: Optional[int]
    On_ART_Under_1: Optional[int]
    On_ART_1_9: Optional[int]
    On_ART_10_14_M: Optional[int]
    On_ART_10_14_F: Optional[int]
    On_ART_15_19_M: Optional[int]
    On_ART_15_19_F: Optional[int]
    On_ART_20_24_M: Optional[int]
    On_ART_20_24_F: Optional[int]
    On_ART_25_Plus_M: Optional[int]
    On_ART_25_Plus_F: Optional[int]
    
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True