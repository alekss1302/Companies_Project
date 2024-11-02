from flask import Blueprint, request, jsonify
from extensions import mongo
from bson import ObjectId
from flask_jwt_extended import jwt_required
from utils import role_required

companies_bp = Blueprint('companies', __name__)

# Create a new company (Admin Only)
@companies_bp.route('/companies', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_company():
    """
    Creates a new company (admin only).

    Expects 'name', 'industry', 'location', and optional 'description' in the request JSON.

    Returns:
        JSON response with the new company details or an error message.
    """
    data = request.get_json()

    if not data.get("name"):
        return jsonify({"error": "Company name is required"}), 400

    new_company = {
        "name": data["name"],
        "industry": data.get("industry"),
        "location": data.get("location"),
        "description": data.get("description")
    }

    try:
        result = mongo.db.companies.insert_one(new_company)
        new_company["_id"] = str(result.inserted_id)
        return jsonify({"message": "Company created successfully", "company": new_company}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to create company: {str(e)}"}), 500

# Get all companies (Public)
@companies_bp.route('/companies', methods=['GET'])
def get_companies():
    """
    Retrieves all companies.

    Returns:
        JSON response with a list of all companies.
    """
    try:
        companies = list(mongo.db.companies.find())
        for company in companies:
            company["_id"] = str(company["_id"])
        return jsonify(companies), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve companies: {str(e)}"}), 500

# Get a single company by ID (Public)
@companies_bp.route('/companies/<company_id>', methods=['GET'])
def get_company(company_id):
    """
    Retrieves details for a specific company by ID.

    Args:
        company_id (str): The ID of the company.

    Returns:
        JSON response with the company details or an error if not found.
    """
    try:
        company = mongo.db.companies.find_one({"_id": ObjectId(company_id)})
        if not company:
            return jsonify({"error": "Company not found"}), 404
        company["_id"] = str(company["_id"])
        return jsonify(company), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve company: {str(e)}"}), 500

# Update a company (Admin Only)
@companies_bp.route('/companies/<company_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_company(company_id):
    """
    Updates a specific company (admin only).

    Args:
        company_id (str): The ID of the company to update.

    Returns:
        JSON response indicating success or an error if the update fails.
    """
    data = request.get_json()
    updated_data = {key: data[key] for key in data if key != "_id"}

    try:
        result = mongo.db.companies.update_one({"_id": ObjectId(company_id)}, {"$set": updated_data})
        if result.matched_count == 0:
            return jsonify({"error": "Company not found"}), 404
        return jsonify({"message": "Company updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update company: {str(e)}"}), 500

# Delete a company (Admin Only)
@companies_bp.route('/companies/<company_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_company(company_id):
    """
    Deletes a specific company (admin only).

    Args:
        company_id (str): The ID of the company to delete.

    Returns:
        JSON response indicating success or an error if the deletion fails.
    """
    try:
        result = mongo.db.companies.delete_one({"_id": ObjectId(company_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Company not found"}), 404
        return jsonify({"message": "Company deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete company: {str(e)}"}), 500
