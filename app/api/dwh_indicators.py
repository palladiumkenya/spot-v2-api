import requests
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy import text


def get_period():
    current_date = datetime.now()

    first_day_of_current_month = current_date.replace(day=1)
    last_day_of_last_month = first_day_of_current_month - timedelta(days=1)

    # date_object = datetime.strptime(last_day_of_last_month, "%Y-%m-%d")

    month = last_day_of_last_month.month
    year = last_day_of_last_month.year
    return month, year, last_day_of_last_month


def post_indicators(value, period, facility_info, indicator):
    try:
        client = requests.Session()
        response = client.post('https://spot.kenyahmis.org:4720/api/v1/metrics/facmetrics/dwhIndicator', json={
            'id': str(uuid4()),
            'facilityCode': facility_info['mfl_code'],
            'facilityName': facility_info['name'],
            'name': indicator,
            'value': value if value is not None else 0,
            'indicatorDate': period.strftime('%Y-%m-%d %H:%M:%S'),
            'stage': 'DWH',
            'facilityManifestId': None,
        }, timeout=300, verify=False)

        if response.status_code in [200, 201]:
            pass
        else:
            # logging.error('PostLiveSyncIndicator: failed to post indicator')
            pass

    except Exception as e:
        print(f'PostLiveSyncIndicator: failed to post indicator: {str(e)}')


def execute_query(db, query):
    return db.execute(text(query))


def fetch_and_post(db, facility, indicator_query, indicator_name):
    period = get_period()
    row = execute_query(db, indicator_query)
    post_indicators(row.scalar(), period[2], facility, indicator_name)
