from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request

def role_required(required_roles):
    """
    Decorator to enforce role-based access control for specific roles.

    Args:
        required_roles (str or list): The required role(s) for accessing the route.
                                      Accepts a single role (str) or a list of roles.
    Returns:
        Function: The wrapped function if the user has the required role, otherwise a 403 error.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()  # Verifies that the request has a valid JWT token
            claims = get_jwt()
            
            # Check if the role matches one of the required roles
            if isinstance(required_roles, str):
                roles = [required_roles]
            else:
                roles = required_roles
            
            if claims.get("role") in roles:
                return fn(*args, **kwargs)
            else:
                return jsonify({"error": "Access denied: insufficient permissions"}), 403
        return wrapper
    return decorator
