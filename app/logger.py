import logging
from logging.handlers import BaseRotatingHandler
from io import BytesIO
from app.database import DebugLog

class MongoDBHandler(BaseRotatingHandler):
    def __init__(self, collection, level=logging.NOTSET):
        super().__init__('spot.log', 'a')
        self.collection = collection

    def emit(self, record):
        try:
            log_entry = {
                "level": record.levelname,
                "message": self.format(record),
                "timestamp": record.created,
            }
            self.collection.insert_one(log_entry)
        except Exception:
            self.handleError(record)

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(name='spot Logger')

logger.setLevel(logging.DEBUG)

# log file handler
log_file = 'spot.request.log'
handler = logging.FileHandler(log_file)
log_file_root = 'spot.root.log'
handler_root = logging.FileHandler(log_file_root)
# Db handler
mongo_handler = MongoDBHandler(collection=DebugLog, level=logging.INFO)

# log formatter (customize as needed)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Configure the root logger with the handler
logging.basicConfig(level=logging.DEBUG, handlers=[handler_root])
# handler for the logger
logger.addHandler(handler) 
# Add the MongoDB handler
logger.addHandler(mongo_handler) 