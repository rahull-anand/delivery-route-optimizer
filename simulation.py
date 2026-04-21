import asyncio
from models import AgentStatus, OrderStatus
from dispatcher import agents, orders, G, find_nearest_agent
from datetime import datetime

connected_clients = set()

async def broadcast(message: dict):
    """Send update to all connected dashboard clients"""
    if connected_clients:
        disconnected = set()
        for client in connected_clients:
            try:
                await client.send_json(message)
            except:
                disconnected.add(client)
        connected_clients.difference_update(disconnected)

async def check_reassignment():
    """If an agent has been moving for too long, reassign to closer agent"""
    for order in orders.values():
        if order.status.value in ["assigned", "picked_up"]:
            agent = agents.get(order.assigned_agent_id)
            if not agent:
                continue

            # Find if there's a much closer idle agent
            from city_graph import find_shortest_path
            nearest_agent, nearest_distance = find_nearest_agent(order.pickup_location)

            if nearest_agent and nearest_agent.id != agent.id:
                _, current_distance = find_shortest_path(G, agent.current_location, order.pickup_location)

                # If another agent is 3x closer — reassign!
                if nearest_distance * 3 < current_distance:
                    print(f"🔄 Reassigning order {order.id[:8]} — found closer agent {nearest_agent.name}!")
                    from dispatcher import reassign_order
                    reassign_order(order.id)
                    await broadcast({
                        "type": "reassignment",
                        "message": f"Order reassigned to {nearest_agent.name}!",
                        "agents": [a.to_dict() for a in agents.values()],
                        "orders": [o.to_dict() for o in orders.values()]
                    })

async def move_agents():
    """Move all active agents one step along their route every 2 seconds"""
    tick = 0
    while True:
        for agent in agents.values():
            if agent.status in [AgentStatus.MOVING_TO_PICKUP, AgentStatus.DELIVERING]:
                if agent.route and agent.route_index < len(agent.route) - 1:
                    agent.route_index += 1
                    agent.current_location = agent.route[agent.route_index]

                    order = orders.get(agent.current_order_id)

                    if order and agent.current_location == order.pickup_location:
                        agent.status = AgentStatus.DELIVERING
                        order.status = OrderStatus.PICKED_UP
                        print(f"📦 {agent.name} picked up order at {order.pickup_location}")

                    elif order and agent.current_location == order.delivery_location:
                        agent.status = AgentStatus.IDLE
                        agent.current_order_id = None
                        agent.route = []
                        agent.route_index = 0
                        agent.total_deliveries += 1
                        order.status = OrderStatus.DELIVERED
                        order.delivered_at = datetime.now().isoformat()
                        print(f"✅ {agent.name} delivered order to {order.delivery_location}!")

                    await broadcast({
                        "type": "agent_update",
                        "agent": agent.to_dict(),
                        "order": order.to_dict() if order else None
                    })

        # Check reassignment every 10 ticks
        if tick % 10 == 0:
            await check_reassignment()

        tick += 1
        await asyncio.sleep(2)