import re
import pyodbc
from datetime import datetime
from fastapi import APIRouter
from app.serializers.facilityMetricsSerializer import facilityMetricsListEntity
from app.database import Notices
from app.config.config import settings

router = APIRouter()

def get_refresh_date():
	server = settings.DB_MSSQL_HOST
	database = settings.DB_MSSQL
	username = settings.DB_MSSQL_USERNAME
	password = settings.DB_MSSQL_PASS

	query = "SELECT MAX(LoadDate) FROM REPORTING.dbo.Linelist_FACTART"

	conn = pyodbc.connect(
		f'DRIVER=SQL Server;SERVER={server};DATABASE={database};UID={username};PWD={password}'
	)

	# Create a cursor to execute the query
	cursor = conn.cursor()

	# Execute the query
	cursor.execute(query)

	# Fetch the result (assuming only one row)
	row = cursor.fetchone()
	cursor.close()
	conn.close()
	return row

@router.get("/")
async def get_facility_metrics():
	notice = Notices.find_one({"title": "DWH REFRESH"})["message"]

	last_refresh_date = datetime.strptime(get_refresh_date()[0], "%Y-%m-%d")
	formatted_date = last_refresh_date.strftime("%b %d, %Y")

	# Define a regular expression pattern to match the date
	date_pattern = re.compile(r'\w{3} \d{4}')
	updated_string = re.sub(date_pattern, formatted_date, notice)

	Notices.update_one({"title": "DWH REFRESH"}, {"$set": {"message":updated_string}})
	
	return {'New Notice': updated_string}
