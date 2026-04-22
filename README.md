# 🚴 Real-Time Delivery Route Optimizer

A production-grade delivery routing system that optimizes delivery routes in real-time using Dijkstra algorithm — similar to how Swiggy and Zomato manage their delivery fleet.

## 🔥 Features
- **Dijkstra Shortest Path** — finds optimal route for every delivery
- **Smart Agent Assignment** — automatically assigns nearest idle agent
- **Dynamic Reassignment** — reassigns orders if a closer agent becomes available
- **Real-Time Tracking** — live agent movement via WebSockets
- **Live Map Dashboard** — React dashboard showing agents moving in real time
- **5 Concurrent Agents** — handle multiple deliveries simultaneously

## 🛠️ Tech Stack
- **Backend** — Python, FastAPI, NetworkX
- **Real-time** — WebSockets
- **Frontend** — React, Vite
- **Algorithm** — Dijkstra shortest path (via NetworkX)
- **Infrastructure** — Docker, AWS EC2

## 🚀 How to Run

### Backend
pip install -r requirements.txt
uvicorn main:app --reload

### Frontend
cd dashboard
npm install
npm run dev

Open http://localhost:5173 to see the live dashboard.

## 🏗️ Architecture
Customer places order
        ↓
System finds nearest idle agent (Dijkstra)
        ↓
Agent moves along optimal route in real time
        ↓
WebSockets broadcast location to dashboard
        ↓
Dynamic reassignment if closer agent found
        ↓
Order delivered!
