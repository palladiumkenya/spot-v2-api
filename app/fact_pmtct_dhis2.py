from datetime import datetime
from dotenv import load_dotenv
from .models import FACT_PMTCT_DHIS2
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, APIRouter
from .database import get_db
from fastapi import FastAPI, HTTPException
import requests
from .config import settings
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

router = APIRouter()

app = FastAPI()
load_dotenv()


@router.get("/process_pmtct_dhis2/latest")
async def process_pmtct_dhis2(db: Session = Depends(get_db)):
    try:
        current_date = datetime.now()
        previous_month = current_date - timedelta(days=current_date.day)
        period = previous_month.strftime('%Y%m')

        data = process_pmtct_service(period, db)
        print(data.keys())
        # Perform the merge operation for the filtered records
        db.bulk_insert_mappings(FACT_PMTCT_DHIS2, data["new"])
        db.commit()
        return {"message": "PMTCT Dhis2 Dwh data processed successfully.", "records": {"new": len(data["new"]), "updated": len(data["updated"])}}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/process_pmtct_dhis2/{period}")
async def process_pmtct_dhis2(period: str, db: Session = Depends(get_db)):
    try:
        data = process_pmtct_service(period, db)
        print(data.keys())
        # Perform the merge operation for the filtered records
        db.bulk_insert_mappings(FACT_PMTCT_DHIS2, data["new"])
        db.commit()
        return {"message": "PMTCT Dhis2 Dwh data processed successfully.", "records": {"new": len(data["new"]), "updated": len(data["updated"])}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def process_pmtct_service(period, db):
    try:
        dhis2_api_base_url = settings.DHIS2_API_BASE_URL
        dhis2_username = settings.DHIS2_USERNAME
        dhis2_password = settings.DHIS2_PASSWORD

        ou = "dimension=ou:LEVEL-5;"
        de = "dimension=dx:uSxBUWnagGg;C8xdcRWT9d2;qSgLzXh46n9;ETX9cUWF43c;mQz4DhBSv9V;LQpQQP3KnU1;ssqPT53vnZf;kk8BEq4Jlf7;PXUzSsmeY0P;oZc8MNc0nLZ;nwXS5vxrrr7;hn3aChn4sVx;AfHArvGun12;hHLR1HP8xzI;KYpWTsp2yHv;lJpaBye9B0H;WNFWVHMqPv9;ckPCoAwmWmT;vkOYqEesPAi;PyDKoTxqKB9;UMyB7dSIdz1;wMYMF6VVcCW;MciNE2W7sor;i5jVVTm1vI8;hZrdUVigO54;UdXbP4fFObF;Y0hKWx5oza6;VBCPSPnEnPx;DUr6GIyAR0h;W8kBodAGDBo;HsJtt7Nzn1z;mM9oXTBwkXS;WcO6ZWYvXPB;YzC4XfEm8E6;APBLLBYtVP3;C5b8YcNtR8D;SAva1cicjiX;wc8k1HwRUB6;HAumxpKBaoK;Jn6ATTfXp02;RY1js5pK2Ep;PgYIC96gz70;OMEeGtvqlx1;UIok7l6W4nh;KQDcvUpq0rx;R0CoqawtNCc;DMr8fYCKJzF;uMEWtdvqMj2;SNaQTm9pPNb;xHufJhG2OJx;Sb7py5Bpscw;AyIWn14DRdG;w8Mh4mNrZkF;iWhHBwe5R1H;l2BRlJnfhmJ;DO7Ix0h8vfS;efy1HMhR4NC;JJDVvDJ02cb;HzahP52iTLK;"
        pe = "dimension=pe:" + period + ";"
        query = (
            "/analytics?"
            + ou
            + "&"
            + de
            + "&"
            + pe
            + "&displayProperty=NAME&showHierarchy=true&tableLayout=true&columns=dx;pe&rows=ou&hideEmptyRows=true&paging=false"
        )
        url = f"{dhis2_api_base_url}{query}"
        auth = (dhis2_username, dhis2_password)

        try:
            response = requests.get(url, auth=auth)
            response.raise_for_status()
            data_set = response.json()
            ct_data = []
            records_to_merge = []
            records_to_update = []

            if "rows" in data_set:
                for row in data_set["rows"]:
                    if row[7].strip().isdigit():
                        try:
                            data = {}
                            data['County'] = row[1].replace(" County", "").strip() if row[1].strip() != "" else None
                            data['SubCounty'] = row[2].replace(" Sub County", "").strip() if row[2].strip() != "" else None
                            data['Ward'] = row[3].replace(" Ward", "").strip() if row[3].strip() != "" else None
                            data['DHISOrgId'] = row[5].strip() if row[5].strip() != "" else None
                            data['SiteCode'] = row[7].strip() if row[7].strip() != "" else None
                            data['FacilityName'] = row[6].strip() if row[6].strip() != "" else None
                            data['ReportMonth_Year'] = period
                            data['firstAncVisits'] = int(row[9]) if row[9].strip() != "" else None
                            data['deliveryFromHivPosMothers'] = int(row[10]) if row[10].strip() != "" else None
                            data['knownPosAt1stAnc'] = int(row[11]) if row[11].strip() != "" else None
                            data['intialTestAtAnc'] = int(row[12]) if row[12].strip() != "" else None
                            data['initialTestAtL_D'] = int(row[13]) if row[13].strip() != "" else None
                            data['initialTestAtPnc_6wks'] = int(row[14]) if row[14].strip() != "" else None
                            data['knownHivStatusTotal'] = int(row[15]) if row[15].strip() != "" else None
                            data['retestingPnc<=6wks'] = int(row[16]) if row[16].strip() != "" else None
                            data['testedPnc>6wksTo6mnts'] = int(row[17]) if row[17].strip() != "" else None
                            data['knowPosAt1stAnc'] = int(row[18]) if row[18].strip() != "" else None
                            data['posResultsAnc'] = int(row[19]) if row[19].strip() != "" else None
                            data['posResultsL&D'] = int(row[20]) if row[20].strip() != "" else None
                            data['posResultsPnc<=6wks'] = int(row[21]) if row[21].strip() != "" else None
                            data['posPnc>6wksTo6mnts'] = int(row[22]) if row[22].strip() != "" else None
                            data['totalPos'] = int(row[23]) if row[23].strip() != "" else None
                            data['onHAARTat1stAnc'] = int(row[24]) if row[24].strip() != "" else None
                            data["startHAARTanc"] = int(row[25]) if row[25].strip() != "" else None
                            data["startHAARTL&D"] = int(row[26]) if row[26].strip() != "" else None
                            data["startHAARTpnc<=6wks"] = int(row[27]) if row[27].strip() != "" else None
                            data["onMaternalHAARTtotal"] = int(row[28]) if row[28].strip() != "" else None
                            data["startHAARTPnc>6wksto6mnts"] = int(row[29]) if row[29].strip() != "" else None
                            data["onMaternalHAART12mnts"] = int(row[30]) if row[30].strip() != "" else None
                            data["newCohort12mths"] = int(row[31]) if row[31].strip() != "" else None
                            data["syphilisScreened1stanc"] = int(row[32]) if row[32].strip() != "" else None
                            data["syphilisScreenedPos"] = int(row[33]) if row[33].strip() != "" else None
                            data["syphilisTreated"] = int(row[34]) if row[34].strip() != "" else None
                            data["HIVposMordernFP6wks"] = int(row[35]) if row[35].strip() != "" else None
                            data["HIVposPncVisits6wks"] = int(row[36]) if row[36].strip() != "" else None
                            data["knownStatus1stContact"] = int(row[37]) if row[37].strip() != "" else None
                            data["initialTestANCMale"] = int(row[38]) if row[38].strip() != "" else None
                            data["initialTestL&DMale"] = int(row[39]) if row[39].strip() != "" else None
                            data["initialTestPncMale"] = int(row[40]) if row[40].strip() != "" else None
                            data["totalKnownStatusMale"] = int(row[41]) if row[41].strip() != "" else None
                            data["1stAncKPAdolescencts"] = int(row[42]) if row[42].strip() != "" else None
                            data["PosResultAdolescents"] = int(row[43]) if row[43].strip() != "" else None
                            data["StartedHAARTAdolescentsTotal"] = int(row[44]) if row[44].strip() != "" else None
                            data["knownExposureAtPenta1"] = int(row[45]) if row[45].strip() != "" else None
                            data["totalGivenPenta1"] = int(row[46]) if row[46].strip() != "" else None
                            data["infantARVProphylANC"] = int(row[47]) if row[47].strip() != "" else None
                            data["infantARVProphylL&D"] = int(row[48]) if row[48].strip() != "" else None
                            data["infantARVProphyl<8wksPNC"] = int(row[49]) if row[49].strip() != "" else None
                            data["totalARVProphyl"] = int(row[50]) if row[50].strip() != "" else None
                            data["HEICtxDdsStart<2mnts"] = int(row[51]) if row[51].strip() != "" else None
                            data["initialPCR<8wks"] = int(row[52]) if row[52].strip() != "" else None
                            data["initialPCR>8wksTo12mnts"] = int(row[53]) if row[53].strip() != "" else None
                            data["initialPCRtest<12mntsTotal"] = int(row[54]) if row[54].strip() != "" else None
                            data["infected24mnts"] = int(row[55]) if row[55].strip() != "" else None
                            data["uninfected24mnts"] = int(row[56]) if row[56].strip() != "" else None
                            data["unknownOutcome"] = int(row[57]) if row[57].strip() != "" else None
                            data["netCohortHEI24mnts"] = int(row[58]) if row[58].strip() != "" else None
                            data["motherBabyPairs24mnts"] = int(row[59]) if row[59].strip() != "" else None
                            data["pairNetCohort24mnts"] = int(row[60]) if row[60].strip() != "" else None
                            data["EBFat6mnts"] = int(row[61]) if row[61].strip() != "" else None
                            data["ERFat6mnts"] = int(row[62]) if row[62].strip() != "" else None
                            data["MFat6mnts"] = int(row[63]) if row[63].strip() != "" else None
                            data["BFat12mnts"] = int(row[64]) if row[64].strip() != "" else None
                            data["notBFat12mnts"] = int(row[65]) if row[65].strip() != "" else None
                            data["BFat18mnts"] = int(row[66]) if row[66].strip() != "" else None
                            data["notBFat18mnts"] = int(row[67]) if row[67].strip() != "" else None

                            # Append the data dictionary to the main list
                            ct_data.append(data)

                        except ValueError:
                            raise HTTPException(
                                status_code=500, detail="Invalid data in the response.")
            try:
                # Filter out duplicate records by checking if they already exist in the database
                existing_records = db.query(FACT_PMTCT_DHIS2).filter(FACT_PMTCT_DHIS2.DHISOrgId.in_([r['DHISOrgId'] for r in ct_data]),
                                                                     FACT_PMTCT_DHIS2.SiteCode.in_(
                                                                         [r['SiteCode'] for r in ct_data]),
                                                                     FACT_PMTCT_DHIS2.ReportMonth_Year.in_([r['ReportMonth_Year'] for r in ct_data])).all()
                existing_record_ids = {
                    (rec.DHISOrgId, rec.SiteCode, rec.ReportMonth_Year) for rec in existing_records}
                records_to_merge = [rec for rec in ct_data if (
                    rec['DHISOrgId'], rec['SiteCode'], rec['ReportMonth_Year']) not in existing_record_ids]
                records_to_update = [rec for rec in ct_data if (
                    rec['DHISOrgId'], rec['SiteCode'], rec['ReportMonth_Year']) in existing_record_ids]
                
                for existing in records_to_update:
                    print(existing)
                    db.query(FACT_PMTCT_DHIS2).\
                        filter(FACT_PMTCT_DHIS2.DHISOrgId == existing['DHISOrgId'], FACT_PMTCT_DHIS2.SiteCode == existing['SiteCode'], FACT_PMTCT_DHIS2.ReportMonth_Year == period).\
                        update({
                            "County": existing["County"],
                            "SubCounty": existing["SubCounty"],
                            "Ward": existing["Ward"],
                            "firstAncVisits": existing["firstAncVisits"],
                            "deliveryFromHivPosMothers": existing["deliveryFromHivPosMothers"],
                            "knownPosAt1stAnc": existing["knownPosAt1stAnc"],
                            "intialTestAtAnc": existing["intialTestAtAnc"],
                            "initialTestAtL_D": existing["initialTestAtL_D"],
                            "initialTestAtPnc_6wks": existing["initialTestAtPnc_6wks"],
                            "knownHivStatusTotal": existing["knownHivStatusTotal"],
                            "retestingPnc_6wks": existing["retestingPnc<=6wks"],
                            "testedPnc_6wksTo6mnts": existing["testedPnc>6wksTo6mnts"],
                            "knowPosAt1stAnc": existing["knowPosAt1stAnc"],
                            "posResultsAnc": existing["posResultsAnc"],
                            "posResultsL_D": existing["posResultsL&D"],
                            "posResultsPnc_6wks": existing["posResultsPnc<=6wks"],
                            "posPnc_6wksTo6mnts": existing["posPnc>6wksTo6mnts"],
                            "totalPos": existing["totalPos"],
                            "onHAARTat1stAnc": existing["onHAARTat1stAnc"],
                            "startHAARTanc": existing["startHAARTanc"],
                            "startHAARTL_D": existing["startHAARTL&D"],
                            "startHAARTpnc_6wks": existing["startHAARTpnc<=6wks"],
                            "onMaternalHAARTtotal": existing["onMaternalHAARTtotal"],
                            "startHAARTPnc_6wksto6mnts": existing["startHAARTPnc>6wksto6mnts"],
                            "onMaternalHAART12mnts": existing["onMaternalHAART12mnts"],
                            "newCohort12mths": existing["newCohort12mths"],
                            "syphilisScreened1stanc": existing["syphilisScreened1stanc"],
                            "syphilisScreenedPos": existing["syphilisScreenedPos"],
                            "syphilisTreated": existing["syphilisTreated"],
                            "HIVposMordernFP6wks": existing["HIVposMordernFP6wks"],
                            "HIVposPncVisits6wks": existing["HIVposPncVisits6wks"],
                            "knownStatus1stContact": existing["knownStatus1stContact"],
                            "initialTestANCMale": existing["initialTestANCMale"],
                            "initialTestL_DMale": existing["initialTestL&DMale"],
                            "initialTestPncMale": existing["initialTestPncMale"],
                            "totalKnownStatusMale": existing["totalKnownStatusMale"],
                            "_1stAncKPAdolescencts": existing["1stAncKPAdolescencts"],
                            "PosResultAdolescents": existing["PosResultAdolescents"],
                            "StartedHAARTAdolescentsTotal": existing["StartedHAARTAdolescentsTotal"],
                            "knownExposureAtPenta1": existing["knownExposureAtPenta1"],
                            "totalGivenPenta1": existing["totalGivenPenta1"],
                            "infantARVProphylANC": existing["infantARVProphylANC"],
                            "infantARVProphylL_D": existing["infantARVProphylL&D"],
                            "infantARVProphyl_8wksPNC": existing["infantARVProphyl<8wksPNC"],
                            "totalARVProphyl": existing["totalARVProphyl"],
                            "HEICtxDdsStart_2mnts": existing["HEICtxDdsStart<2mnts"],
                            "initialPCR_8wks": existing["initialPCR<8wks"],
                            "initialPCR_8wksTo12mnts": existing["initialPCR>8wksTo12mnts"],
                            "initialPCRtest_12mntsTotal": existing["initialPCRtest<12mntsTotal"],
                            "infected24mnts": existing["infected24mnts"],
                            "uninfected24mnts": existing["uninfected24mnts"],
                            "unknownOutcome": existing["netCohortHEI24mnts"],
                            "netCohortHEI24mnts": existing["unknownOutcome"],
                            "motherBabyPairs24mnts": existing["motherBabyPairs24mnts"],
                            "pairNetCohort24mnts": existing["pairNetCohort24mnts"],
                            "EBFat6mnts": existing["EBFat6mnts"],
                            "ERFat6mnts": existing["ERFat6mnts"],
                            "MFat6mnts": existing["MFat6mnts"],
                            "BFat12mnts": existing["BFat12mnts"],
                            "notBFat12mnts": existing["notBFat12mnts"],
                            "BFat18mnts": existing["BFat18mnts"],
                            "notBFat18mnts": existing["notBFat18mnts"]
                        })
                    db.commit()

            except Exception as e:
                print(e)
                db.rollback()
                raise HTTPException(
                    status_code=500, detail=f"Failed to save DHIS2 data.{e}")
            return {"new": records_to_merge, "updated": records_to_update}
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=500, detail="Failed to retrieve DHIS2 data.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
