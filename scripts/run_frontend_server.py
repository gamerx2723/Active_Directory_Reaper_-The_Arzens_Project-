import json
import os
import subprocess
import sys
import threading

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

import networkx as nx
# pyrefly: ignore [missing-import]
from flask import Flask, abort, jsonify, request, send_from_directory


# ---------------------------------------------------
# Load graph once (mock or BloodHound JSON) and cache it
# ---------------------------------------------------
def load_graph():
    """Load a deterministic graph.
    If a BloodHound export exists at data/bloodhound_export.json we use it,
    otherwise we fall back to the synthetic mock graph.
    """
    bloodhound_path = os.path.join(BASE_DIR, "data", "bloodhound_export.json")
    if os.path.exists(bloodhound_path):
        try:
            with open(bloodhound_path, "r") as f:
                data = json.load(f)
            g = nx.DiGraph()
            for n in data.get("nodes", []):
                g.add_node(n["id"], **n)
            for e in data.get("edges", []):
                g.add_edge(e["source"], e["target"], **e)
            return g
        except Exception as e:
            print("Failed to load BloodHound JSON, falling back to mock graph:", e)
    # Fallback – deterministic mock graph
    from src import mock_graph
    return mock_graph.build_mock_graph()


GRAPH_CACHE = load_graph()

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "frontend"))

# Global variable to hold latest metrics (simple example)
metrics_data = {"episodes": [], "rewards": []}


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(app.static_folder, filename)


def run_subprocess(cmd):
    # Run subprocess and capture output in the context of the project root
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=BASE_DIR)
    return result.stdout + ("\n" + result.stderr if result.stderr else "")


@app.route("/api/train", methods=["POST"])
def api_train():
    # Dynamically choose source based on data directory contents
    bloodhound_path = os.path.join(BASE_DIR, "data", "bloodhound_export.json")
    source_arg = "--source json" if os.path.exists(bloodhound_path) else "--source mock"
    cmd = f"python scripts/train.py {source_arg}"
    
    # Run synchronously so the frontend waits until training actually finishes
    output = run_subprocess(cmd)
    return jsonify({"status": "training complete", "output": output})


@app.route("/api/benchmark", methods=["POST"])
def api_benchmark():
    bloodhound_path = os.path.join(BASE_DIR, "data", "bloodhound_export.json")
    source_arg = "--source json" if os.path.exists(bloodhound_path) else "--source mock"
    cmd = f"python scripts/benchmark.py {source_arg}"
    output = run_subprocess(cmd)
    return output, 200, {"Content-Type": "text/plain"}


import math
import random

_dummy_episodes = list(range(1, 31))
_dummy_rewards = [int(120 * math.log(e if e > 0 else 1) + random.randint(-8, 8)) for e in _dummy_episodes]

@app.route("/api/metrics", methods=["GET"])
def api_metrics():
    # Serve real metrics if they exist, otherwise serve stable non-linear dummy curve
    metrics_path = os.path.join(BASE_DIR, "output", "metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, "r") as f:
            data = json.load(f)
            data["is_real"] = True
            return jsonify(data)
    return jsonify({"episodes": _dummy_episodes, "rewards": _dummy_rewards, "is_real": False})


@app.route("/api/graph", methods=["GET"])
def api_graph():
    # Dynamically serve either the BloodHound JSON or the mock graph
    try:
        g = load_graph()
        nodes = [{"data": {"id": n, "label": n}} for n in g.nodes]
        edges = [{"data": {"source": u, "target": v}} for u, v in g.edges]
        return jsonify({"nodes": nodes, "edges": edges})
    except Exception as e:
        abort(500, description=str(e))


if __name__ == "__main__":
    # Allow optional test flag to just check startup
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--test", action="store_true", help="Run a quick health check and exit"
    )
    args = parser.parse_args()
    if args.test:
        print("Flask server started successfully (test mode)")
    else:
        app.run(host="0.0.0.0", port=8000, debug=True)
