import json
from faker import Faker
import random
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

# Initialize Faker
fake = Faker()

# Number of documents to generate
NUM_COMPANIES = 10
NUM_REVIEWS_PER_COMPANY = 5
NUM_ACCOMPLISHMENTS_PER_COMPANY = 3
NUM_USERS = 20

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["famous_companies_db"]

# Clear existing data in collections
db.users.delete_many({})
db.companies.delete_many({})
db.reviews.delete_many({})
db.accomplishments.delete_many({})

# Create lists to hold generated data
companies = []
reviews = []
accomplishments = []
users = []

# Generate users
for _ in range(NUM_USERS):
    user = {
        "_id": ObjectId(),  # Directly use ObjectId for user IDs
        "name": fake.name(),
        "email": fake.email(),
        "created_at": fake.date_time_this_year().isoformat()
    }
    users.append(user)

# Generate companies, reviews, and accomplishments
for _ in range(NUM_COMPANIES):
    company_id = ObjectId()  # Directly use ObjectId for company IDs

    # Company data
    company = {
        "_id": company_id,
        "name": fake.company(),
        "industry": fake.word(ext_word_list=["Healthcare", "Finance", "Technology", "Manufacturing", "Retail"]),
        "location": fake.city(),
        "founded": fake.year(),
        "ceo": fake.name(),
        "description": fake.text(max_nb_chars=100),
    }
    companies.append(company)

    # Generate reviews for each company
    for _ in range(NUM_REVIEWS_PER_COMPANY):
        review = {
            "company_id": company_id,  # Use ObjectId directly for references
            "user_id": random.choice(users)["_id"],  # Use existing user ObjectId
            "review_text": fake.sentence(),
            "rating": round(random.uniform(1.0, 5.0), 1),
            "date": fake.date_between(start_date="-1y", end_date="today").isoformat()
        }
        reviews.append(review)

    # Generate accomplishments for each company
    for _ in range(NUM_ACCOMPLISHMENTS_PER_COMPANY):
        accomplishment = {
            "company_id": company_id,  # Use ObjectId directly for references
            "title": fake.sentence(nb_words=4),
            "description": fake.text(max_nb_chars=80),
            "date": fake.date_between(start_date="-5y", end_date="today").isoformat(),
            "achievement_score": round(random.uniform(1.0, 10.0), 1)
        }
        accomplishments.append(accomplishment)

# Insert data into MongoDB
try:
    db.users.insert_many(users)
    db.companies.insert_many(companies)
    db.reviews.insert_many(reviews)
    db.accomplishments.insert_many(accomplishments)
    print("Data successfully inserted into MongoDB.")
except Exception as e:
    print(f"An error occurred: {e}")

# Custom JSON encoder to handle ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

# Save to JSON files with ObjectId handling
with open("users.json", "w") as f:
    json.dump(users, f, indent=4, cls=JSONEncoder)
with open("companies.json", "w") as f:
    json.dump(companies, f, indent=4, cls=JSONEncoder)
with open("reviews.json", "w") as f:
    json.dump(reviews, f, indent=4, cls=JSONEncoder)
with open("accomplishments.json", "w") as f:
    json.dump(accomplishments, f, indent=4, cls=JSONEncoder)

print("Dataset also saved to JSON files.")
