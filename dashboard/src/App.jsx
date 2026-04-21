import { useState, useEffect, useRef } from "react";
import axios from "axios";

const API = "http://127.0.0.1:8000";
const WS = "ws://127.0.0.1:8000/ws";

const GRID_SIZE = 400;
const CELL = GRID_SIZE / 3;

const COLORS = {
  idle: "#00ff88",
  moving_to_pickup: "#ffaa00",
  delivering: "#00aaff",
};

const NODE_POSITIONS = {
  A: [0, 3], B: [1, 3], C: [2, 3], D: [3, 3],
  E: [0, 2], F: [1, 2], G: [2, 2], H: [3, 2],
  I: [0, 1], J: [1, 1], K: [2, 1], L: [3, 1],
  M: [0, 0], N: [1, 0], O: [2, 0], P: [3, 0],
};

const EDGES = [
  ["A","B"],["B","C"],["C","D"],
  ["E","F"],["F","G"],["G","H"],
  ["I","J"],["J","K"],["K","L"],
  ["M","N"],["N","O"],["O","P"],
  ["A","E"],["E","I"],["I","M"],
  ["B","F"],["F","J"],["J","N"],
  ["C","G"],["G","K"],["K","O"],
  ["D","H"],["H","L"],["L","P"],
];

function getPos(node) {
  const [col, row] = NODE_POSITIONS[node];
  return { x: 60 + col * CELL, y: 60 + row * CELL };
}

