import re
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from app.database import Notices, get_db

router = APIRouter()

def get_refresh_date(db):
	query = text("SELECT MAX(LoadDate) FROM REPORTING.dbo.Linelist_FACTART")
	row = db.execute(query)

	return row.scalar()


@router.get("/")
async def get_update_dwh_refresh_date(db: Session = Depends(get_db)):
	notice = Notices.find_one({"title": "DWH REFRESH"})["message"]

	last_refresh_date = get_refresh_date(db)
	formatted_date = last_refresh_date.strftime("%b %d, %Y")

	# Define a regular expression pattern to match the date
	date_pattern = re.compile(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{1,2},\s\d{4}\b")
	updated_string = re.sub(date_pattern, formatted_date, notice)

	Notices.update_one({"title": "DWH REFRESH"}, {"$set": {"message":updated_string}})
	
	return {'New Notice': updated_string}
