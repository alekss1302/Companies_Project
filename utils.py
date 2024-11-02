from bson import ObjectId
from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask import jsonify
from extensions import mongo

def format_object_id(document):
    """
    Recursively formats ObjectId fields in a document, converting all `_id` fields to strings.

    Args:
        document (dict or list): The MongoDB document(s) containing ObjectId fields.

    Returns:
        dict or list: Document(s) with ObjectId fields converted to strings.
    """
    if isinstance(document, dict):
        return {k: (str(v) if isinstance(v, ObjectId) else format_object_id(v)) for k, v in document.items()}
    elif isinstance(document, list):
        return [format_object_id(item) for item in document]
    return document

def role_required(required_role):
    """
    Decorator to enforce role-based access control with real-time validation from the database.

    Args:
        required_role (str): The role required to access the route.

    Returns:
        Function: The wrapped function if the user has the required role, otherwise a 403 error.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()  # Ensures the request has a valid JWT token
            current_user_id = get_jwt_identity()  # Retrieves the current user's ID from the JWT
            try:
                # Fetches the user from the database by ID
                user = mongo.db.users.find_one({"_id": ObjectId(current_user_id)})
                
                # Checks if the user's role matches the required role
                if user and user.get("role") == required_role:
                    return fn(*args, **kwargs)
                return jsonify({"error": "Access denied: insufficient permissions"}), 403
            except Exception as e:
                return jsonify({"error": f"Authorization error: {str(e)}"}), 500
        return decorator
    return wrapper
