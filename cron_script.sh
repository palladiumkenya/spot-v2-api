#!/bin/bash

# Define the endpoints and their respective schedules
ENDPOINT1="http://localhost:4141/api/process_ct_dhis2/latest"
ENDPOINT2="http://localhost:4141/api/process_hts_dhis2/latest"
ENDPOINT3="http://localhost:4141/api/process_pmtct_dhis2/latest"

# Add the cron jobs
echo "0 4 * * * curl $ENDPOINT1" >> /etc/cron.d/my-cron
echo "0 5 * * * curl $ENDPOINT2" >> /etc/cron.d/my-cron
echo "0 6 * * * curl $ENDPOINT3" >> /etc/cron.d/my-cron

# Apply the cron jobs
crontab /etc/cron.d/my-cron

# Start cron in the background
cron -f &
