from flask import Flask, jsonify, request
from flask_cors import CORS
import time

app = Flask(__name__)

# Allow all origins to talk to the API - Critical for GitHub Pages to Azure communication
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# --- The Warangal Multi-Tenant Database ---
restaurants = [
    {
        "id": 1, "name": "Raiyaan's Hotel", "location": "Subedari", "rating": 4.5, 
        "tags": ["Biryani", "North Indian"],
        "menu": [{"item": "Chicken Dum Biryani", "price": 150}, {"item": "Special Murg Masala", "price": 560}]
    },
    {
        "id": 2, "name": "Mandi.com", "location": "Hanamkonda", "rating": 4.6, 
        "tags": ["Arabian Mandi"],
        "menu": [{"item": "Chicken Juicy Mandi", "price": 420}, {"item": "Mutton Mandi", "price": 650}]
    },
    {
        "id": 3, "name": "Kritunga Restaurant", "location": "Naimnagar", "rating": 4.8, 
        "tags": ["Rayalaseema", "Telugu"],
        "menu": [{"item": "Ragi Sangati", "price": 180}, {"item": "Natukodi Pulusu", "price": 320}]
    },
    {
        "id": 4, "name": "Suprabha Hotel", "location": "Hanamkonda", "rating": 4.2, 
        "tags": ["South Indian", "Veg"],
        "menu": [{"item": "Ghee Roast Dosa", "price": 80}, {"item": "Thali", "price": 150}]
    }
]

orders = []

@app.route("/")
def health():
    return jsonify({"status": "Warangal Eats Backend Online", "time": time.time()})

# --- CUSTOMER ENDPOINTS ---

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    return jsonify(restaurants)

@app.route("/orders", methods=["POST", "OPTIONS"])
def place_order():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
        
    data = request.json
    new_order = {
        "order_id": len(orders) + 1,
        "res_id": data.get("res_id"),  # Linked to the specific restaurant
        "status": "PENDING_RESTAURANT",
        "items": data.get("items"),
        "total": data.get("total", 0),
        "created_at": time.time(),
        "assigned_rider": None
    }
    orders.append(new_order)
    return jsonify(new_order), 201

@app.route("/order-status/<int:order_id>", methods=["GET"])
def get_status(order_id):
    order = next((o for o in orders if o["order_id"] == order_id), None)
    if order:
        return jsonify(order)
    return jsonify({"error": "Order not found"}), 404

# --- PARTNER (RESTAURANT OWNER) ENDPOINTS ---

@app.route("/restaurant/manage-orders/<int:res_id>", methods=["GET"])
def manage_orders(res_id):
    """
