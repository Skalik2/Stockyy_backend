import pytest
import os
import mongomock
import jwt
import datetime
import requests

os.environ['DATABASE_API'] = 'mongodb://mock_db'
os.environ['JWT_SECRET_KEY'] = 'test-secret-key'
os.environ['API_TICKERS'] = 'https://fake-api.com/v8/finance/chart'
os.environ['GEMINI_API_KEY'] = 'test-gemini-key'

from app import app as flask_app

@pytest.fixture
def app(monkeypatch):
    
    mock_mongo_client = mongomock.MongoClient()
    
    monkeypatch.setattr('app.db.client', mock_mongo_client)
    monkeypatch.setattr('app.routes.user.client', mock_mongo_client)
    monkeypatch.setattr('app.routes.stockFavorites.client', mock_mongo_client)
    monkeypatch.setattr('app.service.token.client', mock_mongo_client)
    
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": os.environ['JWT_SECRET_KEY'],
        "CACHE_TYPE": "NullCache" 
    })
    
    flask_app.mongo_client = mock_mongo_client
    
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_db_user(app):
    from werkzeug.security import generate_password_hash
    db = app.mongo_client.db
    email = 'test@example.com'
    password = 'password123'
    hashed_password = generate_password_hash(password)
    user_data = {"email": email, "password": hashed_password, "favorites": ["AAPL", "GOOG"]}
    db.users.insert_one(user_data)
    return {"email": email, "password": password}

@pytest.fixture
def auth_token(mock_db_user):
    token = jwt.encode(
        {
            "email": mock_db_user['email'],
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
        },
        os.environ['JWT_SECRET_KEY'],
        algorithm="HS256"
    )
    return f"Bearer {token}"

@pytest.fixture
def mock_requests_get(monkeypatch):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            self.text = str(json_data)

        def json(self):
            return self.json_data

        def raise_for_status(self):
            if self.status_code >= 400:
                http_error_msg = f"{self.status_code} Client Error"
                raise requests.exceptions.HTTPError(http_error_msg, response=self)

    def mock_get(*args, **kwargs):
        url = args[0]
        if 'notfound' in url:
            return MockResponse({"chart": {"result": None, "error": "Not Found"}}, 404)
        if 'error' in url:
            return MockResponse({"chart": {"result": None, "error": "Server Error"}}, 500)
        
        sample_data = {
            "chart": {
                "result": [
                    {
                        "meta": {
                            "currency": "USD",
                            "symbol": "AAPL",
                            "longName": "Apple Inc.",
                            "exchangeName": "NASDAQ",
                            "instrumentType": "EQUITY",
                            "regularMarketPrice": 150.0,
                            "chartPreviousClose": 145.0,
                            "previousClose": 145.0,
                            "fiftyTwoWeekHigh": 200.0,
                            "fiftyTwoWeekLow": 100.0,
                            "regularMarketDayHigh": 152.0,
                            "regularMarketDayLow": 148.0,
                            "regularMarketVolume": 1000000,
                            "exchangeTimezoneName": "America/New_York",
                            "timezone": "EDT",
                            "fullExchangeName": "NasdaqGS"
                        },
                        "timestamp": [1622552400, 1622552700],
                        "indicators": {
                            "quote": [
                                {
                                    "close": [149.0, 150.0],
                                    "open": [148.0, 149.0],
                                    "high": [150.0, 151.0],
                                    "low": [147.0, 148.0],
                                    "volume": [500000, 500000]
                                }
                            ]
                        }
                    }
                ],
                "error": None
            }
        }
        return MockResponse(sample_data, 200)

    monkeypatch.setattr('requests.get', mock_get)

@pytest.fixture
def mock_gemini_api(monkeypatch):
    class MockGenAIResponse:
        def __init__(self, text):
            self.text = text

    def mock_generate_content(prompt):
        if "ERROR" in prompt:
            raise Exception("Gemini API Error")
        
        response_text = """
        Zalety:
        - Silna marka i lojalna baza klientów.
        - Innowacyjne produkty i ekosystem.

        Wady:
        - Wysoka zależność od sprzedaży iPhone'a.
        - Rosnąca presja regulacyjna.

        Opinia inwestorska:
        Apple pozostaje solidną inwestycją długoterminową. Dywersyfikacja przychodów będzie kluczowa dla przyszłego wzrostu.
        """
        return MockGenAIResponse(response_text)

    monkeypatch.setattr('app.routes.AI.model.generate_content', mock_generate_content)