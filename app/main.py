from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import aiormq
import aiocron
from app.routers import mockapis
from app.routers import notices
from app.routers import facilities
from app.routers import indicators
from app.routers import manifests
from app.routers import profiles
from app.routers import facility_metrics
from app.routers import refresh_messages
from app.routers import bi_directional_communication
from app.routers import dwh_refresh
from app import seeder
# from app.consumer.testConsumer import consume_messages
from app.consumer import indicatorConsumer
from app.consumer import manifestConsumer
from app.consumer import extractConsumer
from app.consumer import handshakeConsumer
from app.error_handler import *

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.add_exception_handler(HTTPException, http_error_handler)
# app.add_exception_handler(Exception, tasks_error_handler)

@app.on_event("startup")
async def startup_event():
    start_background_tasks()

def start_background_tasks():
    try:
        # Start consuming messages on application startup
        asyncio.create_task(indicatorConsumer.consume_messages())
        asyncio.create_task(manifestConsumer.consume_messages())
        asyncio.create_task(extractConsumer.consume_messages())
        asyncio.create_task(handshakeConsumer.consume_messages())
    except aiormq.AMQPError as e:
        print(f"Error occurred: {type(e).__name__}: {e}")
        print("Retrying connection...")
    finally:
        asyncio.sleep(500)  # Wait for 500 seconds before retrying the connection

    # Seed the data into the database
    seeder.seed()
    asyncio.sleep(1)

# ...other routes and application code...
app.include_router(mockapis.router)
app.include_router(facilities.router, tags=['Facilities'], prefix='/api/facilities')
app.include_router(notices.router, tags=['Notices'], prefix='/api/notices')
app.include_router(dwh_refresh.router, tags=['Notices'], prefix='/api/dwh_refresh')
app.include_router(indicators.router, tags=['Indicators'], prefix='/api/indicators')
app.include_router(profiles.router, tags=['Profiles'], prefix='/api/profiles')
app.include_router(manifests.router, tags=['Manifests'], prefix='/api/manifests')
app.include_router(facility_metrics.router, tags=['Facility Metrics'], prefix='/api/metrics')
app.include_router(refresh_messages.router, tags=['Resend Rabbit Messages'], prefix='/api/messages')
app.include_router(bi_directional_communication.router, tags=['DWAPI Bi-directional Communication'], prefix='/bi_directional_communication')

@app.get("/api/healthchecker")
def root():
    return {"message": "Welcome to SPOTv2, we are up and running"}

# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)