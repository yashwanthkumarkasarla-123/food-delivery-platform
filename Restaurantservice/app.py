from flask import Flask, jsonify, request
from flask_cors import CORS
import time

app = Flask(__name__)

# Enable CORS to allow requests from your GitHub Pages frontend to your Azure-hosted backend
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# --- IN-MEMORY DATABASE ---
# Note: In a production app, this would be replaced by a SQL (PostgreSQL) or NoSQL (MongoDB) database.
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
    }
]

# List to store all orders placed during the current server session
orders = []

# --- CUSTOMER ROUTES ---

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    """Returns the list of all available restaurants and their menus."""
    return jsonify(restaurants)

@app.route("/orders", methods=["POST", "OPTIONS"])
def place_order():
    """Handles new order placement from the customer app."""
    if request.method == "OPTIONS": 
        return jsonify({"status": "ok"}), 200 # Handle CORS pre-flight requests
        
    data = request.json
    new_order = {
        "order_id": len(orders) + 1,
        "res_id": data.get("res_id"),
        "status": "PENDING_RESTAURANT", # Initial state
        "items": data.get("items", []),
        "total": data.get("total", 0),
        "assigned_rider": None
    }
    orders.append(new_order)
    return jsonify(new_order), 201

# --- RESTAURANT PARTNER ROUTES ---

@app.route("/restaurant/manage-orders/<int:res_id>", methods=["GET"])
def manage_orders(res_id):
    """Fetches active orders for a specific restaurant ID."""
    # Filters out orders that don't belong to the restaurant or are already completed
    active = [o for o in orders if o.get("res_id") == res_id and o["status"] != "DELIVERED"]
    return jsonify(active), 200

@app.route("/restaurant/action", methods=["POST", "OPTIONS"])
def restaurant_action():
    """Allows restaurants to ACCEPT or REJECT a pending order."""
    if request.method == "OPTIONS": return jsonify({"status": "ok"}), 200
    
    data = request.json
    # Find the specific order in our list
    order = next((o for o in orders if o["order_id"] == data['order_id']), None)
    if order:
        # If accepted, status moves to PREPARING, triggering visibility for the Rider
        order["status"] = "PREPARING" if data['action'] == "ACCEPT" else "REJECTED"
        return jsonify({"message": "Success"}), 200
    return jsonify({"error": "Not Found"}), 404

# --- RIDER SPECIFIC ROUTES ---

@app.route("/rider/available-orders", methods=["GET"])
def get_rider_orders():
    """Fetches orders that are ready for pickup or currently being delivered."""
    relevant = ["PREPARING", "OUT_FOR_DELIVERY"]
    available = [o for o in orders if o["status"] in relevant]
    return jsonify(available), 200

@app.route("/rider/action", methods=["POST", "OPTIONS"])
def rider_action():
    """Handles the delivery lifecycle: Picking up from restaurant and delivering to customer."""
    if request.method == "OPTIONS": return jsonify({"status": "ok"}), 200
    
    data = request.json
    order = next((o for o in orders if o["order_id"] == data['order_id']), None)
    if order:
        if data['action'] == 'PICKUP':
            order["status"] = "OUT_FOR_DELIVERY"
            order["assigned_rider"] = data.get('rider_name', 'Rajesh')
        elif data['action'] == 'DELIVER':
            order["status"] = "DELIVERED"
        return jsonify({"message": "Status Updated"}), 200
    return jsonify({"error": "Order not found"}), 404

# --- TRACKING ROUTE ---

@app.route("/order-status/<int:order_id>", methods=["GET"])
def get_status(order_id):
    """Real-time endpoint for the customer app to poll for status updates."""
    order = next((o for o in orders if o["order_id"] == order_id), None)
    return jsonify(order) if order else (jsonify({"error": "Not Found"}), 404)

if __name__ == "__main__":
    # Host 0.0.0.0 is required for Docker/Azure Container Apps to expose the service
    app.run(host="0.0.0.0", port=5000)
