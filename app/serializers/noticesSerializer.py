def noticeEntity(notice) -> dict:
    return {
        "id": str(notice["_id"]),
        "rank": int(notice["rank"]),
		"level": int(notice["level"]),
		"title": notice.get("title", ""),
		"message": notice["message"],
    }

def noticesListEntity(notices) -> list:
    return [noticeEntity(notice) for notice in notices]
