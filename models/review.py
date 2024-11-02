from extensions import mongo

def add_review(review_data):
    """
    Adds a new review to the 'reviews' collection.

    Args:
        review_data (dict): Data for the new review to be inserted.

    Returns:
        dict: A response indicating success and the inserted review ID, or an error message if insertion fails.
    """
    try:
        result = mongo.db.reviews.insert_one(review_data)
        return {"success": True, "inserted_id": str(result.inserted_id)}
    except Exception as e:
        return {"success": False, "error": str(e)}
