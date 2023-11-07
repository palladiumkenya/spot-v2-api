# spot-v2-api
API for spot v2

Provide a brief, descriptive name for your FastAPI application.

## Description

This application is meant to serve as the api backend for DWAPI SPOT version 2.

## Installation

Clone the repository 

```bash
# Navigate to the project directory
cd spot-v2-api

# Create a virtual environment (optional but recommended)
python -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```
## Configuration

Copy the .env.example into .env and populate it with your db credentials.

## Usage

```bash
# Start the  application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
## Endpoints
Once the apllication is running endpoint can be found via the swagger endpoint
http://localhost:8000/docs
or via redoc
http://localhost:8000/redoc


