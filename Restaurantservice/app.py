from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time

app = Flask(__name__)
CORS(app)

# Security: Rate Limiter (Relaxed for development testing)
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

# 2. IN-MEMORY STORE: Orders
orders = []

# --- CUSTOMER ENDPOINTS ---

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
        "created_at": time.time(), # Order start timestamp
        "assigned_rider": None
    }
    orders.append(new_order)
    return jsonify(new_order), 201

# --- RESTAURANT OWNER ENDPOINTS ---

@app.route("/restaurant/manage-orders", methods=["GET"])
def manage_orders():
    """Admin page calls this to see alerts."""
    # We clean up or flag expired orders here
    current_time = time.time()
    for o in orders:
        if o['status'] == 'PENDING_RESTAURANT' and (current_time - o['created_at']) > 300:
            o['status'] = 'AUTO_REJECTED'
            
    # Return only active pending orders
    pending = [o for o in orders if o['status'] == 'PENDING_RESTAURANT']
    return jsonify(pending)

@app.route("/restaurant/action", methods=["POST"])
def restaurant_action():
    """Restaurant accepts or rejects."""
    data = request.json
    order_id = data.get("order_id")
    action = data.get("action") # 'ACCEPT' or 'REJECT'
    
    for order in orders:
        if order["order_id"] == order_id:
            # Check if 5 minutes expired
            if time.time() - order["created_at"] > 300:
                order["status"] = "AUTO_REJECTED"
                return jsonify({"error": "Time expired (5 min). Order cancelled."}), 400
            
            if action == "ACCEPT":
                order["status"] = "PREPARING"
                return jsonify({"message": "Order accepted! Kitchen notified."})
            else:
                order["status"] = "REJECTED_BY_RES"
                return jsonify({"message": "Order rejected by restaurant."})
                
    return jsonify({"error": "Order not found"}), 404

if __name__ == "__main__":
    # Ensure it listens on 0.0.0.0 for Azure Container App compatibility
    app.run(host="0.0.0.0", port=5000)
