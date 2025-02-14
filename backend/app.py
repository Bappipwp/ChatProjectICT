from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://chatuser:securepassword@localhost/chatdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #could remove
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

if __name__ == "__main__":
    app.run(debug=True)

#Config secret key
app.config["JWT_SECRET_KEY"] = "supersecretkey" #Change this later
jwt = JWTManager(app)

@app.route("/")
def home():
    return "Welcome to the Chat App!"
    #return{"message": "Privacy App Backend is Running"}

if __name__ == "__main__":
    app.run(debug=True)
