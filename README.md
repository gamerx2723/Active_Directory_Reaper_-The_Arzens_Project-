# Active Directory Reaper - Active Directory Attack Path Simulation

## Overview
This project applies Deep Reinforcement Learning (Deep Q-Network) to autonomously discover and exploit privilege escalation paths within an Active Directory (AD) environment. By ingesting BloodHound graph data (JSON export), the AI agent learns to navigate complex lateral movement techniques such as Kerberoasting, DCSync, Unconstrained Delegation, and ACL abuse.

## Features
- **Dynamic Graph Parsing:** Automatically ingests BloodHound exports and dynamically calculates the start (a standard compromised user) and goal (Domain Admins).
- **Deep Q-Learning Agent:** Built using `stable-baselines3`, the agent is trained on a custom Gymnasium environment representing the AD network.
- **Real-Time Web UI:** A beautiful, responsive Flask and Cytoscape.js frontend to visualize the AD graph topology, monitor AI training metrics live, and run benchmarks.
- **Scalability:** The custom environment can parse synthetic noise and handle up to hundreds of nodes, training the AI to filter out dead-ends and isolate the golden attack path.

## Setup & Installation
1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. (Optional) Provide your own BloodHound JSON export to `data/bloodhound_export.json`. If missing, a procedural mock graph will be generated.

## Usage
Start the interactive UI:
```bash
python scripts/run_frontend_server.py
```
Then navigate to `http://localhost:8000`.

- **Start Training:** Trains the DQN model on the currently loaded graph structure.
- **Run Benchmark:** Evaluates the trained model against the optimal baseline path.

## Project Structure
- `src/` - Core Python modules containing the custom Gym environment, BloodHound graph parser, and attack technique mappings.
- `scripts/` - Scripts for model training, benchmarking, graph generation, and starting the web server.
- `frontend/` - HTML, CSS, and Vanilla JS for the modern dashboard visualization.
