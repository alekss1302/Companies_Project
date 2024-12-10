from flask import Blueprint, request, jsonify
from extensions import mongo
from bson import ObjectId
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils import role_required

reviews_bp = Blueprint('reviews', __name__)

# Create a review (User or Admin)
@reviews_bp.route('/companies/<company_id>/reviews', methods=['POST'])
@jwt_required()
def create_review(company_id):
    data = request.get_json()
    if not data.get("rating"):
        return jsonify({"error": "Rating is required"}), 400

    review = {
        "user_id": ObjectId(get_jwt_identity()),
        "company_id": ObjectId(company_id),
        "rating": data["rating"],
        "review_text": data.get("review_text", "")
    }

    try:
        # Insert review into database
        result = mongo.db.reviews.insert_one(review)
        # Convert the review to JSON serializable format
        review["_id"] = str(result.inserted_id)
        review["user_id"] = str(review["user_id"])
        review["company_id"] = str(review["company_id"])
        return jsonify({"message": "Review created successfully", "review": review}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to create review: {str(e)}"}), 500



# Retrieve all reviews for a company
@reviews_bp.route('/companies/<company_id>/reviews', methods=['GET'])
def get_reviews(company_id):
    try:
        # Ensure company_id is an ObjectId
        reviews = list(mongo.db.reviews.find({"company_id": ObjectId(company_id)}))
        # Convert ObjectIds to strings for JSON serializable format
        for review in reviews:
            review["_id"] = str(review["_id"])
            review["company_id"] = str(review["company_id"])
            review["user_id"] = str(review["user_id"])
        return jsonify(reviews), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve reviews: {str(e)}"}), 500

# Update a review (User or Admin)
@reviews_bp.route('/reviews/<review_id>', methods=['PUT'])
@jwt_required()
def update_review(review_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})
        if not review:
            return jsonify({"error": "Review not found"}), 404
        
        # Check authorization
        if review["user_id"] != user_id and not role_required("admin")(lambda: True)():
            return jsonify({"error": "Unauthorized to update this review"}), 403

        updated_data = {
            "rating": data.get("rating", review["rating"]),
            "review_text": data.get("review_text", review.get("review_text"))
        }

        # Update review in database
        mongo.db.reviews.update_one({"_id": ObjectId(review_id)}, {"$set": updated_data})
        return jsonify({"message": "Review updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update review: {str(e)}"}), 500

# Delete a review (Admin only)
@reviews_bp.route('/reviews/<review_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_review(review_id):
    try:
        # Delete review from database
        result = mongo.db.reviews.delete_one({"_id": ObjectId(review_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Review not found"}), 404
        return jsonify({"message": "Review deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete review: {str(e)}"}), 500
