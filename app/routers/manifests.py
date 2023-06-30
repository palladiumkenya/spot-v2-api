from fastapi import APIRouter
from app.serializers.manifestSerializer import manifestListEntity
from app.database import Manifests

router = APIRouter()

@router.get("/")
async def get_extracts_progress():
	pipeline = [
		{"$match": {"is_current": True}},
		{"$lookup": {
			"from": "facilities",
			"localField": "mfl_code",
			"foreignField": "mfl_code",
			"as": "facility_info"
		}},
		{"$unwind": "$facility_info"},
		{"$lookup": {
			"from": "dockets",
			"let": {"extractId": "$extract_id"},
			"pipeline": [
				{"$match": {
					"$expr": {"$in": ["$$extractId", "$extracts.id"]}
				}},
				{"$project": {
					"display": {
						"$arrayElemAt": [
							{"$filter": {
								"input": "$extracts",
								"cond": {"$eq": ["$$this.id", "$$extractId"]}
							}},
							0
						]
					}
				}}
			],
			"as": "extract_info"
		}},
		{"$unwind": "$extract_info"},
		{"$lookup": {
			"from": "dockets",
			"localField": "docket_id",
			"foreignField": "_id",
			"as": "docket_info"
		}},
		{"$unwind": "$docket_info"},
		{"$addFields": {
			"status": {
				"$cond": [
					{"$eq": ["$queued", "$received"]},
					"Processed",
					{"$cond": [
						{"$eq": ["$received", "$expected"]},
						"Upload Complete",
						{"$cond": [
							{"$eq": ["$received", 0]},
							"Upload Not Started",
							"Upload In Progress..."
						]}
					]}
				]
			}
		}},
		{"$group": {
			"_id": {
				"facility": "$facility_info._id",
				"docket": "$docket_info._id"
			},
			"docket": { "$first": "$docket_info.display" },
			"mfl_code": { "$first": "$facility_info.mfl_code" },
			"documents": {
				"$push": {
					"code": {"$toString": "$mfl_code"},
					"facility": "$facility_info.name",
					"docket": "$docket_info.display",
					"extract_display_name": "$extract_info.display.display",
					"status": "$status",
					"received": "$received",
					"expected": "$expected",
					"queued": "$queued",
					"rank": "$extract_info.display.rank",
					"updated_at": "$updated_at"
				}
			}
		}},
		{"$sort": {"documents.rank": 1}}
	]
	manifests = manifestListEntity(Manifests.aggregate(pipeline))
	return {'manifests': manifests}

@router.get("/{code}")
async def get_extracts_progress(code: int):
	pipeline = [
		{"$match": {"is_current": True, "mfl_code" : code}},
		{"$lookup": {
			"from": "facilities",
			"localField": "mfl_code",
			"foreignField": "mfl_code",
			"as": "facility_info"
		}},
		{"$unwind": "$facility_info"},
		{"$lookup": {
			"from": "dockets",
			"let": {"extractId": "$extract_id"},
			"pipeline": [
				{"$match": {
					"$expr": {"$in": ["$$extractId", "$extracts.id"]}
				}},
				{"$project": {
					"display": {
						"$arrayElemAt": [
							{"$filter": {
								"input": "$extracts",
								"cond": {"$eq": ["$$this.id", "$$extractId"]}
							}},
							0
						]
					}
				}}
			],
			"as": "extract_info"
		}},
		{"$unwind": "$extract_info"},
		{"$lookup": {
			"from": "dockets",
			"localField": "docket_id",
			"foreignField": "_id",
			"as": "docket_info"
		}},
		{"$unwind": "$docket_info"},
		{"$addFields": {
			"status": {
				"$cond": [
					{"$eq": ["$queued", "$received"]},
					"Processed",
					{"$cond": [
						{"$eq": ["$received", "$expected"]},
						"Upload Complete",
						{"$cond": [
							{"$eq": ["$received", 0]},
							"Upload Not Started",
							"Upload In Progress..."
						]}
					]}
				]
			}
		}},
		{"$group": {
			"_id": {
				"facility": "$facility_info._id",
				"docket": "$docket_info._id"
			},
			"docket": { "$first": "$docket_info.display" },
			"mfl_code": { "$first": "$facility_info.mfl_code" },
			"documents": {
				"$push": {
					"code": {"$toString": "$mfl_code"},
					"facility": "$facility_info.name",
					"docket": "$docket_info.display",
					"extract_display_name": "$extract_info.display.display",
					"status": "$status",
					"received": "$received",
					"expected": "$expected",
					"queued": "$queued",
					"rank": "$extract_info.display.rank",
					"updated_at": "$updated_at"
				}
			}
		}},
		{"$sort": {"documents.rank": 1}}
	]
	manifests = manifestListEntity(Manifests.aggregate(pipeline))
	return {'manifests': manifests}

