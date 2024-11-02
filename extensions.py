from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask import jsonify

mongo = PyMongo()
jwt = JWTManager()

# JWT Callbacks for Custom Error Handling
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    """
    Callback function for expired tokens.
    """
    return jsonify({"error": "Token has expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    """
    Callback function for invalid tokens.
    """
    return jsonify({"error": "Invalid token"}), 401

@jwt.unauthorized_loader
def unauthorized_callback(error):
    """
    Callback function for requests without tokens.
    """
    return jsonify({"error": "Authorization required"}), 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    """
    Callback function for revoked tokens.
    """
    return jsonify({"error": "Token has been revoked"}), 401
