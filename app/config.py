import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API = os.environ.get('DATABASE_API')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')