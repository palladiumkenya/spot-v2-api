from bson import ObjectId
from datetime import datetime
import random
from app import schemas
from app import database


def seed_dockets(data):
    # Check if the collection is empty
    if database.Dockets.count_documents({}) == 0:
        # Iterate over the data and insert each item into the collection
        for item in data:
            schema = schemas.DocketSchema(
                name=item["name"],
                display=item["display"],
                extracts=[
                    schemas.ExtractSchema(**extract) for extract in item["extracts"]
                ],
            )
            database.Dockets.insert_one(schema.dict())

        print("Dockets data seeded successfully.")
    else:
        print("Dockets table already contains data. Skipping seed.")


def seed_indicators(data):
    # Check if the collection is empty
    if database.Indicators.count_documents({}) == 0:
        # Iterate over the data and insert each item into the collection
        for item in data:
            schema = schemas.IndicatorsBaseSchema(**item)
            database.Indicators.insert_one(schema.dict())

        print("Indicators data seeded successfully.")
    else:
        print("Indicators table already contains data. Skipping seed.")


def seed_notices(data):
    # Check if the collection is empty
    if database.Notices.count_documents({}) == 0:
        # Iterate over the data and insert each item into the collection
        for item in data:
            schema = schemas.NoticesBaseSchema(**item)
            database.Notices.insert_one(schema.dict())

        print("Notices data seeded successfully.")
    else:
        print("Notices table already contains data. Skipping seed.")


def seed_manifest(data):
    # Check if the collection is empty
    if database.Manifests.count_documents({}) == 0:
        docket = database.Dockets.aggregate([{"$sample": {"size": 1}}]).next()
        extract_definitions = docket["extracts"]
        # Iterate over the data and insert each item into the collection
        for item in data:
            # Assign a random extract ID as the extract_id
            random_extract = random.choice(extract_definitions)["id"]
            # Create the ManifestsSchema object with the random docket_id
            schema = schemas.ManifestsSchema(
                **item, docket_id=ObjectId(docket["_id"]), extract_id=random_extract)
            database.Manifests.insert_one(schema.dict())
        print("Manifests data seeded successfully.")
    else:
        print("Manifests table already contains data. Skipping seed.")

def create_profiles():
    if "profiles_vw" not in database.db.list_collection_names():
        pipeline = [
            {
                "$match": {"is_current": True}
            },
            {
                "$lookup": {
                    "from": "extracts",
                    "let": {
                        "manifest_id_field": "$manifest_id",
                        "extract_id_field": "$extract_id",
                        "mfl_code_field": "$mfl_code",
                    },
                    "pipeline": [
                        {
                            "$match": {
                                "$expr": {
                                    "$and": [
                                        { "$eq": ["$manifest_id", "$$manifest_id_field"] },
                                        { "$eq": ["$extract_id", "$$extract_id_field"] },
                                        { "$eq": ["$mfl_code", "$$mfl_code_field"] },
                                    ],
                                },
                            },
                        },
                    ],
                    "as": "extracts",
                },
            },
            {
                "$unwind": {
                    "path": "$extracts",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$lookup": {
                    "from": "facilities",
                    "localField": "mfl_code",
                    "foreignField": "mfl_code",
                    "as": "facility_info"
                }
            },
            {
                "$unwind": "$facility_info"
            },
            {
                "$lookup": {
                    "from": "dockets",
                    "localField": "docket_id",
                    "foreignField": "_id",
                    "as": "docket_info"
                }
            },
            {
                "$unwind": "$docket_info"  # Convert docket_info array to object
            },
            {
                "$sort": {
                    "updated_at": -1
                }
            },
            {
                "$group": {
                    "_id": {
						"facility": "$facility_info._id",
						"docket": "$docket_info._id"
					},  # Group by facility's _id & docket's _id
                    "facility": {"$first": "$facility_info.name"},
                    "mfl_code": {"$first": "$facility_info.mfl_code"},
                    "partner": {"$first": "$facility_info.partner"},
                    "county": {"$first": "$facility_info.county"},
                    "subcounty": {"$first": "$facility_info.subcounty"},
                    "agency": {"$first": "$facility_info.agency"},
                    "docket": {"$first": "$docket_info.name"},
                    "updated_at": {"$first": {"$ifNull": ["$extracts.updated_at", "$created_at"]}},
                    "totalExpected": {"$sum": {"$ifNull": ["$expected", 0]}},
                    "totalReceived": {"$sum": {"$ifNull": ["$extracts.received", 0]}},
                    "totalQueued": {"$sum": {"$ifNull": ["$extracts.queued", 0]}}
                }
            },
            {
                "$addFields": {
                    "status": {
                        "$switch": {
                            "branches": [
                                {
                                    "case": {"$eq": ["$totalQueued", "$totalExpected"]},
                                    "then": "Processed"
                                },
                                {
                                    "case": {"$eq": ["$totalReceived", "$totalExpected"]},
                                    "then": "Queued For Processing"
                                },
                                {
                                    "case": {"$eq": ["$totalReceived", 0]},
                                    "then": "Upload In Progress..."
                                }
                            ],
                            "default": "Upload In Progress..."
                        }
                    }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "facility": 1,
                    "mfl_code": 1,
                    "partner": 1,
                    "updated_at": 1,
                    "county": 1,
                    "subcounty": 1,
                    "agency": 1,
                    "docket": 1,
                    "status": 1,
                    "totalExpected": 1,
                    "totalReceived": 1,
                    "totalQueued": 1,
                }
            },
            {
                "$sort": {
                    "updated_at": -1
                }
            }
        ]
        database.db.command({"create": "profiles_vw", "viewOn":"manifests", "pipeline":pipeline})
        print("Profiles_vw data seeded successfully.")
    else:
        print("Profiles_vw already exists data. Skipping seed.")

