from datetime import datetime
from dotenv import load_dotenv
from .models import FACT_HTS_DHIS2
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

@router.get("/process_hts_dhis2/latest")
async def process_hts_dhis2(db: Session = Depends(get_db)):
    try:
        current_date = datetime.now()
        previous_month = current_date - timedelta(days=current_date.day)
        period = previous_month.strftime('%Y%m')

        data = process_hts_service(period, db)
        print(data.keys())
        # Perform the merge operation for the filtered records
        db.bulk_insert_mappings(FACT_HTS_DHIS2, data["new"])
        db.commit()
        return {"message": "HTS Dhis2 Dwh data processed successfully.", "records": {"new": len(data["new"]), "updated": len(data["updated"])}}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/process_hts_dhis2/{period}")
async def process_hts_dhis2(period: str, db: Session = Depends(get_db)):
    try:
        data = process_hts_service(period, db)
        print(data.keys())
        # Perform the merge operation for the filtered records
        db.bulk_insert_mappings(FACT_HTS_DHIS2, data["new"])
        db.commit()
        return {"message": "HTS Dhis2 Dwh data processed successfully.", "records": {"new": len(data["new"]), "updated": len(data["updated"])}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def process_hts_service(period, db):
    try:
        dhis2_api_base_url = settings.DHIS2_API_BASE_URL
        dhis2_username = settings.DHIS2_USERNAME
        dhis2_password = settings.DHIS2_PASSWORD
        
        ou = "dimension=ou:LEVEL-5;"
        de = "dimension=dx:NOga2tabGrd;dlldM4hP2Wk;OePJt8CcZ0d;lj9QYJqS7bN;gMICOUtzqRb;XiRbc0DSMOH;YXJf27jfkvS;pkShOkgNQt2;JiuqbydCIcy;gTkVw97FnQK;atSQz5O7e2A;du5RMT3aecB;D9YwtS6RhQ1;wu0ITFRjUzF;kLXGWRLzCAw;xMNhnyu7vm1;F9OR49Lc1aR;oCFXmpol7D8;J4vNm7YEkdj;cBTa1jVzT8f;"
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
                            data["County"] = row[1].replace(" County", "").strip() if row[1].strip() != "" else None
                            data["SubCounty"] = row[2].replace(" Sub County", "").strip() if row[2].strip() != "" else None
                            data["Ward"] = row[3].replace(" Ward", "").strip() if row[3].strip() != "" else None
                            data["DHISOrgId"] = row[5].strip() if row[5].strip() != "" else None
                            data["FacilityName"] = row[6].strip() if row[6].strip() != "" else None
                            data["SiteCode"] = row[7].strip() if row[7].strip() != "" else None
                            data["ReportMonth_Year"] = period
                            data["Tested_Total"] = int(row[9]) if row[9].strip() != "" else None
                            data["Positive_Total"] = int(row[10]) if row[10].strip() != "" else None
                            data["Tested_1_9"] = int(row[11]) if row[11].strip() != "" else None
                            data["Tested_10_14_M"] = int(row[12]) if row[12].strip() != "" else None
                            data["Tested_10_14_F"] = int(row[13]) if row[13].strip() != "" else None
                            data["Tested_15_19_M"] = int(row[14]) if row[14].strip() != "" else None
                            data["Tested_15_19_F"] = int(row[15]) if row[15].strip() != "" else None
                            data["Tested_20_24_M"] = int(row[16]) if row[16].strip() != "" else None
                            data["Tested_20_24_F"] = int(row[17]) if row[17].strip() != "" else None
                            data["Tested_25_Plus_M"] = int(row[18]) if row[18].strip() != "" else None
                            data["Tested_25_Plus_F"] = int(row[19]) if row[19].strip() != "" else None
                            data["Positive_1_9"] = int(row[20]) if row[20].strip() != "" else None
                            data["Positive_10_14_M"] = int(row[21]) if row[21].strip() != "" else None
                            data["Positive_10_14_F"] = int(row[22]) if row[22].strip() != "" else None
                            data["Positive_15_19_M"] = int(row[23]) if row[23].strip() != "" else None
                            data["Positive_15_19_F"] = int(row[24]) if row[24].strip() != "" else None
                            data["Positive_20_24_M"] = int(row[25]) if row[25].strip() != "" else None
                            data["Positive_20_24_F"] = int(row[26]) if row[26].strip() != "" else None
                            data["Positive_25_Plus_M"] = int(row[27]) if row[27].strip() != "" else None
                            data["Positive_25_Plus_F"] = int(row[28]) if row[28].strip() != "" else None

                            ct_data.append(data)
                            
                        except ValueError:
                            raise HTTPException(
                                status_code=500, detail="Invalid data in the response.")
            try:
                # Filter out duplicate records by checking if they already exist in the database
                existing_records = db.query(FACT_HTS_DHIS2).filter(FACT_HTS_DHIS2.DHISOrgId.in_([r['DHISOrgId'] for r in ct_data]),
                                                                    FACT_HTS_DHIS2.SiteCode.in_([r['SiteCode'] for r in ct_data]),
                                                                    FACT_HTS_DHIS2.ReportMonth_Year.in_([r['ReportMonth_Year'] for r in ct_data])).all()
                existing_record_ids = {(rec.DHISOrgId, rec.SiteCode, rec.ReportMonth_Year) for rec in existing_records}
                records_to_merge = [rec for rec in ct_data if (rec['DHISOrgId'], rec['SiteCode'], rec['ReportMonth_Year']) not in existing_record_ids]
                records_to_update = [rec for rec in ct_data if (rec['DHISOrgId'], rec['SiteCode'], rec['ReportMonth_Year']) in existing_record_ids]

                for existing in records_to_update:
                    db.query(FACT_HTS_DHIS2).\
                        filter(FACT_HTS_DHIS2.DHISOrgId == existing['DHISOrgId'], FACT_HTS_DHIS2.SiteCode == existing['SiteCode'], FACT_HTS_DHIS2.ReportMonth_Year == period).\
                        update({
                            "County": existing["County"],
                            "FacilityName": existing["FacilityName"],
                            "SubCounty": existing["SubCounty"],
                            "Ward": existing["Ward"],
                            "Tested_Total": existing["Tested_Total"],
                            "Positive_Total": existing["Positive_Total"],
                            "Tested_1_9": existing["Tested_1_9"],
                            "Tested_10_14_M": existing["Tested_10_14_M"],
                            "Tested_10_14_F": existing["Tested_10_14_F"],
                            "Tested_15_19_M": existing["Tested_15_19_M"],
                            "Tested_15_19_F": existing["Tested_15_19_F"],
                            "Tested_20_24_M": existing["Tested_20_24_M"],
                            "Tested_20_24_F": existing["Tested_20_24_F"],
                            "Tested_25_Plus_M": existing["Tested_25_Plus_M"],
                            "Tested_25_Plus_F": existing["Tested_25_Plus_F"],
                            "Positive_1_9": existing["Positive_1_9"],
                            "Positive_10_14_M": existing["Positive_10_14_M"],
                            "Positive_10_14_F": existing["Positive_10_14_F"],
                            "Positive_15_19_M": existing["Positive_15_19_M"],
                            "Positive_15_19_F": existing["Positive_15_19_F"],
                            "Positive_20_24_M": existing["Positive_20_24_M"],
                            "Positive_20_24_F": existing["Positive_20_24_F"],
                            "Positive_25_Plus_M": existing["Positive_25_Plus_M"],
                            "Positive_25_Plus_F": existing["Positive_25_Plus_F"]})
                    db.commit()
                print(existing_records, records_to_update, len(records_to_merge))

            except IntegrityError as e:
                db.rollback()
            return {"new": records_to_merge, "updated": records_to_update }
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=500, detail="Failed to retrieve DHIS2 data.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
