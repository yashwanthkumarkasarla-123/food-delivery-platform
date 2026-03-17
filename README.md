# food-delivery-platform
![Build Status](https://github.com/yashwanthkumarkasarla-123/food-delivery-platform/actions/workflows/deploy.yml/badge.svg)

#  Warangal Eats | Full-Stack Food Delivery Ecosystem

Warangal Eats is a real-time, three-way delivery platform that synchronizes the "Order-to-Door" lifecycle between Customers, Restaurants, and Riders. 

![Project Header](https://images.unsplash.com/photo-1526367790999-0150786486a9?q=80&w=1000&auto=format&fit=crop)

##  Key Features

* **Premium Customer Interface**: Dark-themed UI with glassmorphism effects, live order status polling, and persistent tracking using `localStorage`.
* **Restaurant Kitchen Dashboard**: Real-time management of orders (Accept/Reject/Mark Ready) with visual status indicators.
* **Logistics Rider Portal**: Dynamic job assignment that only shows orders when they are "Ready for Pickup," optimizing the rider's journey.
* **State Machine Architecture**: A robust backend logic that prevents out-of-order actions (e.g., a rider cannot pick up food that isn't cooked).
* **Cloud Native**: Fully containerized and deployed on **Azure Container Apps**.

##  Tech Stack

* **Frontend**: Vanilla JavaScript (ES6+), HTML5, CSS3 (Modern Flex/Grid).
* **Backend**: Python 3.x, Flask.
* **API**: RESTful architecture with CORS enabled for cross-origin deployment.
* **Deployment**: Azure Container Apps, GitHub Pages.

##  System Architecture

The project follows a "Triangle" communication model:

1.  **Customer** places an order via the API.
2.  **Restaurant** receives the order via polling and updates the state.
3.  **Rider** watches for the "Ready" state to initiate delivery.
4.  **Backend** acts as the single source of truth for the Order State Machine.



##  Getting Started

### Prerequisites
* Python 3.10+
* Flask
* Flask-CORS

### Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/your-username/warangal-eats.git](https://github.com/your-username/warangal-eats.git)


   ## 🔗 Live Demo Links

To see the real-time synchronization in action, open these links in separate tabs or devices:

* **[User App](https://yashwanthkumarkasarla-123.github.io/food-delivery-platform/)**: Place your order and track it live.
* **[Partner Portal](https://yashwanthkumarkasarla-123.github.io/food-delivery-platform/partner.html)**: Login (IDs: 1, 2, or 3) [Password: warangal123] to accept and cook orders.
* **[Rider Portal](https://yashwanthkumarkasarla-123.github.io/food-delivery-platform/delivery.html)**: Pick up and deliver the ready orders.

> **Tip:** For the best experience, try a "split-screen" view to watch the status update instantly across all three portals!
