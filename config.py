import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///roadguard.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'jwt-secret-key'
    TWILIO_SID = 'your-twilio-sid'  # For notifications
    TWILIO_AUTH_TOKEN = 'your-twilio-token'
    TWILIO_PHONE = '+1234567890'
    STRIPE_SECRET_KEY = 'your-stripe-secret-key'