# Define the data to seed
dockets = [
    {
        "name": "NDWH",
        "display": "NDWH",
        "extracts": [
            {"id": str(ObjectId()), "name": "PatientExtract", "display": "All Patients", "isPatient": True, "rank": 1},
            {"id": str(ObjectId()), "name": "PatientArtExtract", "display": "ART Patients", "isPatient": False, "rank": 2},
            {"id": str(ObjectId()), "name": "PatientBaselineExtract",
                "display": "Patient Baselines", "isPatient": False, "rank": 3},
            {"id": str(ObjectId()), "name": "PatientStatusExtract",
                "display": "Patient Status", "isPatient": False, "rank": 4},
            {"id": str(ObjectId()), "name": "PatientLabExtract",
                "display": "Patient Labs", "isPatient": False, "rank": 5},
            {"id": str(ObjectId()), "name": "PatientPharmacyExtract",
                "display": "Patient Pharmacy", "isPatient": False, "rank": 6},
            {"id": str(ObjectId()), "name": "PatientVisitExtract",
                "display": "Patient Visit", "isPatient": False, "rank": 7},
            {"id": str(ObjectId()), "name": "PatientAdverseEventExtract",
                "display": "Patient Adverse Events", "isPatient": False, "rank": 8},
            {"id": str(ObjectId()), "name": "AllergiesChronicIllnessExtract",
                "display": "Allergies ChronicIllness", "isPatient": False, "rank": 11},
            {"id": str(ObjectId()), "name": "IptExtract",
                "display": "IPT", "isPatient": False, "rank": 12},
            {"id": str(ObjectId()), "name": "DepressionScreeningExtract",
                "display": "Depression Screening", "isPatient": False, "rank": 13},
            {"id": str(ObjectId()), "name": "ContactListingExtract",
                "display": "Contact Listing", "isPatient": False, "rank": 14},
            {"id": str(ObjectId()), "name": "GbvScreeningExtract",
                "display": "GBV Screening", "isPatient": False, "rank": 15},
            {"id": str(ObjectId()), "name": "EnhancedAdherenceCounsellingExtract",
                "display": "Enhanced Adherence Counselling", "isPatient": False, "rank": 16},
            {"id": str(ObjectId()), "name": "DrugAlcoholScreeningExtract",
                "display": "Drug and Alcohol Screening", "isPatient": False, "rank": 17},
            {"id": str(ObjectId()), "name": "OvcExtract",
                "display": "OVC", "isPatient": False, "rank": 18},
            {"id": str(ObjectId()), "name": "OtzExtract",
                "display": "OTZ", "isPatient": False, "rank": 19},
            {"id": str(ObjectId()), "name": "CovidExtract",
                "display": "Covid", "isPatient": False, "rank": 20},
            {"id": str(ObjectId()), "name": "DefaulterTracingExtract", "display": "Defaulter Tracing",
                "isPatient": False, "rank": 21},
            {"id": str(ObjectId()), "name": "Detained",
                "display": "Patient Not Sent", "isPatient": False, "rank": 99}
        ]
    },
    {
        "name": "MNCH",
        "display": "MNCH",
        "extracts": [
            {"id": str(ObjectId()), "name": "PatientMnchExtract",
                "display": "Mnch Patient", "isPatient": True, "rank": 1},
            {"id": str(ObjectId()), "name": "MnchEnrolmentExtract",
                "display": "Mnch Enrolment", "isPatient": False, "rank": 2},
            {"id": str(ObjectId()), "name": "MnchArtExtract",
                "display": "Mnch Art", "isPatient": False, "rank": 21},
            {"id": str(ObjectId()), "name": "AncVisitExtract",
                "display": "Anc Visit", "isPatient": False, "rank": 22},
            {"id": str(ObjectId()), "name": "MatVisitExtract",
                "display": "Mat Visit", "isPatient": False, "rank": 23},
            {"id": str(ObjectId()), "name": "PncVisitExtract",
                "display": "Pnc Visit", "isPatient": False, "rank": 24},
            {"id": str(ObjectId()), "name": "MotherBabyPairExtract",
                "display": "Mother Baby Pair", "isPatient": False, "rank": 25},
            {"id": str(ObjectId()), "name": "CwcEnrolmentExtract",
                "display": "Cwc Enrolment", "isPatient": False, "rank": 26},
            {"id": str(ObjectId()), "name": "CwcVisitExtract",
                "display": "Cwc Visit", "isPatient": False, "rank": 27},
            {"id": str(ObjectId()), "name": "HeiExtract",
                "display": "Hei", "isPatient": False, "rank": 28},
            {"id": str(ObjectId()), "name": "MnchLabExtract",
                "display": "Mnch Labs", "isPatient": False, "rank": 29}
        ]
    },
    {
        "name": "PREP",
        "display": "PREP",
        "extracts": [
            {"id": str(ObjectId()), "name": "PatientPrepExtract",
                "display": "Patient Prep", "isPatient": True, "rank": 30},
            {"id": str(ObjectId()), "name": "PrepBehaviourRiskExtract",
                "display": "Prep Behaviour Risk", "isPatient": False, "rank": 31},
            {"id": str(ObjectId()), "name": "PrepVisitExtract",
                "display": "Prep Visit", "isPatient": False, "rank": 32},
            {"id": str(ObjectId()), "name": "PrepLabExtract",
                "display": "Prep Labs", "isPatient": False, "rank": 33},
            {"id": str(ObjectId()), "name": "PrepPharmacyExtract",
                "display": "Prep Pharmacy", "isPatient": False, "rank": 34},
            {"id": str(ObjectId()), "name": "PrepAdverseEventExtract",
                "display": "Prep Adverse Events", "isPatient": False, "rank": 35},
            {"id": str(ObjectId()), "name": "PrepCareTerminationExtract",
                "display": "Prep Care Termination", "isPatient": False, "rank": 35}
        ]
    },
    {
        "name": "HTS",
        "display": "HTS",
        "extracts": [
            {"id": str(ObjectId()), "name": "HtsClientExtract",
                "display": "Hts Clients", "isPatient": True, "rank": 1},
            {"id": str(ObjectId()), "name": "HtsClientTestsExtract",
                "display": "Hts Client Tests", "isPatient": False, "rank": 2},
            {"id": str(ObjectId()), "name": "HtsClientLinkageExtract",
                "display": "Hts Client Linkage", "isPatient": False, "rank": 3},
            {"id": str(ObjectId()), "name": "HtsTestKitsExtract",
                "display": "Hts Test Kits", "isPatient": False, "rank": 4},
            {"id": str(ObjectId()), "name": "HtsClientTracingExtract",
                "display": "Hts Client Tracing", "isPatient": False, "rank": 5},
            {"id": str(ObjectId()), "name": "HtsPartnerTracingExtract",
                "display": "Hts Partner Tracing", "isPatient": False, "rank": 6},
            {"id": str(ObjectId()), "name": "HtsPartnerNotificationServicesExtract",
                "display": "Hts Partner Notification Services", "isPatient": False, "rank": 7}
        ]
    }
]

