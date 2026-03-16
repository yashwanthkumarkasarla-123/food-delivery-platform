
from flask import Flask, jsonify

app = Flask(__name__)

restaurants = [
    {"id": 1, "name": "Pizza Hub", "rating": 4.5},
    {"id": 2, "name": "Burger Town", "rating": 4.2},
    {"id": 3, "name": "South Indian Meals", "rating": 4.8}
]

@app.route("/restaurants")
def get_restaurants():
    return jsonify(restaurants)

@app.route("/")
def home():
    return "Restaurant Service Running 🚀"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)