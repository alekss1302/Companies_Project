import json
from faker import Faker
import random
from datetime import datetime

# Initialize Faker
fake = Faker()

# Number of documents to generate
NUM_COMPANIES = 10
NUM_REVIEWS_PER_COMPANY = 5
NUM_ACCOMPLISHMENTS_PER_COMPANY = 3

# Create list to hold generated company data
companies = []

for _ in range(NUM_COMPANIES):
    company = {
        "name": fake.company(),
        "industry": fake.word(ext_word_list=["Healthcare", "Finance", "Technology", "Manufacturing", "Retail"]),
        "location": fake.city(),
        "founded": fake.year(),
        "ceo": fake.name(),
        "average_rating": round(random.uniform(1.0, 5.0), 1),
        "description": fake.text(max_nb_chars=100),
        "reviews": [],
        "accomplishments": []
    }

    # Generate reviews for each company
    for _ in range(NUM_REVIEWS_PER_COMPANY):
        review = {
            "user_id": str(random.randint(1, 20)),
            "review_text": fake.sentence(),
            "rating": round(random.uniform(1.0, 5.0), 1),
            "date": fake.date_between(start_date="-1y", end_date="today").isoformat()
        }
        company["reviews"].append(review)

    # Generate accomplishments for each company
    for _ in range(NUM_ACCOMPLISHMENTS_PER_COMPANY):
        accomplishment = {
            "title": fake.sentence(nb_words=4),
            "description": fake.text(max_nb_chars=80),
            "date": fake.date_between(start_date="-5y", end_date="today").isoformat()
        }
        company["accomplishments"].append(accomplishment)

    companies.append(company)

# Save to JSON file
with open("famous_companies_dataset.json", "w") as f:
    json.dump(companies, f, indent=4)

print("Dataset generated and saved to 'famous_companies_dataset.json'")
