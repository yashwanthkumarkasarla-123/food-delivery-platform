from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
# Enabling CORS so your Netlify/GitHub frontend can talk to this Azure backend
CORS(app)

# 1. Mock Database for Restaurants
restaurants = [
    {"id": 1, "name": "Papadams Blue", "location": "Hanamkonda", "rating": 4.4, "tags": ["Biryani", "South Indian"]},
    {"id": 2, "name": "Kritunga Restaurant", "location": "Subedari", "rating": 5.0, "tags": ["Authentic Telugu"]},
    {"id": 3, "name": "Kalinga Dhaba", "location": "Kazipet", "rating": 4.0, "tags": ["Spicy Tandoori"]},
    {"id": 4, "name": "Sri Geetha Bhavan", "location": "Hanamkonda", "rating": 4.3, "tags": ["Veg Udupi"]}
]

# 2. Mock Database for Orders (In-memory for now)
orders = []

# --- CUSTOMER ENDPOINTS ---

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    """Returns the list of all restaurants in Warangal"""
    return jsonify(restaurants)

@app.route("/orders", methods=["POST"])
def create_order():
    """Allows customers to place a new COD order"""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    new_order = {
        "order_id": len(orders) + 1,
        "items": data.get("items", []),
        "payment": data.get("payment", "COD"),
        "user": data.get("user", "Guest"),
        "status": "PLACED" # Initial status
    }
    orders.append(new_order)
    return jsonify(new_order), 201

# --- RESTAURANT ENDPOINTS ---

@app.route("/restaurant/manage-orders", methods=["GET"])
def get_pending_orders():
    """Restaurants use this to see what orders they need to cook"""
    pending = [o for o in orders if o['status'] == 'PLACED']
    return jsonify(pending)

@app.route("/restaurant/update-status", methods=["POST"])
def update_order_status():
    """Updates order from PLACED -> ACCEPTED -> DELIVERED"""
    data = request.json
    order_id = data.get("order_id")
    new_status = data.get("status")
    
    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = new_status
            return jsonify({"message": f"Order {order_id} updated to {new_status}"})
            
    return jsonify({"error": "Order not found"}), 404

if __name__ == "__main__":
    # Standard port for Flask; Azure will map this via Docker
    app.run(host="0.0.0.0", port=5000)
