import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    print("Loading configuration...",os.environ.get('SECRET_KEY'))
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'roadguard-secret-key-2023'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'roadguard.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False