def test_analiza_spolki_success(client, mock_gemini_api):
    response = client.get('/api/analiza_spolki?nazwa_spolki=Apple')
    assert response.status_code == 200
    data = response.json
    assert data['spolka'] == 'Apple'
    assert 'zalety' in data
    assert 'wady' in data
    assert 'opinia_inwestorska' in data
    assert isinstance(data['zalety'], list)
    assert '- Silna marka i lojalna baza klientów.' in data['zalety']
    assert 'Apple pozostaje solidną inwestycją długoterminową.' in data['opinia_inwestorska']

def test_analiza_spolki_missing_param(client):
    response = client.get('/api/analiza_spolki')
    assert response.status_code == 400
    assert response.json['blad'] == "Nie podano parametru 'nazwa_spolki'"

def test_analiza_spolki_api_error(client, mock_gemini_api):
    response = client.get('/api/analiza_spolki?nazwa_spolki=ERROR')
    assert response.status_code == 500
    assert 'Błąd API Gemini' in response.json['error']

def test_analiza_spolki_model_not_configured(client, monkeypatch):
    monkeypatch.setattr('app.routes.AI.model', None)
    response = client.get('/api/analiza_spolki?nazwa_spolki=Apple')
    assert response.status_code == 500
    assert 'Model Gemini nie jest poprawnie skonfigurowany' in response.json['blad']