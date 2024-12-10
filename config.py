import os

class Config:
    """
    Base configuration with common settings.
    """
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/famous_companies_db")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "alekss13022002")


class DevelopmentConfig(Config):
    """
    Development configuration with debug settings enabled.
    """
    DEBUG = True


class ProductionConfig(Config):
    """
    Production configuration with debug settings disabled for security.
    """
    DEBUG = False


class TestingConfig(Config):
    """
    Testing configuration with testing-specific settings.
    """
    TESTING = True
    MONGO_URI = os.getenv("TEST_MONGO_URI", "mongodb://localhost:27017/test_famous_companies_db")
