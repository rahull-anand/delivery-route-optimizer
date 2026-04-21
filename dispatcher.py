from models import DeliveryAgent, Order, AgentStatus, OrderStatus, create_sample_agents
from city_graph import create_city_graph, find_shortest_path
import uuid

# Initialize city graph
G, intersections = create_city_graph()

# In-memory storage
agents = {a.id: a for a in create_sample_agents()}
orders = {}

def find_nearest_agent(pickup_location: str):
    """Find the nearest idle agent to the pickup location"""
    nearest_agent = None
    min_distance = float('inf')

    for agent in agents.values():
        if agent.status == AgentStatus.IDLE:
            _, distance = find_shortest_path(G, agent.current_location, pickup_location)
            if distance < min_distance:
                min_distance = distance
                nearest_agent = agent

    return nearest_agent, min_distance

def assign_order(customer_name: str, pickup_location: str, delivery_location: str):
    """Create order and assign to nearest agent"""
    # Create order
    order = Order(
        id=str(uuid.uuid4()),
        customer_name=customer_name,
        pickup_location=pickup_location,
        delivery_location=delivery_location
    )
    orders[order.id] = order

    # Find nearest agent
    agent, distance = find_nearest_agent(pickup_location)

    if not agent:
        print(f"❌ No idle agents available for order {order.id}")
        return order, None

    # Calculate full route: agent → pickup → delivery
    path_to_pickup, _ = find_shortest_path(G, agent.current_location, pickup_location)
    path_to_delivery, _ = find_shortest_path(G, pickup_location, delivery_location)

    # Combine routes (avoid duplicating pickup location)
    full_route = path_to_pickup + path_to_delivery[1:]

    # Assign order to agent
    agent.status = AgentStatus.MOVING_TO_PICKUP
    agent.current_order_id = order.id
    agent.route = full_route
    agent.route_index = 0

    order.status = OrderStatus.ASSIGNED
    order.assigned_agent_id = agent.id

    print(f"✅ Order {order.id[:8]} assigned to {agent.name}")
    print(f"📍 Route: {' → '.join(full_route)}")

    return order, agent

def reassign_order(order_id: str):
    """Reassign an order to a different agent"""
    order = orders.get(order_id)
    if not order:
        return None, None

    # Free up current agent
    current_agent = agents.get(order.assigned_agent_id)
    if current_agent:
        current_agent.status = AgentStatus.IDLE
        current_agent.current_order_id = None
        current_agent.route = []

    # Find new nearest agent
    agent, _ = find_nearest_agent(order.pickup_location)
    if not agent:
        return order, None

    # Recalculate route
    path_to_pickup, _ = find_shortest_path(G, agent.current_location, order.pickup_location)
    path_to_delivery, _ = find_shortest_path(G, order.pickup_location, order.delivery_location)
    full_route = path_to_pickup + path_to_delivery[1:]

    agent.status = AgentStatus.MOVING_TO_PICKUP
    agent.current_order_id = order.id
    agent.route = full_route
    agent.route_index = 0
    order.assigned_agent_id = agent.id

    print(f"🔄 Order {order.id[:8]} reassigned to {agent.name}")
    return order, agent

def get_all_agents():
    return [a.to_dict() for a in agents.values()]

def get_all_orders():
    return [o.to_dict() for o in orders.values()]