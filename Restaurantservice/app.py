from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time

app = Flask(__name__)
CORS(app)

# Security: Rate Limiter (Relaxed for development)
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["2000 per day", "500 per hour"],
    storage_uri="memory://"
)

# 1. DATABASE: Restaurants with Full Menus
restaurants = [
    {
        "id": 1, 
        "name": "Papadams Blue", 
        "location": "Hanamkonda", "rating": 4.4,
        "tags": ["Biryani", "South Indian"],
        "menu": [
            {"id": "pb1", "item": "Chicken Biryani", "price": 280},
            {"id": "pb2", "item": "Paneer Butter Masala", "price": 220},
            {"id": "pb3", "item": "Butter Naan", "price": 40}
        ]
    },
    {
        "id": 2, 
        "name": "Kritunga Restaurant", 
        "location": "Subedari", "rating": 5.0,
        "tags": ["Authentic Telugu"],
        "menu": [
            {"id": "kr1", "item": "Ragi Sangati", "price": 180},
            {"id": "kr2", "item": "Natu Kodi Pulusu", "price": 350},
            {"id": "kr3", "item": "Gongura Mutton", "price": 380}
        ]
    },
    {
        "id": 3, 
        "name": "Kalinga Dhaba", 
        "location": "Kazipet", "rating": 4.0,
        "tags": ["Spicy Tandoori"],
        "menu": [
            {"id": "kd1", "item": "Tandoori Chicken", "price": 320},
            {"id": "kd2", "item": "Mixed Veg Curry", "price": 190},
            {"id": "kd3", "item": "Jeera Rice", "price": 150}
        ]
    },
    {
        "id": 4, 
        "name": "Sri Geetha Bhavan", 
        "location": "Hanamkonda", "rating": 4.3,
        "tags": ["Veg Udupi"],
        "menu": [
            {"id": "sg1", "item": "Masala Dosa", "price": 80},
            {"id": "sg2", "item": "Filter Coffee", "price": 30},
            {"id": "sg3", "item": "Idli Sambar", "price": 60}
        ]
    }
]

# 2. DATABASE: Orders & Riders
orders = []
riders = [
    {"id": "rider1", "name": "Rajesh", "status": "IDLE", "location": "Hanamkonda"},
    {"id": "rider2", "name": "Suresh", "status": "IDLE", "location": "Kazipet"}
]

# --- ENDPOINTS ---

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    return jsonify(restaurants)

@app.route("/orders", methods=["POST"])
def place_order():
    """Customer places an order. Starts the 5-min Restaurant Timer."""
    data = request.json
    new_order = {
        "order_id": len(orders) + 1,
        "res_id": data.get("res_id"),
        "items": data.get("items", []),
        "total": sum(item['price'] for item in data.get("items", [])),
        "status": "PENDING_RESTAURANT",
        "created_at": time.time(), # Order start time
        "assigned_rider": None,
        "rider_alert_time": None
    }
    orders.append(new_order)
    return jsonify(new_order), 201

@app.route("/restaurant/action", methods=["POST"])
def restaurant_action():
    """Restaurant accepts or rejects. Logic: Must be within 5 mins."""
    data = request.json
    order_id = data.get("order_id")
    action = data.get("action") # 'ACCEPT' or 'REJECT'
    
    for order in orders:
        if order["order_id"] == order_id:
            # Check if 5 minutes (300 seconds) have passed
            if time.time() - order["created_at"] > 300:
                order["status"] = "AUTO_REJECTED"
                return jsonify({"error": "Time expired (5 min). Order cancelled."}), 400
            
            if action == "ACCEPT":
                order["status"] = "PREPARING"
                order["rider_alert_time"] = time.time() # Start 1-min Rider Timer
                return jsonify({"message": "Order accepted! Finding rider..."})
            else:
                order["status"] = "REJECTED_BY_RES"
                return jsonify({"message": "Order rejected by restaurant."})
                
    return jsonify({"error": "Order not found"}), 404

@app.route("/rider/status", methods=["GET"])
def get_rider_alerts():
    """Riders check this to see if they have 1 min to accept an order."""
    current_time = time.time()
    for order in orders:
        if order["status"] == "PREPARING" and not order["assigned_rider"]:
            # If 1 min (60s) passed, we would normally reassign.
            return jsonify({"order_id": order["order_id"], "time_left": 60 - (current_time - order["rider_alert_time"])})
    return jsonify({"message": "No pending pickups"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
