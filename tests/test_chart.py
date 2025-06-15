import json

def test_get_stock_data_success(client, mock_requests_get):
    response = client.get('/api/chart/AAPL')
    assert response.status_code == 200
    data = response.json
    assert data['symbol'] == 'AAPL'
    assert data['price'] == 150.0
    assert data['change'] == 5.0
    assert data['changePercent'] == 3.4483
    assert 'chartData' in data
    assert data['chartData'] == [149.0, 150.0]

def test_get_stock_data_api_error(client, mock_requests_get):
    response = client.get('/api/chart/error')
    assert response.status_code == 502
    assert b"External API error" in response.data

def test_get_stock_details_success(client, mock_requests_get):
    response = client.get('/api/stock-details/AAPL')
    assert response.status_code == 200
    data = response.json
    assert data['symbol'] == 'AAPL'
    assert data['longName'] == 'Apple Inc.'
    assert data['regularMarketPrice'] == 150.0
    assert data['exchange'] == 'NasdaqGS'

def test_get_historical_data_success(client, mock_requests_get):
    response = client.get('/api/historical-data/AAPL?range=1d')
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    assert len(data[0]) == 2
    first_point = data[0][0]
    assert 'timestamp' in first_point
    assert first_point['open'] == 148.0
    assert first_point['close'] == 149.0
    assert first_point['volume'] == 500000
