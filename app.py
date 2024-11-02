from bson import ObjectId
from flask import Flask, jsonify
from marshmallow import ValidationError
from extensions import mongo, jwt
from routes.companies import companies_bp
from routes.review import reviews_bp
from routes.accomplishments import accomplishments_bp
from routes.user import users_bp

app = Flask(__name__)

# Configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/famous_companies_db"  # Move to env variable in production
app.config["SECRET_KEY"] = "your_secret_key"  # Move to env variable in production
app.config["JWT_SECRET_KEY"] = "your_jwt_secret_key"  # Move to env variable in production
mongo.init_app(app)
jwt.init_app(app)

# Error Handlers
@app.errorhandler(ValidationError)
def handle_validation_error(error):
    """Handles validation errors and returns a JSON response."""
    return jsonify({"error": error.messages}), 400

@app.errorhandler(404)
def not_found(error):
    """Handles 404 errors (resource not found) and returns a JSON response."""
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handles server errors and returns a JSON response."""
    return jsonify({"error": "An internal error occurred"}), 500

# Register Blueprints for Different Routes
app.register_blueprint(companies_bp, url_prefix='/api')
app.register_blueprint(reviews_bp, url_prefix='/api')
app.register_blueprint(accomplishments_bp, url_prefix='/api')
app.register_blueprint(users_bp, url_prefix='/users')  # Consider changing to /api/users for consistency

# Data Analysis Routes
@app.route('/companies/top-rated', methods=['GET'])
def get_top_rated_companies():
    """
    Retrieves the top 5 rated companies by calculating the average rating.
    """
    pipeline = [
        {"$lookup": {
            "from": "reviews",
            "localField": "_id",
            "foreignField": "company_id",
            "as": "reviews"
        }},
        {"$unwind": "$reviews"},
        {"$group": {
            "_id": "$_id",
            "name": {"$first": "$name"},
            "averageRating": {"$avg": "$reviews.rating"}
        }},
        {"$sort": {"averageRating": -1}},
        {"$limit": 5}
    ]
    try:
        result = list(mongo.db.companies.aggregate(pipeline))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify(result)

@app.route('/companies/<company_id>/average-rating', methods=['GET'])
def get_average_rating(company_id):
    """
    Calculates and returns the average rating of a specific company.
    """
    try:
        pipeline = [
            {"$match": {"company_id": ObjectId(company_id)}},  # Match reviews for this company
            {"$group": {
                "_id": "$company_id",
                "averageRating": {"$avg": "$rating"}
            }}
        ]
        result = list(mongo.db.reviews.aggregate(pipeline))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    if result:
        return jsonify(result[0])
    return jsonify({"message": "No reviews found for this company"}), 404

@app.route('/companies/review-counts', methods=['GET'])
def get_review_counts():
    """
    Retrieves the review counts for each company, sorted by review count.
    """
    pipeline = [
        {"$lookup": {
            "from": "reviews",
            "localField": "_id",
            "foreignField": "company_id",
            "as": "reviews"
        }},
        {"$project": {
            "name": 1,
            "reviewCount": {"$size": "$reviews"}
        }},
        {"$sort": {"reviewCount": -1}}
    ]
    try:
        result = list(mongo.db.companies.aggregate(pipeline))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify(result)

@app.route('/companies/<company_id>/top-accomplishments', methods=['GET'])
def get_top_accomplishments(company_id):
    """
    Retrieves the top 5 accomplishments for a company, sorted by score or date.
    """
    pipeline = [
        {"$match": {"company_id": ObjectId(company_id)}},
        {"$sort": {"achievement_score": -1}},  # Sort by score, or by date if required
        {"$limit": 5}
    ]
    try:
        accomplishments = list(mongo.db.accomplishments.aggregate(pipeline))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify(accomplishments)

@app.route('/companies/<company_id>/rating-distribution', methods=['GET'])
def get_rating_distribution(company_id):
    """
    Provides a distribution of ratings for a specific company.
    """
    pipeline = [
        {"$match": {"company_id": ObjectId(company_id)}},
        {"$group": {
            "_id": "$rating",
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    try:
        distribution = list(mongo.db.reviews.aggregate(pipeline))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify(distribution)

@app.route('/companies/engagement', methods=['GET'])
def get_company_engagement():
    """
    Lists companies by engagement based on review and accomplishment counts.
    """
    pipeline = [
        {"$lookup": {
            "from": "reviews",
            "localField": "_id",
            "foreignField": "company_id",
            "as": "reviews"
        }},
        {"$lookup": {
            "from": "accomplishments",
            "localField": "_id",
            "foreignField": "company_id",
            "as": "accomplishments"
        }},
        {"$project": {
            "name": 1,
            "reviewCount": {"$size": "$reviews"},
            "accomplishmentCount": {"$size": "$accomplishments"}
        }},
        {"$sort": {"reviewCount": -1, "accomplishmentCount": -1}}
    ]
    try:
        engagement = list(mongo.db.companies.aggregate(pipeline))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify(engagement)

# Run the application
if __name__ == "__main__":
    app.run(debug=True)
