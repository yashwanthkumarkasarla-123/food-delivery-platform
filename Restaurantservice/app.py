from flask import Flask, jsonify, request
from flask_cors import CORS
import time

app = Flask(__name__)

# Essential for cross-domain communication between GitHub Pages and Azure
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# In-memory database with MENU items added back in
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
        "tags": ["Rayalaseema"],
        "menu": [{"item": "Ragi Sangati", "price": 180}, {"item": "Natukodi Pulusu", "price": 320}]
    },
    {
        "id": 4, "name": "Suprabha Hotel", "location": "Hanamkonda", "rating": 4.2, 
        "tags": ["South Indian Veg"],
        "menu": [{"item": "Ghee Roast Dosa", "price": 80}, {"item": "South Indian Thali", "price": 150}]
    }
]

orders = []

@app.route("/")
def health():
    return jsonify({"status": "Warangal Eats Backend Online", "timestamp": time.time()}), 200

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    return jsonify(restaurants)

# --- CUSTOMER: PLACE ORDER (Update this) ---
@app.route("/orders", methods=["POST", "OPTIONS"])
def place_order():
    if request.method == "OPTIONS": return jsonify({"status": "ok"}), 200
    data = request.json
    
    # Find restaurant name for the Rider's benefit
    res_info = next((r for r in restaurants if r["id"] == data.get("res_id")), {"name": "Unknown"})

    new_order = {
        "order_id": len(orders) + 1,
        "res_id": data.get("res_id"),
        "restaurant_name": res_info["name"], # Added this
        "location": res_info.get("location", "Warangal"), # Added this
        "status": "PENDING_RESTAURANT",
        "items": data.get("items", []),
        "total": data.get("total", 0),
        "assigned_rider": None,
        "created_at": time.time()
    }
    orders.append(new_order)
    return jsonify(new_order), 201

# --- RIDER: VIEW READY ORDERS (New Route) ---
@app.route("/rider/available-orders", methods=["GET"])
def get_rider_orders():
    # Riders only care about orders being prepared or ready
    ready_orders = [o for o in orders if o["status"] == "PREPARING"]
    return jsonify(ready_orders), 200

# --- PARTNER: MANAGE SPECIFIC RESTAURANT ORDERS ---
@app.route("/restaurant/manage-orders/<int:res_id>", methods=["GET"])
def manage_orders(res_id):
    active_orders = [o for o in orders if o.get("res_id") == res_id and o["status"] != "DELIVERED"]
    return jsonify(active_orders), 200

# --- PARTNER: ACCEPT/REJECT ACTION ---
@app.route("/restaurant/action", methods=["POST", "OPTIONS"])
def restaurant_action():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
        
    data = request.json
    order_id = data.get('order_id')
    action = data.get('action')
    
    order = next((o for o in orders if o["order_id"] == order_id), None)
    if order:
        order["status"] = "PREPARING" if action == "ACCEPT" else "REJECTED"
        return jsonify({"message": f"Order {action}ED"}), 200
    return jsonify({"error": "Order not found"}), 404

# --- CUSTOMER: TRACK STATUS ---
@app.route("/order-status/<int:order_id>", methods=["GET"])
def get_status(order_id):
    order = next((o for o in orders if o["order_id"] == order_id), None)
    if order:
        return jsonify(order), 200
    return jsonify({"error": "Order not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