indicators = [
    {
        "mfl_code": "14020",
        "facility_manifestid": "456",
        "name": "TX_CURR",
        "emr_value": 890,
        "emr_indicator_date": "2023-06-21T18:21:39.322466",
        "dwh_value": None,
        "dwh_indicator_date": None,
        "is_current": True
    },
    {
        "mfl_code": "12663",
        "facility_manifestid": "012",
        "name": "TX_NEW",
        "emr_value": 20,
        "emr_indicator_date": "2023-06-21T18:21:39.322466",
        "dwh_value": 22,
        "dwh_indicator_date": "2023-06-21T18:21:39.322466",
        "is_current": True
    }
]

notices = [
    {
        "message": "It may take upto 1 HOUR for data to be processed and displayed after being SENT",
        "rank": 1,
        "level": 1,
        "title": ""
    },
    {
        "message": "The last refresh was on Tue Jun 20 2023",
        "rank": 1,
        "level": 2,
        "title": "DWH REFRESH"
    }
]

manifests = [
    {
        "manifest_id": str(ObjectId()),
        "mfl_code": 12663,
        "session": str(ObjectId()),
        "received": 240,
        "start": datetime.now(),
        "end": datetime.now(),
        "is_current": False
    }
]


def seed():
    # Seed the data into the database
    seed_dockets(dockets)
    seed_indicators(indicators)
    seed_notices(notices)
    seed_manifest(manifests)
    create_profiles()
