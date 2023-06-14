from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models, fact_ct_dhis2, fact_hts_dhis2, fact_pmtct_dhis2
from .database import engine

models.Base.metadata.create_all(bind=engine)

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


app.include_router(fact_ct_dhis2.router, tags=['CT DHIS2'], prefix='/api')
app.include_router(fact_hts_dhis2.router, tags=['HTS DHIS2'], prefix='/api')
app.include_router(fact_pmtct_dhis2.router, tags=['PMTCT DHIS2'], prefix='/api')


@app.get("/api/healthchecker")
def root():
    return {"message": "Welcome to FastAPI with DHIS2/3pm Pull"}

