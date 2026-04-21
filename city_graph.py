import networkx as nx
import random

def create_city_graph():
    """Create a graph representing a city with intersections and roads"""
    G = nx.Graph()
    
    # City intersections (nodes) with coordinates
    intersections = {
        "A": (0, 0), "B": (1, 0), "C": (2, 0), "D": (3, 0),
        "E": (0, 1), "F": (1, 1), "G": (2, 1), "H": (3, 1),
        "I": (0, 2), "J": (1, 2), "K": (2, 2), "L": (3, 2),
        "M": (0, 3), "N": (1, 3), "O": (2, 3), "P": (3, 3),
    }
    
    # Add nodes with coordinates
    for node, (x, y) in intersections.items():
        G.add_node(node, x=x, y=y)
    
    # Add roads (edges) with distances
    roads = [
        ("A", "B", 2), ("B", "C", 3), ("C", "D", 2),
        ("E", "F", 2), ("F", "G", 1), ("G", "H", 3),
        ("I", "J", 3), ("J", "K", 2), ("K", "L", 2),
        ("M", "N", 2), ("N", "O", 3), ("O", "P", 2),
        ("A", "E", 2), ("E", "I", 3), ("I", "M", 2),
        ("B", "F", 1), ("F", "J", 2), ("J", "N", 3),
        ("C", "G", 3), ("G", "K", 2), ("K", "O", 2),
        ("D", "H", 2), ("H", "L", 1), ("L", "P", 3),
        ("B", "F", 1), ("F", "K", 4), ("G", "J", 2),
    ]
    
    for u, v, w in roads:
        G.add_edge(u, v, weight=w)
    
    return G, intersections

def find_shortest_path(G, start, end):
    """Find shortest path using Dijkstra's algorithm"""
    try:
        path = nx.dijkstra_path(G, start, end, weight='weight')
        distance = nx.dijkstra_path_length(G, start, end, weight='weight')
        return path, distance
    except nx.NetworkXNoPath:
        return None, float('inf')

def get_all_nodes(G):
    """Get all intersection names"""
    return list(G.nodes())

if __name__ == "__main__":
    G, intersections = create_city_graph()
    path, distance = find_shortest_path(G, "A", "P")
    print(f"Shortest path from A to P: {path}")
    print(f"Total distance: {distance}")