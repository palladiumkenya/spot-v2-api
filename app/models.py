# coding: utf-8
from .database import Base
from sqlalchemy import Column, text, DateTime, CHAR, Index, Integer,  Unicode
from sqlalchemy.sql import func
from sqlalchemy.dialects.mssql import DATETIMEOFFSET, CHAR
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Unicode, DateTime, func, text

Base = declarative_base()

metadata = Base.metadata


class FACT_CT_DHIS2(Base):
    __tablename__ = 'FACT_CT_DHIS2'

    id = Column(CHAR(36, 'Latin1_General_CI_AS'), primary_key=True, nullable=False, unique=True,
                server_default=text("(newid())"))
    DHISOrgId = Column(Unicode(255), index=True)
    SiteCode = Column(Unicode(255), index=True)
    FacilityName = Column(Unicode(255), index=True)
    County = Column(Unicode(255), index=True)
    SubCounty = Column(Unicode(255), index=True)
    Ward = Column(Unicode(255), index=True)
    ReportMonth_Year = Column(Unicode(255), index=True)
    Enrolled_Total = Column(Integer)
    StartedART_Total = Column(Integer)
    CurrentOnART_Total = Column(Integer)
    CTX_Total = Column(Integer)
    OnART_12Months = Column(Integer)
    NetCohort_12Months = Column(Integer)
    VLSuppression_12Months = Column(Integer)
    VLResultAvail_12Months = Column(Integer)
    createdAt = Column(DateTime, nullable=False, default=datetime.utcnow())
    updatedAt = Column(DateTime, nullable=False,
                       default=datetime.utcnow(), onupdate=func.now())
    Start_ART_Under_1 = Column(Integer)
    Start_ART_1_9 = Column(Integer)
    Start_ART_10_14_M = Column(Integer)
    Start_ART_10_14_F = Column(Integer)
    Start_ART_15_19_M = Column(Integer)
    Start_ART_15_19_F = Column(Integer)
    Start_ART_20_24_M = Column(Integer)
    Start_ART_20_24_F = Column(Integer)
    Start_ART_25_Plus_M = Column(Integer)
    Start_ART_25_Plus_F = Column(Integer)
    On_ART_Under_1 = Column(Integer)
    On_ART_1_9 = Column(Integer)
    On_ART_10_14_M = Column(Integer)
    On_ART_10_14_F = Column(Integer)
    On_ART_15_19_M = Column(Integer)
    On_ART_15_19_F = Column(Integer)
    On_ART_20_24_M = Column(Integer)
    On_ART_20_24_F = Column(Integer)
    On_ART_25_Plus_M = Column(Integer)
    On_ART_25_Plus_F = Column(Integer)

    UniqueCheck = Index('UniqueCheck', 'DHISOrgId',
                        'SiteCode', 'ReportMonth_Year', unique=True)


class FACT_HTS_DHIS2(Base):
    __tablename__ = 'FACT_HTS_DHIS2'

    id = Column('id', CHAR(36, 'SQL_Latin1_General_CP1_CI_AS'), primary_key=True,
                nullable=False, unique=True, server_default=text("NEWID()"))
    DHISOrgId = Column('DHISOrgId', Unicode(510), index=True)
    SiteCode = Column('SiteCode', Unicode(510), index=True)
    FacilityName = Column('FacilityName', Unicode(510), index=True)
    County = Column('County', Unicode(510), index=True)
    SubCounty = Column('SubCounty', Unicode(510), index=True)
    Ward = Column('Ward', Unicode(510), index=True)
    ReportMonth_Year = Column('ReportMonth_Year', Unicode(510), index=True)
    Tested_Total = Column('Tested_Total', Integer)
    Positive_Total = Column('Positive_Total', Integer)
    createdAt = Column('createdAt', DATETIMEOFFSET,
                       nullable=False, default=datetime.utcnow)
    updatedAt = Column('updatedAt', DATETIMEOFFSET, nullable=False,
                       default=datetime.utcnow, onupdate=func.now())
    Tested_1_9 = Column('Tested_1_9', Integer)
    Tested_10_14_M = Column('Tested_10_14_M', Integer)
    Tested_10_14_F = Column('Tested_10_14_F', Integer)
    Tested_15_19_M = Column('Tested_15_19_M', Integer)
    Tested_15_19_F = Column('Tested_15_19_F', Integer)
    Tested_20_24_M = Column('Tested_20_24_M', Integer)
    Tested_20_24_F = Column('Tested_20_24_F', Integer)
    Tested_25_Plus_M = Column('Tested_25_Plus_M', Integer)
    Tested_25_Plus_F = Column('Tested_25_Plus_F', Integer)
    Positive_1_9 = Column('Positive_1_9', Integer)
    Positive_10_14_M = Column('Positive_10_14_M', Integer)
    Positive_10_14_F = Column('Positive_10_14_F', Integer)
    Positive_15_19_M = Column('Positive_15_19_M', Integer)
    Positive_15_19_F = Column('Positive_15_19_F', Integer)
    Positive_20_24_M = Column('Positive_20_24_M', Integer)
    Positive_20_24_F = Column('Positive_20_24_F', Integer)
    Positive_25_Plus_M = Column('Positive_25_Plus_M', Integer)
    Positive_25_Plus_F = Column('Positive_25_Plus_F', Integer)

    UniqueCheck = Index('UniqueCheck', 'DHISOrgId',
                        'SiteCode', 'ReportMonth_Year', unique=True)


