from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum
import uuid
from datetime import datetime
class AgentStatus(Enum):
    IDLE = "idle"
    DELIVERING = "delivering"
    MOVING_TO_PICKUP = "moving_to_pickup"

class OrderStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    PICKED_UP = "picked_up"
    DELIVERED = "delivered"

@dataclass
class DeliveryAgent:
    id: str
    name: str
    current_location: str
    status: AgentStatus = AgentStatus.IDLE
    current_order_id: Optional[str] = None
    route: List[str] = field(default_factory=list)
    route_index: int = 0
    total_deliveries: int = 0

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "current_location": self.current_location,
            "status": self.status.value,
            "current_order_id": self.current_order_id,
            "route": self.route,
            "route_index": self.route_index,
            "total_deliveries": self.total_deliveries
        }

@dataclass
class Order:
    id: str
    customer_name: str
    pickup_location: str
    delivery_location: str
    status: OrderStatus = OrderStatus.PENDING
    assigned_agent_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    delivered_at: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "pickup_location": self.pickup_location,
            "delivery_location": self.delivery_location,
            "status": self.status.value,
            "assigned_agent_id": self.assigned_agent_id,
            "created_at": self.created_at,
            "delivered_at": self.delivered_at
        }

def create_sample_agents():
    """Create 5 delivery agents at different locations"""
    agents = [
        DeliveryAgent(id=str(uuid.uuid4()), name="Ravi", current_location="A"),
        DeliveryAgent(id=str(uuid.uuid4()), name="Priya", current_location="D"),
        DeliveryAgent(id=str(uuid.uuid4()), name="Arjun", current_location="M"),
        DeliveryAgent(id=str(uuid.uuid4()), name="Sneha", current_location="P"),
        DeliveryAgent(id=str(uuid.uuid4()), name="Kiran", current_location="H"),
    ]
    return agents
