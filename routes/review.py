from flask import Blueprint, request, jsonify
from extensions import mongo
from bson import ObjectId
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils import role_required

reviews_bp = Blueprint('reviews', __name__)

# Create a review for a company (User or Admin)
@reviews_bp.route('/companies/<company_id>/reviews', methods=['POST'])
@jwt_required()
def create_review(company_id):
    """
    Creates a new review for a specific company (requires user authentication).

    Expects 'rating' and optional 'comment' in the request JSON.

    Args:
        company_id (str): The ID of the company being reviewed.

    Returns:
        JSON response with the new review details or an error message.
    """
    data = request.get_json()
    
    if not data.get("rating"):
        return jsonify({"error": "Rating is required"}), 400
    
    review = {
        "user_id": get_jwt_identity(),
        "company_id": company_id,
        "rating": data["rating"],
        "comment": data.get("comment", "")
    }

    try:
        result = mongo.db.reviews.insert_one(review)
        review["_id"] = str(result.inserted_id)
        return jsonify({"message": "Review created successfully", "review": review}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to create review: {str(e)}"}), 500

# Get all reviews for a company (Public)
@reviews_bp.route('/companies/<company_id>/reviews', methods=['GET'])
def get_reviews(company_id):
    """
    Retrieves all reviews for a specific company.

    Args:
        company_id (str): The ID of the company.

    Returns:
        JSON response with a list of reviews or an error message.
    """
    try:
        reviews = list(mongo.db.reviews.find({"company_id": company_id}))
        for review in reviews:
            review["_id"] = str(review["_id"])
        return jsonify(reviews), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve reviews: {str(e)}"}), 500

# Update a review (User who created the review or Admin)
@reviews_bp.route('/reviews/<review_id>', methods=['PUT'])
@jwt_required()
def update_review(review_id):
    """
    Updates a specific review (accessible to the review's author or an admin).

    Expects 'rating' and/or 'comment' in the request JSON.

    Args:
        review_id (str): The ID of the review to update.

    Returns:
        JSON response indicating success or an error if the update fails.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})
        if not review:
            return jsonify({"error": "Review not found"}), 404
        
        # Check if the user is the review author or has an admin role
        if review["user_id"] != user_id and not role_required("admin")(lambda: True)():
            return jsonify({"error": "Unauthorized to update this review"}), 403
        
        updated_data = {
            "rating": data.get("rating", review["rating"]),
            "comment": data.get("comment", review.get("comment"))
        }
        
        mongo.db.reviews.update_one({"_id": ObjectId(review_id)}, {"$set": updated_data})
        return jsonify({"message": "Review updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update review: {str(e)}"}), 500

# Delete a review (Admin Only)
@reviews_bp.route('/reviews/<review_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_review(review_id):
    """
    Deletes a specific review (admin only).

    Args:
        review_id (str): The ID of the review to delete.

    Returns:
        JSON response indicating success or an error if the deletion fails.
    """
    try:
        result = mongo.db.reviews.delete_one({"_id": ObjectId(review_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Review not found"}), 404
        return jsonify({"message": "Review deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete review: {str(e)}"}), 500
