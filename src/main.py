"""
CP372 Assignment 3 - Network Routing and Packet Forwarding Simulation
Includes Bonus Mark Task for 10%: UDP Socket-Based Link-State Advertisements & Packet Forwarding
"""

import socket
import threading
import time
import json

# Network topology configuration
TOPOLOGY_DATA = """
A B 1
A C 4
B C 2
B D 5
C D 1
"""

# Dedicated UDP port assignments per router (127.0.0.1)
ROUTER_PORTS = {
    "A": 5001,
    "B": 5002,
    "C": 5003,
    "D": 5004
}


class SocketRouterNode:
    """Represents an independent router listening on its own UDP port."""
    def __init__(self, name, port, all_ports, neighbors):
        self.name = name
        self.port = port
        self.all_ports = all_ports
        self.neighbors = neighbors  # {neighbor_name: cost}
        self.lsdb = {name: dict(neighbors)}  # Link-State Database
        self.routing_table = {}
        self.running = True
        self.received_packets = []

        # Bind UDP socket to dedicated port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", self.port))
        self.sock.settimeout(0.2)

        self.listener_thread = threading.Thread(target=self._listen, daemon=True)
        self.listener_thread.start()

    def _listen(self):
        """Background thread listening for incoming LSA and DATA UDP packets."""
        while self.running:
            try:
                raw_data, _ = self.sock.recvfrom(4096)
                msg = json.loads(raw_data.decode("utf-8"))
                msg_type = msg.get("type")

                if msg_type == "LSA":
                    origin = msg["origin"]
                    links = msg["links"]
                    self.lsdb[origin] = links

                elif msg_type == "DATA":
                    dest = msg["dest"]
                    payload = msg["payload"]
                    path = msg["path"] + [self.name]

                    if dest == self.name:
                        print(f"[UDP Port {self.port} | Router {self.name}] Packet DELIVERED! Payload: '{payload}'")
                        print(f"    -> Verified UDP Socket Path: {' -> '.join(path)}")
                        self.received_packets.append(msg)
                    else:
                        self.forward_data_packet(dest, payload, path)

            except socket.timeout:
                continue
            except OSError:
                break

    def advertise_link_state(self):
        """BONUS REQUIREMENT: Advertise link costs one-by-one via UDP to all other routers."""
        lsa_packet = json.dumps({
            "type": "LSA",
            "origin": self.name,
            "links": self.neighbors
        }).encode("utf-8")

        for target_router, target_port in self.all_ports.items():
            if target_router != self.name:
                print(f"[UDP Port {self.port} | Router {self.name}] Sending LSA unicast to Router {target_router} (Port {target_port})")
                self.sock.sendto(lsa_packet, ("127.0.0.1", target_port))

    def compute_dijkstra(self):
        """Computes shortest paths from local Link-State Database (LSDB)."""
        all_nodes = set(self.lsdb.keys())
        for links in self.lsdb.values():
            all_nodes.update(links.keys())

        distances = {node: float("inf") for node in all_nodes}
        next_hops = {node: None for node in all_nodes}
        distances[self.name] = 0
        unvisited = set(all_nodes)

        while unvisited:
            current = min(unvisited, key=lambda n: distances[n])
            if distances[current] == float("inf"):
                break
            unvisited.remove(current)

            for neighbor, cost in self.lsdb.get(current, {}).items():
                if neighbor in unvisited:
                    new_dist = distances[current] + cost
                    if new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        next_hops[neighbor] = neighbor if current == self.name else next_hops[current]

        self.routing_table = {
            node: {"next_hop": next_hops[node], "cost": distances[node]}
            for node in all_nodes if node != self.name
        }

    def forward_data_packet(self, dest, payload, path=None):
        """BONUS REQUIREMENT: Transmit packet along path using UDP sockets."""
        if path is None:
            path = [self.name]

        route = self.routing_table.get(dest)
        if not route or not route["next_hop"]:
            print(f"[UDP Port {self.port} | Router {self.name}] No route to {dest}. Dropping packet.")
            return

        next_hop = route["next_hop"]
        next_port = self.all_ports[next_hop]
        print(f"[UDP Port {self.port} | Router {self.name}] Forwarding UDP packet to {dest} via Next Hop {next_hop} (Port {next_port})")

        packet = json.dumps({
            "type": "DATA",
            "dest": dest,
            "payload": payload,
            "path": path
        }).encode("utf-8")
        self.sock.sendto(packet, ("127.0.0.1", next_port))

    def shutdown(self):
        self.running = False
        self.sock.close()


def parse_topology(text_data):
    graph = {}
    for line in text_data.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) == 3:
            u, v, cost = parts[0], parts[1], int(parts[2])
            graph.setdefault(u, {})[v] = cost
            graph.setdefault(v, {})[u] = cost
    return graph


def run_socket_simulation():
    print("=== CP372 Assignment 3: UDP Socket-Based Routing Simulation (Bonus) ===")
    graph = parse_topology(TOPOLOGY_DATA)
    routers = {}

    try:
        # 1. Initialize each router on its own dedicated UDP port
        for node in sorted(graph.keys()):
            port = ROUTER_PORTS[node]
            routers[node] = SocketRouterNode(node, port, ROUTER_PORTS, graph[node])
            print(f"Initialized Router {node} listening on 127.0.0.1:{port}")

        time.sleep(0.3)

        # 2. Link-State Advertisement phase (one-by-one unicast over UDP)
        print("\n--- Phase 1: Unicast Link-State Advertisements (LSA) over UDP ---")
        for node in sorted(routers.keys()):
            routers[node].advertise_link_state()
            time.sleep(0.1)

        time.sleep(0.4)

        # 3. Compute routing tables using Dijkstra's Algorithm
        print("\n--- Phase 2: Computing Shortest-Path Routing Tables ---")
        for node in sorted(routers.keys()):
            routers[node].compute_dijkstra()
            print(f"\nRouter {node} (Port {ROUTER_PORTS[node]}) Routing Table:")
            print(f"{'Destination':<12} | {'Next Hop':<10} | {'Cost':<5}")
            print("-" * 35)
            for dest, info in sorted(routers[node].routing_table.items()):
                print(f"{dest:<12} | {str(info['next_hop']):<10} | {info['cost']:<5}")

        # 4. Transmit data packets hop-by-hop over UDP sockets
        print("\n--- Phase 3: Hop-by-Hop Packet Forwarding over UDP Sockets ---")
        print("\n[Transmission 1: Router A -> Router D]")
        routers["A"].forward_data_packet("D", "Hello CP372 via UDP Sockets!")
        time.sleep(0.5)

        print("\n[Transmission 2: Router C -> Router A]")
        routers["C"].forward_data_packet("A", "ACK Received via UDP Sockets!")
        time.sleep(0.5)

    finally:
        for router in routers.values():
            router.shutdown()

    print("\n=== UDP Socket Simulation Completed Successfully ===")


if __name__ == "__main__":
    run_socket_simulation()
