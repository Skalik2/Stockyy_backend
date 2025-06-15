def test_add_favorite_success(client, auth_token):
    response = client.post('/api/favorites', json={'ticker': 'TSLA'}, headers={'Authorization': auth_token})
    assert response.status_code == 200
    assert response.json['message'] == 'Ticker added to favorites'

def test_add_favorite_already_exists(client, auth_token):
    response = client.post('/api/favorites', json={'ticker': 'AAPL'}, headers={'Authorization': auth_token})
    assert response.status_code == 200
    assert response.json['message'] == 'Ticker already in favorites'

def test_add_favorite_invalid_ticker(client, auth_token):
    response = client.post('/api/favorites', json={'ticker': 'A'}, headers={'Authorization': auth_token})
    assert response.status_code == 400
    assert response.json['error'] == 'Invalid ticker format'

def test_add_favorite_no_token(client):
    response = client.post('/api/favorites', json={'ticker': 'TSLA'})
    assert response.status_code == 401
    assert response.json['error'] == 'Token is missing'

def test_get_favorites_success(client, auth_token, mock_db_user):
    response = client.get('/api/favorites', headers={'Authorization': auth_token})
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert 'AAPL' in response.json
    assert 'GOOG' in response.json

def test_get_favorites_no_token(client):
    response = client.get('/api/favorites')
    assert response.status_code == 401
    assert response.json['error'] == 'Token is missing'

def test_remove_favorite_success(client, auth_token):
    response = client.delete('/api/favorites/AAPL', headers={'Authorization': auth_token})
    assert response.status_code == 200
    assert response.json['message'] == 'Ticker removed successfully'

    get_response = client.get('/api/favorites', headers={'Authorization': auth_token})
    assert 'AAPL' not in get_response.json

def test_remove_favorite_not_found(client, auth_token):
    response = client.delete('/api/favorites/NONEXISTENT', headers={'Authorization': auth_token})
    assert response.status_code == 404
    assert response.json['message'] == 'Ticker not found in favorites'

def test_remove_favorite_no_token(client):
    response = client.delete('/api/favorites/AAPL')
    assert response.status_code == 401
    assert response.json['error'] == 'Token is missing'