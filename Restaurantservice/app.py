from flask import Flask, jsonify
from flask_cors import CORS # 1. Import CORS

app = Flask(__name__)
CORS(app) # 2. Enable CORS for all routes



restaurants = [
    {"id": 1, "name": "Papadams Blue", "location": "Hanamkonda", "rating": 4.4, "tags": ["Biryani", "South Indian"]},
    {"id": 2, "name": "Kritunga Restaurant", "location": "Subedari", "rating": 5.0, "tags": ["Authentic Telugu"]},
    {"id": 3, "name": "Kalinga Dhaba", "location": "Kazipet", "rating": 4.0, "tags": ["Spicy", "Tandoori"]},
    {"id": 4, "name": "Sri Geetha Bhavan", "location": "Hanamkonda", "rating": 4.3, "tags": ["Veg", "Udupi"]},
]

@app.route("/restaurants")
def get_restaurants():
    return jsonify(restaurants)

@app.route("/")
def home():
    return "Restaurant Service Running 🚀"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
