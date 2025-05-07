import random
import requests
from flask import jsonify, abort
from app.config import Config
from app import app
from flask_caching import Cache

API_URL = Config.API_TICKERS 
cache = Cache(app,config={'CACHE_TYPE': Config.CACHE_TYPE, 'CACHE_DEFAULT_TIMEOUT': Config.CACHE_DEFAULT_TIMEOUT})

headers = {
    'User-Agent': f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{random.randint(1,1000)}.{random.randint(1,10000)}"
}

def process_chart_data(chart_response):
    try:
        result = chart_response.get('chart', {}).get('result', [])
        if not result:
            return None
        
        indicators = result[0].get('indicators', {}).get('quote', [])
        if not indicators:
             return None

        quotes = indicators[0].get('close', [])
        timestamps = result[0].get('timestamp', [])

        if not quotes or not timestamps or len(quotes) != len(timestamps):
            return None 

        processed_data = [
            close for close in quotes if close is not None
        ]
        
        return [float(p) for p in processed_data]

    except (KeyError, IndexError, TypeError, AttributeError) as e:
        print(f"Error processing chart data: {e}") 
        return None


@app.route('/api/chart/<string:ticker>', methods=['GET'])
@cache.cached(timeout=300)
def get_stock_data(ticker):
    if not ticker:
        abort(400, description="Ticker symbol is required.")

    params = {
        'interval': '5m',
        'range': '1d'
    }
    request_url = f"{API_URL}/{ticker}"

    try:
        response = requests.get(request_url, params=params, timeout=10, headers=headers)
        response.raise_for_status()

        data = response.json()

        chart_result = data.get('chart', {}).get('result', [])
        if not chart_result:
             abort(404, description=f"No data found for ticker: {ticker}")

        meta = chart_result[0].get('meta', {})
        if not meta:
             abort(500, description=f"Incomplete metadata received for ticker: {ticker}")

        previous_close = meta.get('chartPreviousClose')
        current_price = meta.get('regularMarketPrice')
        currency = meta.get('currency', 'N/A')

        if previous_close is None or current_price is None:
             abort(500, description=f"Missing price data in API response for ticker: {ticker}")
        
        try:
            previous_close = float(previous_close)
            current_price = float(current_price)
        except (ValueError, TypeError):
             abort(500, description=f"Invalid price data format received for ticker: {ticker}")

        change = current_price - previous_close
        change_percent = (change / previous_close) * 100 if previous_close else 0
        chart_data = process_chart_data(data)

        stock_data = {
            'symbol': ticker.upper(),
            'price': current_price,
            'change': round(change, 4),
            'changePercent': round(change_percent, 4),
            'currency': currency,
            'chartData': chart_data
        }

        return jsonify(stock_data), 200 

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
             abort(404, description=f"Ticker '{ticker}' not found or API endpoint error.")
        else:
             abort(502, description=f"External API error: {e}")
             
    except requests.exceptions.ConnectionError:
        abort(503, description="Could not connect to the external stock API.")
        
    except requests.exceptions.Timeout:
        abort(504, description="Request to the external stock API timed out.")

    except requests.exceptions.RequestException as e:
        print(f"General request error for ticker {ticker}: {e}")
        abort(500, description="An error occurred while fetching stock data.")

    except (KeyError, IndexError, TypeError) as e:
         print(f"Data processing error for ticker {ticker}: {e}")
         abort(500, description="Failed to process data from the external API.")
         
    except Exception as e:
        print(f"An unexpected error occurred for ticker {ticker}: {e}")
        abort(500, description="An internal server error occurred.")


