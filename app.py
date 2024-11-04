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
app.config["MONGO_URI"] = "mongodb://localhost:27017/famous_companies_db"
app.config["SECRET_KEY"] = "your_secret_key"
app.config["JWT_SECRET_KEY"] = "your_jwt_secret_key"
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
app.register_blueprint(users_bp, url_prefix='/api/users')

# Data Analysis Routes
# Retrieves the top 5 rated companies by calculating the average rating.
@app.route('/companies/top-rated', methods=['GET'])
def get_top_rated_companies():
    pipeline = [
        {
            "$lookup": {
                "from": "reviews",
                "localField": "_id",
                "foreignField": "company_id",
                "as": "reviews"
            }
        },
        {
            "$addFields": {
                "averageRating": {"$avg": "$reviews.rating"}
            }
        },
        {
            "$sort": {"averageRating": -1}
        },
        {
            "$limit": 5
        },
        {
            "$project": {
                "name": 1,
                "averageRating": 1
            }
        }
    ]
    try:
        result = list(mongo.db.companies.aggregate(pipeline))
        
        # Convert ObjectIds to strings for JSON response
        for company in result:
            company["_id"] = str(company["_id"])
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    return jsonify(result)


# Calculates and returns the average rating of a specific company.
@app.route('/companies/<company_id>/average-rating', methods=['GET'])
def get_average_rating(company_id):
    try:
        pipeline = [
            {"$match": {"company_id": ObjectId(company_id)}},  # Match reviews for this company
            {"$group": {
                "_id": "$company_id",
                "averageRating": {"$avg": "$rating"}
            }}
        ]
        result = list(mongo.db.reviews.aggregate(pipeline))
        
        if result:
            # Convert ObjectId to string
            result[0]["_id"] = str(result[0]["_id"])
            result[0]["averageRating"] = round(result[0]["averageRating"], 2)  # Round for readability
            return jsonify(result[0])
        else:
            return jsonify({"message": "No reviews found for this company"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Retrieves the review counts for each company, sorted by review count.
@app.route('/companies/review-counts', methods=['GET'])
def get_review_counts():
    pipeline = [
        {
            "$lookup": {
                "from": "reviews",
                "localField": "_id",
                "foreignField": "company_id",
                "as": "reviews"
            }
        },
        {
            "$project": {
                "name": 1,
                "reviewCount": {"$size": "$reviews"}
            }
        },
        {
            "$sort": {"reviewCount": -1}
        }
    ]

    try:
        result = list(mongo.db.companies.aggregate(pipeline))
        
        # Convert ObjectId to string for each company in the result
        for company in result:
            company["_id"] = str(company["_id"])
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(result)


# Provides a distribution of ratings for a specific company.
@app.route('/companies/<company_id>/rating-distribution', methods=['GET'])
def get_rating_distribution(company_id):
    try:
        pipeline = [
            {
                "$addFields": {
                    "company_id": {"$convert": {"input": "$company_id", "to": "objectId", "onError": None}}
                }
            },
            {"$match": {"company_id": ObjectId(company_id)}},
            {"$group": {
                "_id": "$rating",
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        
        distribution = list(mongo.db.reviews.aggregate(pipeline))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    return jsonify(distribution)

# Lists companies by engagement based on review and accomplishment counts.
@app.route('/companies/engagement', methods=['GET'])
def get_company_engagement():
    pipeline = [
        {
            "$lookup": {
                "from": "reviews",
                "let": {"companyId": "$_id"},
                "pipeline": [
                    {
                        "$addFields": {
                            "company_id": {"$convert": {"input": "$company_id", "to": "objectId", "onError": None}}
                        }
                    },
                    {"$match": {"$expr": {"$eq": ["$company_id", "$$companyId"]}}}
                ],
                "as": "reviews"
            }
        },
        {
            "$lookup": {
                "from": "accomplishments",
                "let": {"companyId": "$_id"},
                "pipeline": [
                    {
                        "$addFields": {
                            "company_id": {"$convert": {"input": "$company_id", "to": "objectId", "onError": None}}
                        }
                    },
                    {"$match": {"$expr": {"$eq": ["$company_id", "$$companyId"]}}}
                ],
                "as": "accomplishments"
            }
        },
        {
            "$project": {
                "name": 1,
                "reviewCount": {"$size": "$reviews"},
                "accomplishmentCount": {"$size": "$accomplishments"}
            }
        },
        {"$sort": {"reviewCount": -1, "accomplishmentCount": -1}}
    ]

    try:
        engagement = list(mongo.db.companies.aggregate(pipeline))
        
        # Convert ObjectId to string for each document in the engagement list
        for company in engagement:
            company["_id"] = str(company["_id"])
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(engagement)

# Retrieves the top 5 accomplishments for a specific company based on achievement score.
@app.route('/companies/<company_id>/top-accomplishments', methods=['GET'])
def get_top_accomplishments(company_id):
    try:
        pipeline = [
            {"$match": {"company_id": ObjectId(company_id)}},  # Convert to ObjectId for matching
            {"$sort": {"achievement_score": -1}},  # Sort by achievement score
            {"$limit": 5}
        ]
        accomplishments = list(mongo.db.accomplishments.aggregate(pipeline))
        
        # Convert ObjectIds to strings if needed
        for accomplishment in accomplishments:
            accomplishment["_id"] = str(accomplishment["_id"])
            accomplishment["company_id"] = str(accomplishment["company_id"])
        
        return jsonify(accomplishments)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the application
if __name__ == "__main__":
    app.run(debug=True)
