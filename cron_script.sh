#!/bin/bash
# Define the endpoints and their respective schedules
ENDPOINT1="http://localhost:4141/api/dwh_refresh/"
ENDPOINT2="http://localhost:4141/api/facilities/update_facilities"

# Add the cron jobs
echo "0 6 * * * curl $ENDPOINT1" >> /etc/cron.d/my-cron
echo "0 */4 * * * curl $ENDPOINT2" >> /etc/cron.d/my-cron

# Apply the cron jobs
crontab /etc/cron.d/my-cron

# Start cron in the background
cron -f &
