import asyncio
from models import AgentStatus, OrderStatus
from dispatcher import agents, orders, G
from city_graph import find_shortest_path
from datetime import datetime

# Store connected websocket clients
connected_clients = set()

async def broadcast(message: dict):
    """Send update to all connected dashboard clients"""
    import json
    if connected_clients:
        disconnected = set()
        for client in connected_clients:
            try:
                await client.send_json(message)
            except:
                disconnected.add(client)
        connected_clients.difference_update(disconnected)

async def move_agents():
    """Move all active agents one step along their route every 2 seconds"""
    while True:
        for agent in agents.values():
            if agent.status in [AgentStatus.MOVING_TO_PICKUP, AgentStatus.DELIVERING]:
                if agent.route and agent.route_index < len(agent.route) - 1:
                    # Move one step forward
                    agent.route_index += 1
                    agent.current_location = agent.route[agent.route_index]

                    order = orders.get(agent.current_order_id)

                    # Check if agent reached pickup
                    if order and agent.current_location == order.pickup_location:
                        agent.status = AgentStatus.DELIVERING
                        order.status = OrderStatus.PICKED_UP
                        print(f"📦 {agent.name} picked up order at {order.pickup_location}")

                    # Check if agent reached delivery
                    elif order and agent.current_location == order.delivery_location:
                        agent.status = AgentStatus.IDLE
                        agent.current_order_id = None
                        agent.route = []
                        agent.route_index = 0
                        agent.total_deliveries += 1
                        order.status = OrderStatus.DELIVERED
                        order.delivered_at = datetime.now().isoformat()
                        print(f"✅ {agent.name} delivered order to {order.delivery_location}!")

                    # Broadcast location update to dashboard
                    await broadcast({
                        "type": "agent_update",
                        "agent": agent.to_dict(),
                        "order": order.to_dict() if order else None
                    })

        await asyncio.sleep(2)  # Move every 2 seconds