from flask import Flask, jsonify, request
from flask_cors import CORS
import time

app = Flask(__name__)

# Enhanced CORS for Cloud Deployment
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# --- Real Warangal Restaurant Database ---
restaurants = [
    {
        "id": 1, "name": "Raiyaan's Hotel", "location": "Subedari", "rating": 4.5, 
        "tags": ["Biryani", "Murg Masala", "North Indian"],
        "menu": [{"item": "Special Murg Masala", "price": 560}, {"item": "Chicken Dum Biryani", "price": 150}]
    },
    {
        "id": 2, "name": "Mandi.com", "location": "Hanamkonda", "rating": 4.6, 
        "tags": ["Arabian Mandi", "Juicy Chicken"],
        "menu": [{"item": "Chicken Juicy Mandi", "price": 420}, {"item": "Mutton Mandi", "price": 650}]
    },
    {
        "id": 3, "name": "Kritunga Restaurant", "location": "Naimnagar", "rating": 4.8, 
        "tags": ["Rayalaseema", "Telugu Cuisine"],
        "menu": [{"item": "Ragi Sangati", "price": 180}, {"item": "Natukodi Pulusu", "price": 320}]
    },
    {
        "id": 4, "name": "Suprabha Hotel", "location": "Hanamkonda", "rating": 4.2, 
        "tags": ["South Indian", "Pure Veg"],
        "menu": [{"item": "Ghee Roast Dosa", "price": 80}, {"item": "South Indian Thali", "price": 150}]
    },
    {
        "id": 5, "name": "Kalinga Dhaba", "location": "Kazipet 100ft Rd", "rating": 4.0, 
        "tags": ["Spicy", "Tandoori", "Dhaba Style"],
        "menu": [{"item": "Chicken Tandoori", "price": 280}, {"item": "Butter Naan", "price": 45}]
    },
    {
        "id": 6, "name": "Papadams Blue", "location": "Hanamkonda", "rating": 4.4, 
        "tags": ["Multicuisine", "Family Dining"],
        "menu": [{"item": "Chicken 65", "price": 240}, {"item": "Veg Fried Rice", "price": 180}]
    }
]

orders = []

@app.route("/")
def health_check():
    return jsonify({"status": "Warangal Eats Backend Online", "timestamp": time.time()})

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    return jsonify(restaurants)

# --- ORDER HANDLING ---

@app.route("/orders", methods=["POST", "OPTIONS"])
def place_order():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
        
    data = request.json
    new_order = {
        "order_id": len(orders) + 1,
        "status": "PENDING_RESTAURANT",
        "items": data.get("items"),
        "total": data.get("total", 0),
        "assigned_rider": None,
        "created_at": time.time()
    }
    orders.append(new_order)
    return jsonify(new_order), 201

@app.route("/restaurant/manage-orders", methods=["GET"])
def manage_orders():
    # Only show active orders for the Admin Dashboard
    return jsonify([o for o in orders if o["status"] != "DELIVERED"])

# --- REAL-TIME UPDATES ---

@app.route("/order-status/<int:order_id>", methods=["GET"])
def get_status(order_id):
    order = next((o for o in orders if o["order_id"] == order_id), None)
    if order:
        return jsonify(order)
    return jsonify({"error": "Order not found"}), 404

@app.route("/restaurant/action", methods=["POST", "OPTIONS"])
def restaurant_action():
    if request.method == "OPTIONS": return jsonify({"status": "ok"}), 200
    data = request.json
    order = next((o for o in orders if o["order_id"] == data['order_id']), None)
    if order:
        # Status cycle: PENDING -> PREPARING
        order["status"] = "PREPARING" if data['action'] == "ACCEPT" else "REJECTED"
        return jsonify({"message": f"Order {data['action']}ED"})
    return jsonify({"error": "Order not found"}), 404

@app.route("/rider/claim", methods=["POST", "OPTIONS"])
def rider_claim():
    if request.method == "OPTIONS": return jsonify({"status": "ok"}), 200
    data = request.json
    order = next((o for o in orders if o["order_id"] == data['order_id']), None)
    if order:
        # Status cycle: PREPARING -> OUT_FOR_DELIVERY
        order["status"] = "OUT_FOR_DELIVERY"
        order["assigned_rider"] = data.get("rider_name", "Rajesh - Warangal Express")
        return jsonify({"message": "Rider Assigned!"})
    return jsonify({"error": "Order not found"}), 404

@app.route("/rider/complete", methods=["POST", "OPTIONS"])
def rider_complete():
    if request.method == "OPTIONS": return jsonify({"status": "ok"}), 200
    data = request.json
    order = next((o for o in orders if o["order_id"] == data['order_id']), None)
    if order:
        order["status"] = "DELIVERED"
        return jsonify({"message": "Order delivered successfully!"})
    return jsonify({"error": "Order not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
