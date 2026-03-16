from flask import Flask, jsonify, request
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

# In-memory database
restaurants = [
    {"id": 1, "name": "Papadams Blue", "location": "Hanamkonda", "rating": 4.4, "tags": ["Biryani", "South Indian"], "menu": [{"item": "Chicken Biryani", "price": 280}, {"item": "Butter Naan", "price": 40}]},
    {"id": 2, "name": "Kritunga", "location": "Subedari", "rating": 5.0, "tags": ["Telugu"], "menu": [{"item": "Ragi Sangati", "price": 180}]}
]
orders = []

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    return jsonify(restaurants)

@app.route("/orders", methods=["POST"])
def place_order():
    data = request.json
    new_order = {
        "order_id": len(orders) + 1,
        "status": "PENDING_RESTAURANT",
        "items": data.get("items"),
        "assigned_rider": None,
        "created_at": time.time()
    }
    orders.append(new_order)
    return jsonify(new_order)

# --- REAL-TIME TRACKING ENDPOINTS ---

@app.route("/order-status/<int:order_id>", methods=["GET"])
def get_status(order_id):
    """Customer app calls this every 3 seconds to update the UI."""
    order = next((o for o in orders if o["order_id"] == order_id), None)
    if order:
        return jsonify(order)
    return jsonify({"error": "Order not found"}), 404

@app.route("/restaurant/action", methods=["POST"])
def restaurant_action():
    """Admin app calls this to ACCEPT or REJECT."""
    data = request.json
    order = next((o for o in orders if o["order_id"] == data['order_id']), None)
    if order:
        order["status"] = "PREPARING" if data['action'] == "ACCEPT" else "REJECTED"
        return jsonify({"message": f"Order {data['action']}ED"})
    return jsonify({"error": "Order not found"}), 404

@app.route("/rider/claim", methods=["POST"])
def rider_claim():
    """Rider app calls this to pick up the order."""
    data = request.json
    order = next((o for o in orders if o["order_id"] == data['order_id']), None)
    if order:
        order["status"] = "OUT_FOR_DELIVERY"
        order["assigned_rider"] = data.get("rider_name", "Rajesh")
        return jsonify({"message": "Rider Assigned!"})
    return jsonify({"error": "Order not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
