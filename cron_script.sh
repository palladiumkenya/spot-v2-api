#!/bin/bash
# Define the endpoints and their respective schedules
ENDPOINT1="http://localhost:4141/api/dwh_refresh/"

# Add the cron jobs
echo "0 6 * * * curl $ENDPOINT1" >> /etc/cron.d/my-cron

# Apply the cron jobs
crontab /etc/cron.d/my-cron

# Start cron in the background
cron -f &
