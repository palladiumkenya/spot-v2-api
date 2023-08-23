from fastapi.responses import JSONResponse
from app.database import Error

# HTTP Error Handler
async def http_error_handler(request, exc):
    error_data = {
        "method": request.method,
        "url": str(request.url),
        "detail": str(exc.detail),
        "status_code": exc.status_code,
        "event": "http" 
    }
    Error.insert_one(error_data)
    return JSONResponse(content={"message": "An error occurred. Please try again later."}, status_code=exc.status_code)

# Other Tasks Errors Handler
async def tasks_error_handler(exception):
    error_data = {
        "event": "tasks",
        "detail": str(exception),
    }
    Error.insert_one(error_data)
