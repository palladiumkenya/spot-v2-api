from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import aiocron
from app.routers import mockapis
from app.routers import notices
from app.routers import facilities
from app.routers import indicators
from app.api.facilities import get_all_facilities
from app import seeder
# from app.consumer.testConsumer import consume_messages
from app.consumer.indicatorConsumer import consume_messages

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
    # Start consuming messages on application startup
    asyncio.create_task(consume_messages())
    
    # Seed the data into the database
    seeder.seed()

    # Schedule the task to run every 4 hrs
    cron = aiocron.crontab('0 */4 * * *', func=get_all_facilities)
    await asyncio.sleep(1)
    cron.start()

# ...other routes and application code...
app.include_router(mockapis.router)
app.include_router(facilities.router, tags=['Facilities'], prefix='/api/update_facilities')
app.include_router(notices.router, tags=['Notices'], prefix='/api/notices')
app.include_router(indicators.router, tags=['Indicators'], prefix='/api/indicators')

@app.get("/api/healthchecker")
def root():
    return {"message": "Welcome to SPOTv2, we are up and running"}

# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)