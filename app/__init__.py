from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300

from app.routes import chart, stockFavorites, user, test, AI