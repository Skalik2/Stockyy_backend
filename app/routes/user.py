from app import app
from ..db import client
from flask import request, jsonify
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

@app.route('/api/user/register', methods=['POST'])
def register_user():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password are required"}), 400

    email = data['email']
    password = data['password']
    hashed_password = generate_password_hash(password)

    try:
        if client.db.users.find_one({"email": email}):
            return jsonify({"error": "User with this email already exists"}), 409

        client.db.users.insert_one({"email": email, "password": hashed_password})
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/user/login', methods=['POST'])
def login_user():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password are required"}), 400

    email = data['email']
    password = data['password']

    try:
        user = client.db.users.find_one({"email": email})
        if user and check_password_hash(user['password'], password):
            return jsonify({"message": "Login successful"}), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500