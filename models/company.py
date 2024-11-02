from extensions import mongo

def add_company(company_data):
    """
    Adds a new company to the 'companies' collection.

    Args:
        company_data (dict): Data for the new company to be inserted.

    Returns:
        dict: A response indicating success and the inserted company ID, or an error message if insertion fails.
    """
    try:
        result = mongo.db.companies.insert_one(company_data)
        return {"success": True, "inserted_id": str(result.inserted_id)}
    except Exception as e:
        return {"success": False, "error": str(e)}
