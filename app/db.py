from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from app.config import Config
client = MongoClient(Config.API)