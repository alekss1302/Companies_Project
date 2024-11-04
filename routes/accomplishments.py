from flask import Blueprint, request, jsonify
from extensions import mongo
from bson import ObjectId
from flask_jwt_extended import jwt_required
from utils import role_required
from datetime import datetime

accomplishments_bp = Blueprint('accomplishments', __name__)

# Create an accomplishment (Admin only)
@accomplishments_bp.route('/companies/<company_id>/accomplishments', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_accomplishment(company_id):
    data = request.get_json()
    if not data.get("title"):
        return jsonify({"error": "Accomplishment title is required"}), 400

    accomplishment = {
        "company_id": ObjectId(company_id),
        "title": data["title"],
        "description": data.get("description"),
        "achievement_score": data.get("achievement_score", 0),
        "date": data.get("date", datetime.today().strftime("%Y-%m-%d"))
    }

    try:
        # Insert accomplishment into database
        result = mongo.db.accomplishments.insert_one(accomplishment)
        # Convert the accomplishment to JSON serializable format
        accomplishment["_id"] = str(result.inserted_id)
        accomplishment["company_id"] = str(accomplishment["company_id"])
        return jsonify({"message": "Accomplishment created successfully", "accomplishment": accomplishment}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to create accomplishment: {str(e)}"}), 500

# Retrieve all accomplishments for a company
@accomplishments_bp.route('/companies/<company_id>/accomplishments', methods=['GET'])
def get_accomplishments(company_id):
    try:
        # Ensure company_id is an ObjectId
        accomplishments = list(mongo.db.accomplishments.find({"company_id": ObjectId(company_id)}))
        # Convert ObjectIds to strings for JSON serializable format
        for accomplishment in accomplishments:
            accomplishment["_id"] = str(accomplishment["_id"])
            accomplishment["company_id"] = str(accomplishment["company_id"])
        return jsonify(accomplishments), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve accomplishments: {str(e)}"}), 500

# Update an accomplishment (Admin only)
@accomplishments_bp.route('/accomplishments/<accomplishment_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_accomplishment(accomplishment_id):
    data = request.get_json()
    updated_data = {key: data[key] for key in data if key != "_id"}

    try:
        # Update accomplishment in database
        result = mongo.db.accomplishments.update_one({"_id": ObjectId(accomplishment_id)}, {"$set": updated_data})
        if result.matched_count == 0:
            return jsonify({"error": "Accomplishment not found"}), 404
        return jsonify({"message": "Accomplishment updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update accomplishment: {str(e)}"}), 500

# Delete an accomplishment (Admin only)
@accomplishments_bp.route('/accomplishments/<accomplishment_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_accomplishment(accomplishment_id):
    try:
        # Delete accomplishment from database
        result = mongo.db.accomplishments.delete_one({"_id": ObjectId(accomplishment_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Accomplishment not found"}), 404
        return jsonify({"message": "Accomplishment deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete accomplishment: {str(e)}"}), 500
