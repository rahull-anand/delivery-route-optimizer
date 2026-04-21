from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dispatcher import assign_order, reassign_order, get_all_agents, get_all_orders, agents, orders
from simulation import connected_clients, move_agents
from city_graph import create_city_graph
import asyncio
app = FastAPI(title="Delivery Route Optimizer")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

G, intersections = create_city_graph()

# Start simulation on startup
@app.on_event("startup")
async def startup():
    asyncio.create_task(move_agents())
    print("🚀 Delivery simulation started!")

class OrderRequest(BaseModel):
    customer_name: str
    pickup_location: str
    delivery_location: str

@app.post("/orders")
def create_order(request: OrderRequest):
    """Place a new delivery order"""
    order, agent = assign_order(
        request.customer_name,
        request.pickup_location,
        request.delivery_location
    )
    return {
        "order": order.to_dict(),
        "assigned_agent": agent.to_dict() if agent else None
    }

@app.post("/orders/{order_id}/reassign")
def reassign(order_id: str):
    """Reassign an order to a different agent"""
    order, agent = reassign_order(order_id)
    return {
        "order": order.to_dict() if order else None,
        "new_agent": agent.to_dict() if agent else None
    }

@app.get("/agents")
def get_agents():
    """Get all delivery agents and their locations"""
    return get_all_agents()

@app.get("/orders")
def get_orders():
    """Get all orders"""
    return get_all_orders()

@app.get("/graph")
def get_graph():
    """Get city graph for the dashboard map"""
    nodes = []
    for node, data in G.nodes(data=True):
        nodes.append({
            "id": node,
            "x": data["x"],
            "y": data["y"]
        })

    edges = []
    for u, v, data in G.edges(data=True):
        edges.append({
            "from": u,
            "to": v,
            "weight": data["weight"]
        })

    return {"nodes": nodes, "edges": edges}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time agent location updates"""
    await websocket.accept()
    connected_clients.add(websocket)
    print(f"📡 Dashboard connected! Total: {len(connected_clients)}")

    try:
        # Send initial state
        await websocket.send_json({
            "type": "initial_state",
            "agents": get_all_agents(),
            "orders": get_all_orders()
        })

        # Keep connection alive
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        connected_clients.discard(websocket)
        print(f"📡 Dashboard disconnected!")

@app.get("/")
def root():
    return {"message": "Delivery Route Optimizer is running! Go to /docs to test it."}
