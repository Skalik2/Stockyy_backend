import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API = os.environ.get('DATABASE_API')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    API_TICKERS = os.environ.get('API_TICKERS')
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300
