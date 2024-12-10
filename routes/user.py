from bson import ObjectId
from flask import Blueprint, request, jsonify
from extensions import mongo
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash

users_bp = Blueprint('users', __name__)

# Register new user
@users_bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400

    try:
        hashed_password = generate_password_hash(data["password"])
        new_user = {
            "email": data["email"],
            "password": hashed_password,
            "role": data.get("role", "user")  # Default role is "user"
        }

        # Check for existing email in database
        if mongo.db.users.find_one({"email": new_user["email"]}):
            return jsonify({"error": "Email already in use"}), 409

        # Insert new user
        result = mongo.db.users.insert_one(new_user)
        return jsonify({"message": "User registered successfully", "user_id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500

# User login
@users_bp.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    
    try:
        # Find user by email
        user = mongo.db.users.find_one({"email": data["email"]})

        # Validate password
        if user and check_password_hash(user["password"], data["password"]):
            # Generate JWT access token
            access_token = create_access_token(identity=str(user["_id"]), additional_claims={"role": user.get("role")})
            return jsonify({"access_token": access_token}), 200

        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500

# Get user profile
@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        # Retrieve current user's profile excluding password
        current_user_id = get_jwt_identity()
        user = mongo.db.users.find_one({"_id": ObjectId(current_user_id)}, {"password": 0})

        if not user:
            return jsonify({"error": "User not found"}), 404

        user["_id"] = str(user["_id"])
        return jsonify(user), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve profile: {str(e)}"}), 500
