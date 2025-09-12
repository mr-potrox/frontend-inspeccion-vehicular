from pymongo import MongoClient
from .config import settings

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]

vehicles_col = db["vehicles"]
drivers_col = db["drivers"]
inspections_col = db["inspections"]
sessions_col = db["sessions"]  # Persistencia de sesiones