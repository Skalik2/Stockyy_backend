def test_server_running(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.data == b"Server is running!"

def test_app_config(app):
    assert app.config['TESTING'] is True
    assert app.config['CACHE_TYPE'] == 'NullCache'