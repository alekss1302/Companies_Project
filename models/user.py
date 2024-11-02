from extensions import mongo
from werkzeug.security import generate_password_hash

def add_user(user_data):
    """
    Adds a new user to the 'users' collection with hashed password.

    Args:
        user_data (dict): Data for the new user, including 'email' and 'password'.

    Returns:
        dict: A response indicating success and the inserted user ID, or an error message if insertion fails.
    """
    try:
        user_data['password'] = generate_password_hash(user_data['password'])  # Hash the password before storing
        result = mongo.db.users.insert_one(user_data)
        return {"success": True, "inserted_id": str(result.inserted_id)}
    except Exception as e:
        return {"success": False, "error": str(e)}
