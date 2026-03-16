from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
CORS(app)

# 1. SECURITY: Rate Limiter
# This ensures that if traffic spikes, one person can't overwhelm the server.
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# 2. DATA STORAGE (In-memory for now)
restaurants = [
    {"id": 1, "name": "Papadams Blue", "location": "Hanamkonda", "rating": 4.4, "tags": ["Biryani", "South Indian"]},
    {"id": 2, "name": "Kritunga Restaurant", "location": "Subedari", "rating": 5.0, "tags": ["Authentic Telugu"]},
    {"id": 3, "name": "Kalinga Dhaba", "location": "Kazipet", "rating": 4.0, "tags": ["Spicy Tandoori"]},
    {"id": 4, "name": "Sri Geetha Bhavan", "location": "Hanamkonda", "rating": 4.3, "tags": ["Veg Udupi"]}
]
orders = []

# --- CUSTOMER ENDPOINTS ---

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    return jsonify(restaurants)

@app.route("/orders", methods=["POST"])
@limiter.limit("5 per minute") # Extra security to prevent fake order spam
def create_order():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    # DATA PRIVACY: We hash the user ID so their actual info isn't stored in the order list
    new_order = {
        "order_id": len(orders) + 1,
        "items": data.get("items", []),
        "payment": data.get("payment", "COD"),
        "user_hidden_id": hash(data.get("user", "Guest")), 
        "status": "PLACED"
    }
    orders.append(new_order)
    return jsonify({"message": "Order Securely Placed", "order_id": new_order["order_id"]}), 201

# --- RESTAURANT ONBOARDING ---

@app.route("/register-restaurant", methods=["POST"])
@limiter.limit("2 per hour") # Prevent bot-created fake restaurants
def register_restaurant():
    data = request.json
    if not data or not data.get("name"):
        return jsonify({"error": "Name is required"}), 400
        
    new_res = {
        "id": len(restaurants) + 1,
        "name": data.get("name"),
        "location": data.get("location", "Warangal"),
        "rating": 0.0,
        "tags": data.get("tags", ["General"])
    }
    restaurants.append(new_res)
    return jsonify({"message": "Welcome to Warangal Eats!", "restaurant": new_res}), 201

# --- RESTAURANT MANAGEMENT ---

@app.route("/restaurant/manage-orders", methods=["GET"])
def get_pending_orders():
    # Only returns orders that haven't been delivered yet
    pending = [o for o in orders if o['status'] != 'DELIVERED']
    return jsonify(pending)

@app.route("/restaurant/update-status", methods=["POST"])
def update_order_status():
    data = request.json
    order_id = data.get("order_id")
    new_status = data.get("status") # e.g., "ACCEPTED" or "DELIVERED"
    
    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = new_status
            return jsonify({"message": f"Order {order_id} is now {new_status}"})
            
    return jsonify({"error": "Order not found"}), 404

if __name__ == "__main__":
    # 0.0.0.0 is required for Azure Container Apps to route traffic correctly
    app.run(host="0.0.0.0", port=5000)
