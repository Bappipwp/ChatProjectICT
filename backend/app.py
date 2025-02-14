from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

app = Flask(__name__)
CORS(app)

#Config secret key
app.config["JWT_SECRET_KEY"] = "supersecretkey" #Change this later
jwt = JWTManager(app)

@app.route("/")
def home():
    return{"message": "Privacy App Backend is Running"}

if __name__ == "__main__":
    app.run(debug=True)