def process_historical_data(chart_response):
    try:
        result = chart_response.get('chart', {}).get('result', [])
        if not result:
            return None
        
        quote_data = result[0].get('indicators', {}).get('quote', [{}])[0]
        timestamps = result[0].get('timestamp', [])
        
        opens = quote_data.get('open', [])
        highs = quote_data.get('high', [])
        lows = quote_data.get('low', [])
        closes = quote_data.get('close', [])
        volumes = quote_data.get('volume', [])
        
        historical_data = []
        for i in range(len(timestamps)):
            data_point = {
                "timestamp": timestamps[i],
                "open": float(opens[i]) if i < len(opens) and opens[i] is not None else None,
                "high": float(highs[i]) if i < len(highs) and highs[i] is not None else None,
                "low": float(lows[i]) if i < len(lows) and lows[i] is not None else None,
                "close": float(closes[i]) if i < len(closes) and closes[i] is not None else None,
                "volume": int(volumes[i]) if i < len(volumes) and volumes[i] is not None else None
            }
            historical_data.append(data_point)
        
        return historical_data
    except Exception as e:
        print(f"Error processing historical data: {e}")
        return None

@app.route('/api/stock-details/<string:ticker>', methods=['GET'])
@cache.cached(timeout=60)
def get_stock_details(ticker):
    if not ticker:
        abort(400, description="Ticker symbol is required.")

    params = {'interval': '5m', 'range': '1d'}
    request_url = f"{API_URL}/{ticker}"

    try:
        response = requests.get(request_url, params=params, timeout=10, headers=headers)
        response.raise_for_status()
        data = response.json()

        chart_result = data.get('chart', {}).get('result', [])
        if not chart_result:
            abort(404, description=f"No data found for ticker: {ticker}")

        meta = chart_result[0].get('meta', {})
        if not meta:
            abort(500, description=f"Incomplete metadata for ticker: {ticker}")

        details = {
            'symbol': meta.get('symbol'),
            'currency': meta.get('currency'),
            'longName': meta.get('longName'),
            'exchange': meta.get('exchangeName'),
            'quoteType': meta.get('instrumentType'),
            'regularMarketPrice': meta.get('regularMarketPrice'),
            'previousClose': meta.get('previousClose'),
            'fiftyTwoWeekHigh': meta.get('fiftyTwoWeekHigh'),
            'fiftyTwoWeekLow': meta.get('fiftyTwoWeekLow'),
            'dayHigh': meta.get('regularMarketDayHigh'),
            'dayLow': meta.get('regularMarketDayLow'),
            'volume': meta.get('regularMarketVolume'),
            'marketState': meta.get('exchangeTimezoneName'),
            'timezone': meta.get('timezone')
        }

        numeric_fields = ['regularMarketPrice', 'previousClose', 
                         'fiftyTwoWeekHigh', 'fiftyTwoWeekLow',
                         'dayHigh', 'dayLow', 'volume']
        
        for field in numeric_fields:
            value = details.get(field)
            if value is not None:
                try:
                    details[field] = float(value)
                except (TypeError, ValueError):
                    details[field] = None

        return jsonify(details), 200

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            abort(404, description=f"Ticker '{ticker}' not found")
        abort(502, description=f"External API error: {str(e)}")
    except Exception as e:
        print(f"Error processing stock details: {str(e)}")
        abort(500, description="Internal server error")

@app.route('/api/historical-data/<string:ticker>', methods=['GET'])
@cache.cached(timeout=60)
def get_historical_data(ticker):
    if not ticker:
        abort(400, description="Ticker symbol is required.")

    params = {'interval': '1m', 'range': '1d'}
    request_url = f"{API_URL}/{ticker}"

    try:
        response = requests.get(request_url, params=params, timeout=10, headers=headers)
        response.raise_for_status()
        data = response.json()

        historical_data = process_historical_data(data)
        if not historical_data:
            abort(404, description=f"No historical data for ticker: {ticker}")

        return jsonify(historical_data), 200

    except requests.exceptions.HTTPError as e:
        abort(502, description=f"External API error: {str(e)}")
    except Exception as e:
        print(f"Error fetching historical data: {str(e)}")
        abort(500, description="Internal server error")