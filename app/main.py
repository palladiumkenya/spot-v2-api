from fastapi import FastAPI
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
from app.api.facilities import get_all_facilities
from app import seeder
# from app.consumer.testConsumer import consume_messages
from app.consumer import indicatorConsumer
from app.consumer import manifestConsumer
from app.consumer import extractConsumer

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

@app.on_event("startup")
async def startup_event():
    try:
        # Start consuming messages on application startup
        asyncio.create_task(indicatorConsumer.consume_messages())
        asyncio.create_task(manifestConsumer.consume_messages())
        asyncio.create_task(extractConsumer.consume_messages())
    except aiormq.AMQPError as e:
        print(f"Error occurred: {type(e).__name__}: {e}")
        print("Retrying connection...")
        # finally:
        #     await asyncio.sleep(5)  # Wait for 5 seconds before retrying the connection

    # Seed the data into the database
    seeder.seed()

    # Schedule the task to run every 4 hrs
    ## TODO: LOOK FOR EFFICIENT WAY
    # cron = aiocron.crontab('0 */4 * * *', func=get_all_facilities)
    # await asyncio.sleep(1)
    # cron.start()

# ...other routes and application code...
app.include_router(mockapis.router)
app.include_router(facilities.router, tags=['Facilities'], prefix='/api/facilities')
app.include_router(notices.router, tags=['Notices'], prefix='/api/notices')
app.include_router(indicators.router, tags=['Indicators'], prefix='/api/indicators')
app.include_router(profiles.router, tags=['Profiles'], prefix='/api/profiles')
app.include_router(manifests.router, tags=['Manifests'], prefix='/api/manifests')
app.include_router(facility_metrics.router, tags=['Facility Metrics'], prefix='/api/metrics')

@app.get("/api/healthchecker")
def root():
    return {"message": "Welcome to SPOTv2, we are up and running"}

# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)