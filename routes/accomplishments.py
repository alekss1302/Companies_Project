from flask import Blueprint, request, jsonify
from extensions import mongo
from bson import ObjectId
from flask_jwt_extended import jwt_required
from utils import role_required

accomplishments_bp = Blueprint('accomplishments', __name__)

# Create an accomplishment for a company (Admin Only)
@accomplishments_bp.route('/companies/<company_id>/accomplishments', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_accomplishment(company_id):
    """
    Creates a new accomplishment for a specific company (admin only).

    Expects 'title', 'description', and optional 'year' in the request JSON.

    Args:
        company_id (str): The ID of the company associated with the accomplishment.

    Returns:
        JSON response with the new accomplishment details or an error message.
    """
    data = request.get_json()

    if not data.get("title"):
        return jsonify({"error": "Accomplishment title is required"}), 400

    accomplishment = {
        "company_id": company_id,
        "title": data["title"],
        "description": data.get("description"),
        "year": data.get("year")
    }

    try:
        result = mongo.db.accomplishments.insert_one(accomplishment)
        accomplishment["_id"] = str(result.inserted_id)
        return jsonify({"message": "Accomplishment created successfully", "accomplishment": accomplishment}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to create accomplishment: {str(e)}"}), 500

# Get all accomplishments for a company (Public)
@accomplishments_bp.route('/companies/<company_id>/accomplishments', methods=['GET'])
def get_accomplishments(company_id):
    """
    Retrieves all accomplishments for a specific company.

    Args:
        company_id (str): The ID of the company.

    Returns:
        JSON response with a list of accomplishments or an error message.
    """
    try:
        accomplishments = list(mongo.db.accomplishments.find({"company_id": company_id}))
        for accomplishment in accomplishments:
            accomplishment["_id"] = str(accomplishment["_id"])
        return jsonify(accomplishments), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve accomplishments: {str(e)}"}), 500

# Update an accomplishment (Admin Only)
@accomplishments_bp.route('/accomplishments/<accomplishment_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_accomplishment(accomplishment_id):
    """
    Updates a specific accomplishment (admin only).

    Expects 'title', 'description', and/or 'year' in the request JSON.

    Args:
        accomplishment_id (str): The ID of the accomplishment to update.

    Returns:
        JSON response indicating success or an error if the update fails.
    """
    data = request.get_json()
    updated_data = {key: data[key] for key in data if key != "_id"}

    try:
        result = mongo.db.accomplishments.update_one({"_id": ObjectId(accomplishment_id)}, {"$set": updated_data})
        if result.matched_count == 0:
            return jsonify({"error": "Accomplishment not found"}), 404
        return jsonify({"message": "Accomplishment updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update accomplishment: {str(e)}"}), 500

# Delete an accomplishment (Admin Only)
@accomplishments_bp.route('/accomplishments/<accomplishment_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_accomplishment(accomplishment_id):
    """
    Deletes a specific accomplishment (admin only).

    Args:
        accomplishment_id (str): The ID of the accomplishment to delete.

    Returns:
        JSON response indicating success or an error if the deletion fails.
    """
    try:
        result = mongo.db.accomplishments.delete_one({"_id": ObjectId(accomplishment_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Accomplishment not found"}), 404
        return jsonify({"message": "Accomplishment deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete accomplishment: {str(e)}"}), 500
