"""
CP372 Assignment 3 - Network Routing and Packet Forwarding Simulation
Main Execution Script
"""

import os

class NetworkSimulator:
    def __init__(self, topology_file):
        self.topology_file = topology_file
        self.nodes = set()
        self.adjacency_list = {}
        self.routing_tables = {}

    def load_topology(self):
        """Loads and parses the network topology file from inputs/"""
        if not os.path.exists(self.topology_file):
            print(f"Error: Topology file '{self.topology_file}' not found.")
            return False

        print(f"Loading topology from {self.topology_file}...")
        with open(self.topology_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if len(parts) == 3:
                    u, v, cost = parts[0], parts[1], int(parts[2])
                    self.nodes.add(u)
                    self.nodes.add(v)
                    
                    if u not in self.adjacency_list:
                        self.adjacency_list[u] = {}
                    if v not in self.adjacency_list:
                        self.adjacency_list[v] = {}
                        
                    self.adjacency_list[u][v] = cost
                    self.adjacency_list[v][u] = cost # Assuming undirected weighted links
        
        print(f"Discovered nodes: {sorted(list(self.nodes))}")
        return True

    def compute_shortest_paths(self, start_node):
        """Computes shortest paths using Dijkstra's algorithm for a given router"""
        distances = {node: float('inf') for node in self.nodes}
        next_hops = {node: None for node in self.nodes}
        distances[start_node] = 0
        unvisited = set(self.nodes)

        while unvisited:
            current_node = min(unvisited, key=lambda node: distances[node])
            if distances[current_node] == float('inf'):
                break
            unvisited.remove(current_node)

            for neighbor, weight in self.adjacency_list.get(current_node, {}).items():
                if neighbor in unvisited:
                    new_distance = distances[current_node] + weight
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        # Determine the first hop from start_node to neighbor
                        if current_node == start_node:
                            next_hops[neighbor] = neighbor
                        else:
                            # Trace back or inherit next hop
                            next_hops[neighbor] = next_hops[current_node]

        # Populate routing table format: {destination: {'next_hop': next_hop, 'cost': cost}}
        table = {}
        for node in self.nodes:
            if node != start_node:
                table[node] = {
                    "next_hop": next_hops[node],
                    "cost": distances[node]
                }
        self.routing_tables[start_node] = table

    def build_all_routing_tables(self):
        """Computes routing tables for all nodes in the network"""
        for node in self.nodes:
            self.compute_shortest_paths(node)
        print("Routing tables successfully computed for all routers.")

    def print_routing_tables(self):
        """Prints out routing tables for verification"""
        print("\n--- Computed Routing Tables ---")
        for router, table in self.routing_tables.itemsheta if hasattr(self, 'routing_tables') else self.routing_tables.items():
            pass # Handled below cleanly
        for router, table in self.routing_tables.items():
            print(f"Router {router} Routing Table:")
            print(f"{'Destination':<12} | {'Next Hop':<10} | {'Cost':<5}")
            print("-" * 35)
            for dest, info in table.items():
                print(f"{dest:<12} | {str(info['next_hop']):<10} | {info['cost']:<5}")
            print()

    def simulate_packet_forwarding(self, source, dest, payload):
        """Simulates hop-by-hop packet forwarding across the network graph"""
        print(f"\n--- Simulating Packet Transmission: {source} -> {dest} ---")
        current_node = source
        path = [current_node]

        if source not in self.nodes or dest not in self.nodes:
            print(f"Error: Source or Destination node not found in network topology.")
            return

        while current_node != dest:
            table = self.routing_tables.get(current_node, {})
            if dest not in table or table[dest]['next_hop'] is None:
                print(f"Router {current_node}: No route found to {dest}. Packet dropped.")
                return
            
            next_hop = table[dest]['next_hop']
            print(f"Router {current_node}: Forwarding packet to {{Payload: '{payload}'}} -> Next Hop: {next_hop}")
            current_node = next_hop
            path.append(current_node)

        print(f"Packet successfully delivered to destination {dest}!")
        print(f"Complete Forwarding Path: {' -> '.join(path)}")


def run_main():
    print("=== CP372 Assignment 3: Network Routing Simulation ===")
    
    # Path to topology input file
    topology_path = os.path.join("inputs", "topology_sample.txt")
    
    simulator = NetworkSimulator(topology_path)
    
    if simulator.load_topology():
        simulator.build_all_routing_tables()
        simulator.print_routing_tables()
        
        # Run test packet transmissions
        simulator.simulate_packet_forwarding("A", "D", "Test Packet 1: Hello Computer Networks")
        simulator.simulate_packet_forwarding("C", "A", "Test Packet 2: Return Acknowledgement")
        
    print("\n=== Simulation Completed Successfully ===")

if __name__ == "__main__":
    run_main()
