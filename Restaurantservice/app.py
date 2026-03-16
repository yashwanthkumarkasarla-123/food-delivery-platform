from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
# Crucial for your Netlify frontend to communicate with this Azure backend
CORS(app)

# 1. Database for Restaurants (In-memory)
restaurants = [
    {"id": 1, "name": "Papadams Blue", "location": "Hanamkonda", "rating": 4.4, "tags": ["Biryani", "South Indian"]},
    {"id": 2, "name": "Kritunga Restaurant", "location": "Subedari", "rating": 5.0, "tags": ["Authentic Telugu"]},
    {"id": 3, "name": "Kalinga Dhaba", "location": "Kazipet", "rating": 4.0, "tags": ["Spicy Tandoori"]},
    {"id": 4, "name": "Sri Geetha Bhavan", "location": "Hanamkonda", "rating": 4.3, "tags": ["Veg Udupi"]}
]

# 2. Database for Orders
orders = []

# --- CUSTOMER ENDPOINTS ---

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    """Returns all restaurants including newly registered ones"""
    return jsonify(restaurants)

@app.route("/orders", methods=["POST"])
def create_order():
    """Places a new COD order from the frontend"""
    data = request.json
    new_order = {
        "order_id": len(orders) + 1,
        "items": data.get("items", []),
        "payment": data.get("payment", "COD"),
        "user": data.get("user", "Guest_Warangal"),
        "status": "PLACED"
    }
    orders.append(new_order)
    return jsonify(new_order), 201

# --- RESTAURANT ONBOARDING ---

@app.route("/register-restaurant", methods=["POST"])
def register_restaurant():
    """Allows a new restaurant to join Warangal Eats"""
    data = request.json
    if not data or not data.get("name"):
        return jsonify({"error": "Restaurant name is required"}), 400
        
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
    """Dashboard endpoint to see active orders"""
    pending = [o for o in orders if o['status'] == 'PLACED']
    return jsonify(pending)

@app.route("/restaurant/update-status", methods=["POST"])
def update_order_status():
    """Moves order from PLACED -> ACCEPTED -> DELIVERED"""
    data = request.json
    order_id = data.get("order_id")
    new_status = data.get("status")
    
    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = new_status
            return jsonify({"message": f"Order {order_id} is now {new_status}"})
            
    return jsonify({"error": "Order not found"}), 404

if __name__ == "__main__":
    # Ensure host is 0.0.0.0 for Azure Container Apps visibility
    app.run(host="0.0.0.0", port=5000)