export default function App() {
  const [agents, setAgents] = useState([]);
  const [orders, setOrders] = useState([]);
  const [form, setForm] = useState({ customer_name: "Teja", pickup_location: "A", delivery_location: "P" });
  const [message, setMessage] = useState("");
  const wsRef = useRef(null);

  useEffect(() => {
    fetchData();
    connectWS();
    return () => wsRef.current?.close();
  }, []);

  const fetchData = async () => {
    const [a, o] = await Promise.all([axios.get(`${API}/agents`), axios.get(`${API}/orders`)]);
    setAgents(a.data);
    setOrders(o.data);
  };

  const connectWS = () => {
    const ws = new WebSocket(WS);
    wsRef.current = ws;
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === "initial_state") {
        setAgents(data.agents);
        setOrders(data.orders);
      } else if (data.type === "agent_update") {
        setAgents(prev => prev.map(a => a.id === data.agent.id ? data.agent : a));
        if (data.order) setOrders(prev => prev.map(o => o.id === data.order.id ? data.order : o));
      }
    };
    ws.onclose = () => setTimeout(connectWS, 2000);
  };

  const placeOrder = async () => {
    try {
      const res = await axios.post(`${API}/orders`, form);
      setMessage(`✅ Order assigned to ${res.data.assigned_agent?.name || "No agent available"}!`);
      fetchData();
      setTimeout(() => setMessage(""), 3000);
    } catch {
      setMessage("❌ Failed to place order!");
    }
  };

  const nodes = Object.keys(NODE_POSITIONS);

  return (
    <div style={{ fontFamily: "monospace", backgroundColor: "#0f0f0f", minHeight: "100vh", color: "white", padding: "20px" }}>
      <h1 style={{ color: "#00ff88", textAlign: "center" }}>🚴 Real-Time Delivery Route Optimizer</h1>

      <div style={{ display: "flex", gap: "20px", flexWrap: "wrap", justifyContent: "center" }}>

        {/* City Map */}
        <div style={{ backgroundColor: "#1a1a1a", borderRadius: "10px", padding: "20px" }}>
          <h2 style={{ color: "#00ff88" }}>🗺️ City Map</h2>
          <svg width={GRID_SIZE + 80} height={GRID_SIZE + 80}>
            {/* Draw edges */}
            {EDGES.map(([a, b], i) => {
              const pa = getPos(a), pb = getPos(b);
              return <line key={i} x1={pa.x} y1={pa.y} x2={pb.x} y2={pb.y} stroke="#333" strokeWidth={2} />;
            })}

            {/* Draw nodes */}
            {nodes.map(node => {
              const { x, y } = getPos(node);
              return (
                <g key={node}>
                  <circle cx={x} cy={y} r={18} fill="#222" stroke="#444" strokeWidth={2} />
                  <text x={x} y={y + 5} textAnchor="middle" fill="white" fontSize={12}>{node}</text>
                </g>
              );
            })}

            {/* Draw agents */}
            {agents.map(agent => {
              const { x, y } = getPos(agent.current_location);
              const color = COLORS[agent.status] || "#fff";
              return (
                <g key={agent.id}>
                  <circle cx={x} cy={y} r={10} fill={color} opacity={0.9} />
                  <text x={x} y={y - 20} textAnchor="middle" fill={color} fontSize={10}>{agent.name}</text>
                </g>
              );
            })}
          </svg>

          {/* Legend */}
          <div style={{ display: "flex", gap: "15px", marginTop: "10px" }}>
            <span style={{ color: "#00ff88" }}>● Idle</span>
            <span style={{ color: "#ffaa00" }}>● To Pickup</span>
            <span style={{ color: "#00aaff" }}>● Delivering</span>
          </div>
        </div>

        {/* Right Panel */}
        <div style={{ display: "flex", flexDirection: "column", gap: "20px", minWidth: "300px" }}>

          {/* Place Order */}
          <div style={{ backgroundColor: "#1a1a1a", borderRadius: "10px", padding: "20px" }}>
            <h2 style={{ color: "#00ff88" }}>📦 Place Order</h2>
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              <input value={form.customer_name} onChange={e => setForm({ ...form, customer_name: e.target.value })}
                placeholder="Customer name"
                style={{ padding: "8px", borderRadius: "6px", backgroundColor: "#333", color: "white", border: "none" }} />

              <select value={form.pickup_location} onChange={e => setForm({ ...form, pickup_location: e.target.value })}
                style={{ padding: "8px", borderRadius: "6px", backgroundColor: "#333", color: "white", border: "none" }}>
                {nodes.map(n => <option key={n} value={n}>Pickup: {n}</option>)}
              </select>

              <select value={form.delivery_location} onChange={e => setForm({ ...form, delivery_location: e.target.value })}
                style={{ padding: "8px", borderRadius: "6px", backgroundColor: "#333", color: "white", border: "none" }}>
                {nodes.map(n => <option key={n} value={n}>Deliver to: {n}</option>)}
              </select>

              <button onClick={placeOrder}
                style={{ padding: "10px", backgroundColor: "#00ff88", color: "#000", border: "none", borderRadius: "6px", cursor: "pointer", fontWeight: "bold" }}>
                Place Order 🚴
              </button>
              {message && <span style={{ color: "#00ff88", fontSize: "12px" }}>{message}</span>}
            </div>
          </div>

          {/* Agents Status */}
          <div style={{ backgroundColor: "#1a1a1a", borderRadius: "10px", padding: "20px" }}>
            <h2 style={{ color: "#00ff88" }}>🚴 Agents</h2>
            {agents.map(agent => (
              <div key={agent.id} style={{ padding: "8px", borderBottom: "1px solid #333" }}>
                <span style={{ color: COLORS[agent.status] }}>●</span> {agent.name} — {agent.current_location} — <span style={{ color: "#888" }}>{agent.status}</span>
                {agent.route?.length > 0 && <div style={{ color: "#555", fontSize: "11px" }}>Route: {agent.route.join(" → ")}</div>}
              </div>
            ))}
          </div>

          {/* Orders */}
          <div style={{ backgroundColor: "#1a1a1a", borderRadius: "10px", padding: "20px" }}>
            <h2 style={{ color: "#00ff88" }}>📋 Orders</h2>
            {orders.length === 0 ? <p style={{ color: "#888" }}>No orders yet</p> :
              orders.map(order => (
                <div key={order.id} style={{ padding: "8px", borderBottom: "1px solid #333", fontSize: "12px" }}>
                  <div>{order.customer_name} → {order.pickup_location} to {order.delivery_location}</div>
                  <div style={{ color: order.status === "delivered" ? "#00ff88" : "#ffaa00" }}>{order.status}</div>
                </div>
              ))
            }
          </div>
        </div>
      </div>
    </div>
  );
}