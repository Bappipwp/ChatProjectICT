import os
import secrets
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Generate a secure secret key 
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_urlsafe(64))  # For general Flask usage
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'supersecretkey')  # For JWT usage

# Configuration from environment variables
app.config['FLASK_APP'] = os.getenv('FLASK_APP', 'app.py')
app.config['FLASK_ENV'] = os.getenv('FLASK_ENV', 'production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#cors and db
CORS(app)
db =SQLAlchemy(app)

#user
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
    
#messages
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(100), nullable=False)
    recipient = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Message {self.sender} -> {self.recipient}: {self.content}>'
#databse
with app.app_context():
    db.create_all()
# Initialize JWT
jwt = JWTManager(app)

@app.route("/")
def home():
    return "Welcome to the Chat App!"
    #return{"message": "Privacy App Backend is Running"}

if __name__ == "__main__":
    app.run(debug=True)
