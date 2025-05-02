import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API = os.environ.get('DATABASE_API')

    try:
        API.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)