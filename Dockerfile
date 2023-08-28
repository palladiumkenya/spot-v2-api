# Base image
FROM python:3.9-slim

# Install cron and git
RUN apt-get update && apt-get install -y cron git

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Install curl and ODBC
RUN apt-get update && apt-get install -y curl unixodbc

# Expose the port
EXPOSE 4141

# Copy the cron script
COPY cron_script.sh /app

# Set execution permissions for the cron script
RUN chmod +x /app/cron_script.sh

# Set up cron job
RUN crontab /app/crontab.txt

# Command to run the application and start the cron job
CMD /app/cron_script.sh && uvicorn app.main:app --host 0.0.0.0 --port 2121
