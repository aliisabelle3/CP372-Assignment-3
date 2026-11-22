# CP372 Assignment 3 - Network Routing & Packet Forwarding Simulation

A Python-based network routing and packet forwarding simulation implementing topology design, routing algorithms, and packet transmission.

**Course:** CP372 - Tao Xu
**Assignment:** Assignment 3 - Network Routing and Packet Forwarding  
**Author:** Ali Lopez

---

## Folder Structure

```text
cp372-a3/
├── src/
│   └── main.py             # Main execution & simulation driver
├── inputs/
│   └── topology_sample.txt # Sample network topology configuration file
├── outputs/
│   └── placeholder.txt     # Output logs directory
├── report.pdf              # Comprehensive performance analysis report
└── README.md               # Project documentation

---

## Bonus Implementation (+10% UDP Socket Simulation)

* **Dedicated Router Ports:** Each router runs on a distinct localhost UDP port (`A: 5001`, `B: 5002`, `C: 5003`, `D: 5004`).
* **Unicast Link-State Advertisements:** Each router transmits its link costs individually (one-by-one) to every other router over UDP sockets rather than using shared memory or broadcast.
* **Socket Packet Forwarding:** Data packets are transmitted hop-by-hop across actual UDP sockets along the computed shortest path.
