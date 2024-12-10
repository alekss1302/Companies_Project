from flask import Blueprint, request, jsonify
from extensions import mongo
from bson import ObjectId
from flask_jwt_extended import jwt_required
from utils import role_required

companies_bp = Blueprint('companies', __name__)

# Create a new company (Admin only)
@companies_bp.route('/companies', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_company():
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
        # Insert new company into database
        result = mongo.db.companies.insert_one(new_company)
        new_company["_id"] = str(result.inserted_id)
        return jsonify({"message": "Company created successfully", "company": new_company}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to create company: {str(e)}"}), 500

# Retrieve all companies
@companies_bp.route('/companies', methods=['GET'])
def get_companies():
    try:
        companies = list(mongo.db.companies.find())
        for company in companies:
            company["_id"] = str(company["_id"])
        return jsonify(companies), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve companies: {str(e)}"}), 500

# Retrieve a company by ID
@companies_bp.route('/companies/<company_id>', methods=['GET'])
def get_company(company_id):
    try:
        company = mongo.db.companies.find_one({"_id": ObjectId(company_id)})
        if not company:
            return jsonify({"error": "Company not found"}), 404
        company["_id"] = str(company["_id"])
        return jsonify(company), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve company: {str(e)}"}), 500

# Update a company (Admin only)
@companies_bp.route('/companies/<company_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_company(company_id):
    data = request.get_json()
    updated_data = {key: data[key] for key in data if key != "_id"}

    try:
        # Update company details in database
        result = mongo.db.companies.update_one({"_id": ObjectId(company_id)}, {"$set": updated_data})
        if result.matched_count == 0:
            return jsonify({"error": "Company not found"}), 404
        return jsonify({"message": "Company updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update company: {str(e)}"}), 500

# Delete a company (Admin only)
@companies_bp.route('/companies/<company_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_company(company_id):
    try:
        # Delete company from database
        result = mongo.db.companies.delete_one({"_id": ObjectId(company_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Company not found"}), 404
        return jsonify({"message": "Company deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete company: {str(e)}"}), 500
