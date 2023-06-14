from datetime import datetime
from dotenv import load_dotenv
from .models import FACT_CT_DHIS2
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

@router.get("/process_ct_dhis2/latest")
async def process_ct_dhis2(db: Session = Depends(get_db)):
    try:
        current_date = datetime.now()
        previous_month = current_date - timedelta(days=current_date.day)
        period = previous_month.strftime('%Y%m')
        
        data = process_ct_service(period, db)
        # Perform the merge operation for the filtered records
        # db.bulk_insert_mappings(FACT_CT_DHIS2, data["new"])
        # db.commit()
        return {"message": "CT Dhis2 Dwh data processed successfully.", "records": {"new": len(data["new"]), "updated": len(data["updated"])}}
    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/process_ct_dhis2/{period}")
async def process_ct_dhis2(period: str, db: Session = Depends(get_db)):
    try:
        data = process_ct_service(period, db)
        # Perform the merge operation for the filtered records
        # db.bulk_insert_mappings(FACT_CT_DHIS2, data["new"])
        # db.commit()
        return {"message": "CT Dhis2 Dwh data processed successfully.", "records": {"new":  len(data["new"]), "updated": len(data["updated"])}}
    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

def process_ct_service(period, db):
    try:
        
        dhis2_api_base_url = settings.DHIS2_API_BASE_URL
        dhis2_username = settings.DHIS2_USERNAME
        dhis2_password = settings.DHIS2_PASSWORD
        
        ou = "dimension=ou:LEVEL-5;"
        de = "dimension=dx:JljuWsCDpma;sEtNuNusKTT;PUrg2dmCjGI;QrHtUO7UsaM;S1z1doLHQg1;cbrwRebovN1;RNfqUayuZP2;MR5lxj7v7Lt;mACm1JUzeLT;Hbc2qRi0U5x;LC2OqnUC5Sn;jthpt5cVV9c;yWkSi8L3qGm;DaNcGZnkclz;K59f8nZ5vhy;zNCSlBKbS6d;SCMKsiNj6c5;Nv4OkbdDvmm;SJL4k6Gl53C;wbJOu4h2SSz;Jbu4if6gtDp;GSEmLUnrvzj;oOOnacUi9Jm;AQsTt7jtKbt;e93GKJTHKAX;EhZQp3PTA3C;pR7VzBydoj3;yNCUlEYkmyA;"
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
                            data = {
                                'County': row[1].replace(" County", "") if row[1].strip() != "" else None,
                                'SubCounty': row[2].replace(" Sub County", "") if row[2].strip() != "" else None,
                                'Ward': row[3].replace(" Ward", "") if row[3].strip() != "" else None,
                                'DHISOrgId': row[5] if row[5].strip() != "" else None,
                                'FacilityName': row[6] if row[6].strip() != "" else None,
                                'SiteCode': row[7] if row[7].strip() != "" else None,
                                'ReportMonth_Year': period,
                                'Enrolled_Total': int(row[9]) if row[9].strip() != "" else None,
                                'StartedART_Total': int(row[10]) if row[10].strip() != "" else None,
                                'CurrentOnART_Total': int(row[11]) if row[11].strip() != "" else None,
                                'CTX_Total': int(row[12]) if row[12].strip() != "" else None,
                                'OnART_12Months': int(row[13]) if row[13].strip() != "" else None,
                                'NetCohort_12Months': int(row[14]) if row[14].strip() != "" else None,
                                'VLSuppression_12Months': int(row[15]) if row[15].strip() != "" else None,
                                'VLResultAvail_12Months': int(row[16]) if row[16].strip() != "" else None,
                                'Start_ART_Under_1': int(row[17]) if row[17].strip() != "" else None,
                                'Start_ART_1_9': int(row[18]) if row[18].strip() != "" else None,
                                'Start_ART_10_14_M': int(row[19]) if row[19].strip() != "" else None,
                                'Start_ART_10_14_F': int(row[20]) if row[20].strip() != "" else None,
                                'Start_ART_15_19_M': int(row[21]) if row[21].strip() != "" else None,
                                'Start_ART_15_19_F': int(row[22]) if row[22].strip() != "" else None,
                                'Start_ART_20_24_M': int(row[23]) if row[23].strip() != "" else None,
                                'Start_ART_20_24_F': int(row[24]) if row[24].strip() != "" else None,
                                'Start_ART_25_Plus_M': int(row[25]) if row[25].strip() != "" else None,
                                'Start_ART_25_Plus_F': int(row[26]) if row[26].strip() != "" else None,
                                'On_ART_Under_1': int(row[27]) if row[27].strip() != "" else None,
                                'On_ART_1_9': int(row[28]) if row[28].strip() != "" else None,
                                'On_ART_10_14_M': int(row[29]) if row[29].strip() != "" else None,
                                'On_ART_10_14_F': int(row[30]) if row[30].strip() != "" else None,
                                'On_ART_15_19_M': int(row[31]) if row[31].strip() != "" else None,
                                'On_ART_15_19_F': int(row[32]) if row[32].strip() != "" else None,
                                'On_ART_20_24_M': int(row[33]) if row[33].strip() != "" else None,
                                'On_ART_20_24_F': int(row[34]) if row[34].strip() != "" else None,
                                'On_ART_25_Plus_M': int(row[35]) if row[35].strip() != "" else None,
                                'On_ART_25_Plus_F': int(row[36]) if row[36].strip() != "" else None
                            }
                            ct_data.append(data)
                            
                        except ValueError:
                            raise HTTPException(
                                status_code=500, detail="Invalid data in the response.")
            try:
                # Filter out duplicate records by checking if they already exist in the database
                existing_records = db.query(FACT_CT_DHIS2).filter(FACT_CT_DHIS2.DHISOrgId.in_([r['DHISOrgId'] for r in ct_data]),
                                                                    FACT_CT_DHIS2.SiteCode.in_([r['SiteCode'] for r in ct_data]),
                                                                    FACT_CT_DHIS2.ReportMonth_Year.in_([r['ReportMonth_Year'] for r in ct_data])).all()
                existing_record_ids = {(rec.DHISOrgId, rec.SiteCode, rec.ReportMonth_Year) for rec in existing_records}
                records_to_merge = [rec for rec in ct_data if (rec['DHISOrgId'], rec['SiteCode'], rec['ReportMonth_Year']) not in existing_record_ids]
                records_to_update = [rec for rec in ct_data if (rec['DHISOrgId'], rec['SiteCode'], rec['ReportMonth_Year']) in existing_record_ids]
                
                for existing in records_to_update:
                    db.query(FACT_CT_DHIS2).\
                        filter(FACT_CT_DHIS2.DHISOrgId == existing['DHISOrgId'], FACT_CT_DHIS2.SiteCode == existing['SiteCode'], FACT_CT_DHIS2.ReportMonth_Year == period).\
                        update({
                                'County': existing['County'],
                                'SubCounty': existing['SubCounty'],
                                'Ward': existing['Ward'],
                                'FacilityName': existing['FacilityName'],
                                'Enrolled_Total': existing['Enrolled_Total'],
                                'StartedART_Total': existing['StartedART_Total'],
                                'CurrentOnART_Total': existing['CurrentOnART_Total'],
                                'CTX_Total': existing['CTX_Total'],
                                'OnART_12Months': existing['OnART_12Months'],
                                'NetCohort_12Months': existing['NetCohort_12Months'],
                                'VLSuppression_12Months': existing['VLSuppression_12Months'],
                                'VLResultAvail_12Months': existing['VLResultAvail_12Months'],
                                'Start_ART_Under_1': existing['Start_ART_Under_1'],
                                'Start_ART_1_9': existing['Start_ART_1_9'],
                                'Start_ART_10_14_M': existing['Start_ART_10_14_M'],
                                'Start_ART_10_14_F': existing['Start_ART_10_14_F'],
                                'Start_ART_15_19_M': existing['Start_ART_15_19_M'],
                                'Start_ART_15_19_F': existing['Start_ART_15_19_F'],
                                'Start_ART_20_24_M': existing['Start_ART_20_24_M'],
                                'Start_ART_20_24_F': existing['Start_ART_20_24_F'],
                                'Start_ART_25_Plus_M': existing['Start_ART_25_Plus_M'],
                                'Start_ART_25_Plus_F': existing['Start_ART_25_Plus_F'],
                                'On_ART_Under_1': existing['On_ART_Under_1'],
                                'On_ART_1_9': existing['On_ART_1_9'],
                                'On_ART_10_14_M': existing['On_ART_10_14_M'],
                                'On_ART_10_14_F': existing['On_ART_10_14_F'],
                                'On_ART_15_19_M': existing['On_ART_15_19_M'],
                                'On_ART_15_19_F': existing['On_ART_15_19_F'],
                                'On_ART_20_24_M': existing['On_ART_20_24_M'],
                                'On_ART_20_24_F': existing['On_ART_20_24_F'],
                                'On_ART_25_Plus_M': existing['On_ART_25_Plus_M'],
                                'On_ART_25_Plus_F': existing['On_ART_25_Plus_F']})
                    db.commit()

                # Perform the merge operation for the filtered records
                db.bulk_insert_mappings(FACT_CT_DHIS2, records_to_merge)
                db.commit()

            except IntegrityError as e:
                db.rollback()
                print(f"Error occurred during merge: {e}")
            return {"new": records_to_merge, "updated": records_to_update }
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=500, detail="Failed to retrieve DHIS2 data.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
