from app import app
from app.service.token import token_required
from ..db import client
from flask import request, jsonify

from app.config import Config

SECRET_KEY_JWT = Config.JWT_SECRET_KEY

@app.route('/api/favorites', methods=['POST'])
@token_required
def add_favorite(current_user):
    data = request.get_json()
    
    if not data or 'ticker' not in data:
        return jsonify({"error": "Ticker is required"}), 400
        
    ticker = data['ticker'].upper().strip()
    
    if len(ticker) < 2:
        return jsonify({"error": "Invalid ticker format"}), 400

    try:
        result = client.db.users.update_one(
            {"email": current_user['email']},
            {"$addToSet": {"favorites": ticker}}
        )

        if result.modified_count == 1:
            return jsonify({"message": "Ticker added to favorites"}), 200
        else:
            return jsonify({"message": "Ticker already in favorites"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/favorites', methods=['GET'])
@token_required
def get_favorites(current_user):
    try:
        user = client.db.users.find_one(
            {"email": current_user['email']},
            {"favorites": 1, "_id": 0}
        )
        return jsonify(user.get('favorites', [])), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/favorites/<string:ticker>', methods=['DELETE'])
@token_required
def remove_favorite(current_user, ticker):
    try:
        ticker = ticker.upper().strip()
        if len(ticker) < 2:
            return jsonify({"error": "Invalid ticker format"}), 400

        result = client.db.users.update_one(
            {"email": current_user['email']},
            {"$pull": {"favorites": ticker}}
        )

        if result.modified_count == 1:
            return jsonify({"message": "Ticker removed successfully"}), 200
        elif result.matched_count == 1:
            return jsonify({"message": "Ticker not found in favorites"}), 404
        else:
            return jsonify({"error": "User not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500