class FACT_PMTCT_DHIS2(Base):
    __tablename__ = 'FACT_PMTCT_DHIS2'

    id = Column('id', CHAR(36, 'SQL_Latin1_General_CP1_CI_AS'), primary_key=True,
                nullable=False, unique=True, server_default=text("NEWID()"))
    DHISOrgId = Column('DHISOrgId', Unicode(510), index=True)
    SiteCode = Column('SiteCode', Unicode(510), index=True)
    FacilityName = Column('FacilityName', Unicode(510), index=True)
    County = Column('County', Unicode(510), index=True)
    SubCounty = Column('SubCounty', Unicode(510), index=True)
    Ward = Column('Ward', Unicode(510), index=True)
    ReportMonth_Year = Column('ReportMonth_Year', Unicode(510), index=True)
    firstAncVisits = Column('firstAncVisits', Integer)
    deliveryFromHivPosMothers = Column('deliveryFromHivPosMothers', Integer)
    knownPosAt1stAnc = Column('knownPosAt1stAnc', Integer)
    intialTestAtAnc = Column('intialTestAtAnc', Integer)
    initialTestAtL_D = Column('initialTestAtL&D', Integer)
    initialTestAtPnc_6wks = Column('initialTestAtPnc<=6wks', Integer)
    knownHivStatusTotal = Column('knownHivStatusTotal', Integer)
    retestingPnc_6wks = Column('retestingPnc<=6wks', Integer)
    testedPnc_6wksTo6mnts = Column('testedPnc>6wksTo6mnts', Integer)
    knowPosAt1stAnc = Column('knowPosAt1stAnc', Integer)
    posResultsAnc = Column('posResultsAnc', Integer)
    posResultsL_D = Column('posResultsL&D', Integer)
    posResultsPnc_6wks = Column('posResultsPnc<=6wks', Integer)
    posPnc_6wksTo6mnts = Column('posPnc>6wksTo6mnts', Integer)
    totalPos = Column('totalPos', Integer)
    onHAARTat1stAnc = Column('onHAARTat1stAnc', Integer)
    startHAARTanc = Column('startHAARTanc', Integer)
    startHAARTL_D = Column('startHAARTL&D', Integer)
    startHAARTpnc_6wks = Column('startHAARTpnc<=6wks', Integer)
    onMaternalHAARTtotal = Column('onMaternalHAARTtotal', Integer)
    startHAARTPnc_6wksto6mnts = Column('startHAARTPnc>6wksto6mnts', Integer)
    onMaternalHAART12mnts = Column('onMaternalHAART12mnts', Integer)
    newCohort12mths = Column('newCohort12mths', Integer)
    syphilisScreened1stanc = Column('syphilisScreened1stanc', Integer)
    syphilisScreenedPos = Column('syphilisScreenedPos', Integer)
    syphilisTreated = Column('syphilisTreated', Integer)
    HIVposMordernFP6wks = Column('HIVposMordernFP6wks', Integer)
    HIVposPncVisits6wks = Column('HIVposPncVisits6wks', Integer)
    knownStatus1stContact = Column('knownStatus1stContact', Integer)
    initialTestANCMale = Column('initialTestANCMale', Integer)
    initialTestPncMale = Column('initialTestPncMale', Integer)
    initialTestL_DMale = Column('initialTestL&DMale', Integer)
    totalKnownStatusMale = Column('totalKnownStatusMale', Integer)
    _1stAncKPAdolescencts = Column('1stAncKPAdolescencts', Integer)
    PosResultAdolescents = Column('PosResultAdolescents', Integer)
    StartedHAARTAdolescentsTotal = Column(
        'StartedHAARTAdolescentsTotal', Integer)
    knownExposureAtPenta1 = Column('knownExposureAtPenta1', Integer)
    totalGivenPenta1 = Column('totalGivenPenta1', Integer)
    infantARVProphylANC = Column('infantARVProphylANC', Integer)
    infantARVProphylL_D = Column('infantARVProphylL&D', Integer)
    infantARVProphyl_8wksPNC = Column('infantARVProphyl<8wksPNC', Integer)
    totalARVProphyl = Column('totalARVProphyl', Integer)
    HEICtxDdsStart_2mnts = Column('HEICtxDdsStart<2mnts', Integer)
    initialPCR_8wks = Column('initialPCR<8wks', Integer)
    initialPCR_8wksTo12mnts = Column('initialPCR>8wksTo12mnts', Integer)
    initialPCRtest_12mntsTotal = Column('initialPCRtest<12mntsTotal', Integer)
    infected24mnts = Column('infected24mnts', Integer)
    uninfected24mnts = Column('uninfected24mnts', Integer)
    unknownOutcome = Column('unknownOutcome', Integer)
    netCohortHEI24mnts = Column('netCohortHEI24mnts', Integer)
    motherBabyPairs24mnts = Column('motherBabyPairs24mnts', Integer)
    pairNetCohort24mnts = Column('pairNetCohort24mnts', Integer)
    EBFat6mnts = Column('EBFat6mnts', Integer)
    ERFat6mnts = Column('ERFat6mnts', Integer)
    MFat6mnts = Column('MFat6mnts', Integer)
    BFat12mnts = Column('BFat12mnts', Integer)
    notBFat12mnts = Column('notBFat12mnts', Integer)
    BFat18mnts = Column('BFat18mnts', Integer)
    notBFat18mnts = Column('notBFat18mnts', Integer)
    createdAt = Column('createdAt', DATETIMEOFFSET,
                       nullable=False, default=datetime.utcnow)
    updatedAt = Column('updatedAt', DATETIMEOFFSET, nullable=False,
                       default=datetime.utcnow, onupdate=func.now())

    def __repr__(self):
        return f"<FACT_PMTCT_DHIS2(id='{self.id}', FacilityName='{self.FacilityName}', County='{self.County}', ReportMonth_Year='{self.ReportMonth_Year}')>"
