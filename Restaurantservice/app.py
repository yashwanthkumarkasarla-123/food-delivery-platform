from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

# --- IN-MEMORY DATABASE ---
restaurants = [
    {"id": 1, "name": "Raiyaan's Hotel", "location": "Subedari", "tags": ["Biryani"]},
    {"id": 2, "name": "Mandi.com", "location": "Hanamkonda", "tags": ["Arabian"]},
    {"id": 3, "name": "Kritunga Restaurant", "location": "Naimnagar", "tags": ["Rayalaseema"]}
]

orders = []

# --- CUSTOMER ENDPOINTS ---
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    return jsonify(restaurants)

@app.route("/orders", methods=["POST", "OPTIONS"])
def place_order():
    if request.method == "OPTIONS": return jsonify({"status": "ok"}), 200
    data = request.json
    
    # ADDED: customer_name and delivery_address so the Rider knows where to go
    new_order = {
        "order_id": len(orders) + 1,
        "res_id": data.get("res_id"),
        "customer_name": data.get("customer_name", "Guest"),
        "delivery_address": data.get("address", "Warangal Central"),
        "status": "PENDING_RESTAURANT",
        "items": data.get("items", []),
        "total": data.get("total", 0),
        "assigned_rider": None
    }
    orders.append(new_order)
    return jsonify(new_order), 201

@app.route("/order-status/<int:order_id>", methods=["GET"])
def get_status(order_id):
    order = next((o for o in orders if o["order_id"] == order_id), None)
    return jsonify(order) if order else (jsonify({"error": "Not Found"}), 404)

# --- RESTAURANT PARTNER ENDPOINTS ---
@app.route("/restaurant/manage-orders/<int:res_id>", methods=["GET"])
def manage_orders(res_id):
    active = [o for o in orders if o.get("res_id") == res_id and o["status"] != "DELIVERED"]
    return jsonify(active), 200

@app.route("/restaurant/action", methods=["POST", "OPTIONS"])
def restaurant_action():
    if request.method == "OPTIONS": return jsonify({"status": "ok"}), 200
    data = request.json
    order = next((o for o in orders if o["order_id"] == data['order_id']), None)
    
    if order:
        action = data.get('action')
        if action == "ACCEPT":
            order["status"] = "PREPARING"
        elif action == "MARK_READY":
            order["status"] = "READY_FOR_PICKUP"
        elif action == "REJECT":
            order["status"] = "REJECTED"
        return jsonify({"message": "Status Updated"}), 200
    return jsonify({"error": "Order not found"}), 404

# --- RIDER ENDPOINTS ---
@app.route("/rider/available-orders", methods=["GET"])
def get_rider_orders():
    # Riders see orders READY for pickup or ones they are currently delivering
    relevant = ["READY_FOR_PICKUP", "OUT_FOR_DELIVERY"]
    available = [o for o in orders if o["status"] in relevant]
    return jsonify(available), 200

@app.route("/rider/action", methods=["POST", "OPTIONS"])
def rider_action():
    if request.method == "OPTIONS": return jsonify({"status": "ok"}), 200
    data = request.json
    order = next((o for o in orders if o["order_id"] == data['order_id']), None)
    
    if order:
        action = data.get('action')
        if action == 'PICKUP':
            order["status"] = "OUT_FOR_DELIVERY"
            order["assigned_rider"] = "Rajesh Express"
        elif action == 'DELIVER':
            order["status"] = "DELIVERED"
        return jsonify({"message": "Rider status updated"}), 200
    return jsonify({"error": "Order not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
