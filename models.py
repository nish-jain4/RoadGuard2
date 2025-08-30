from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    phone = Column(String(20), unique=True)
    password_hash = Column(String(128))  # Hashed password
    role = Column(String(20))  # 'user', 'admin', 'worker', 'workshop_owner'
    requests = relationship('Request', backref='user', lazy=True)

class Workshop(Base):
    __tablename__ = 'workshops'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    location_lat = Column(Float)
    location_long = Column(Float)
    rating = Column(Float, default=0.0)
    status = Column(String(20), default='open')  # 'open', 'closed'
    owner_id = Column(Integer, ForeignKey('users.id'))
    workers = relationship('User', backref='workshop', lazy=True)  # Workers linked to workshop

class Request(Base):
    __tablename__ = 'requests'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    workshop_id = Column(Integer, ForeignKey('workshops.id'), nullable=True)
    worker_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    vehicle_info = Column(String(200))
    service_type = Column(String(100))
    photos = Column(String(500))  # Comma-separated URLs
    location_lat = Column(Float)
    location_long = Column(Float)
    status = Column(String(20), default='pending')  # 'pending', 'assigned', 'in_progress', 'completed'
    created_at = Column(DateTime, default=datetime.utcnow)
    eta = Column(Integer, nullable=True)  # Minutes
    comments = Column(String(500))