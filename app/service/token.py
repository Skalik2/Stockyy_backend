from functools import wraps
from flask import request, jsonify
import jwt

from app.config import Config
SECRET_KEY_JWT = Config.JWT_SECRET_KEY
from ..db import client

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            data = jwt.decode(token, SECRET_KEY_JWT, algorithms=["HS256"])
            current_user = client.db.users.find_one({"email": data['email']})
            
            if not current_user:
                return jsonify({"error": "User not found"}), 404
                
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        return f(current_user, *args, **kwargs)

    return decorated