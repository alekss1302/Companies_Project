from extensions import mongo

def add_accomplishment(accomplishment_data):
    """
    Adds a new accomplishment to the 'accomplishments' collection.

    Args:
        accomplishment_data (dict): Data for the new accomplishment to be inserted.

    Returns:
        dict: A response indicating success and the inserted accomplishment ID, or an error message if insertion fails.
    """
    try:
        result = mongo.db.accomplishments.insert_one(accomplishment_data)
        return {"success": True, "inserted_id": str(result.inserted_id)}
    except Exception as e:
        return {"success": False, "error": str(e)}
