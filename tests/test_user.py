import json

def test_register_user_success(client):
    response = client.post('/api/user/register', json={
        'email': 'newuser@example.com',
        'password': 'password123'
    })
    assert response.status_code == 201
    assert response.json['message'] == 'User registered successfully'

def test_register_user_already_exists(client, mock_db_user):
    response = client.post('/api/user/register', json={
        'email': mock_db_user['email'],
        'password': 'password123'
    })
    assert response.status_code == 409
    assert response.json['error'] == 'User with this email already exists'

def test_register_user_missing_data(client):
    response = client.post('/api/user/register', json={'email': 'test@test.com'})
    assert response.status_code == 400
    assert response.json['error'] == 'Email and password are required'

def test_login_user_success(client, mock_db_user):
    response = client.post('/api/user/login', json={
        'email': mock_db_user['email'],
        'password': mock_db_user['password']
    })
    assert response.status_code == 200
    assert 'token' in response.json
    assert response.json['message'] == 'Login successful'

def test_login_user_invalid_password(client, mock_db_user):
    response = client.post('/api/user/login', json={
        'email': mock_db_user['email'],
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert response.json['error'] == 'Invalid email or password'

def test_login_user_not_found(client):
    response = client.post('/api/user/login', json={
        'email': 'nouser@example.com',
        'password': 'password123'
    })
    assert response.status_code == 401
    assert response.json['error'] == 'Invalid email or password'

def test_login_user_missing_data(client):
    response = client.post('/api/user/login', json={'email': 'test@test.com'})
    assert response.status_code == 400
    assert response.json['error'] == 'Email and password are required'