def facilityMetricsEntity(metric) -> dict:
    return {
		"mfl_code": int(metric["mfl_code"]),
		"metric": metric["metric"],
		"value": metric["value"],
		"is_current": metric["is_current"],
    }

def facilityMetricsListEntity(metrics) -> list:
    return [facilityMetricsEntity(metric) for metric in metrics]

