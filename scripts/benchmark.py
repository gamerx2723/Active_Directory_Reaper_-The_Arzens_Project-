"""Benchmark trained DQN agent vs BloodHound shortest-path baseline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import networkx as nx
from stable_baselines3 import DQN

from src.ad_env import ADEnv
from src.graph_loader import load_graph_from_json, load_graph_from_neo4j
from src.mock_graph import bloodhound_shortest_path, build_mock_graph
from src.techniques import MITRE_MAPPING


def get_graph(args):
    if args.source == "mock":
        graph = build_mock_graph()
        start = args.start or "user1"
        goal = args.goal or "domain_admin"
    elif args.source == "neo4j":
        graph = load_graph_from_neo4j(
            args.neo4j_uri, args.neo4j_user, args.neo4j_password
        )
        start = (args.start or "USER1").upper()
        goal = (args.goal or "DOMAIN ADMINS").upper()
    else:
        graph = load_graph_from_json(args.json_path)
        start = (args.start or "USER1").upper()
        goal = (args.goal or "DOMAIN ADMINS").upper()
    
    from src.graph_loader import auto_select_start_goal
    start, goal = auto_select_start_goal(graph, start, goal)
    return graph, start, goal


def run_agent(model_path: str, env: ADEnv, episodes: int = 10) -> list[dict]:
    model = DQN.load(model_path)
    results = []

    for ep in range(episodes):
        obs, _ = env.reset()
        path = [env.current]
        techniques = []
        done = False

        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(int(action))
            if info.get("moved") and info.get("technique"):
                techniques.append(info["technique"])
            path.append(env.current)
            done = terminated or truncated

        results.append(
            {
                "episode": ep + 1,
                "path": path,
                "path_length": len(path) - 1,
                "techniques": techniques,
                "reached_goal": path[-1] == env.goal_node,
                "total_reward": reward,
            }
        )

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark agent vs BloodHound baseline"
    )
    parser.add_argument("--source", choices=["mock", "neo4j", "json"], default="mock")
    parser.add_argument("--neo4j-uri", default="bolt://localhost:7687")
    parser.add_argument("--neo4j-user", default="neo4j")
    parser.add_argument("--neo4j-password", default="")
    parser.add_argument("--json-path", default="data/bloodhound_export.json")
    parser.add_argument("--start", default=None)
    parser.add_argument("--goal", default=None)
    parser.add_argument("--model", default="output/ad_dqn_agent")
    parser.add_argument("--episodes", type=int, default=10)
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    graph, start, goal = get_graph(args)
    env = ADEnv(graph, start_node=start, goal_node=goal)

    baseline_path = bloodhound_shortest_path(graph, start, goal)
    baseline_techniques = []
    for i in range(len(baseline_path) - 1):
        src, dst = baseline_path[i], baseline_path[i + 1]
        if graph.has_edge(src, dst):
            baseline_techniques.append(graph.edges[src, dst].get("technique", "?"))

    agent_results = run_agent(args.model, env, episodes=args.episodes)

    success_rate = sum(1 for r in agent_results if r["reached_goal"]) / len(
        agent_results
    )
    avg_length = sum(
        r["path_length"] for r in agent_results if r["reached_goal"]
    ) / max(sum(1 for r in agent_results if r["reached_goal"]), 1)

    report = {
        "baseline": {
            "path": baseline_path,
            "path_length": len(baseline_path) - 1 if baseline_path else None,
            "techniques": baseline_techniques,
            "mitre": [MITRE_MAPPING.get(t, {}) for t in baseline_techniques],
        },
        "agent": {
            "success_rate": success_rate,
            "avg_path_length": avg_length,
            "episodes": agent_results,
        },
        "comparison": {
            "same_path_as_baseline": any(
                r["path"] == baseline_path for r in agent_results if r["reached_goal"]
            ),
            "baseline_length": len(baseline_path) - 1 if baseline_path else None,
            "agent_avg_length": avg_length,
        },
    }

    report_path = output_dir / "benchmark_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("\n=== BENCHMARK RESULTS ===")
    print(f"BloodHound baseline path: {' -> '.join(baseline_path) or 'NO PATH'}")
    print(f"Baseline length: {report['comparison']['baseline_length']}")
    print(f"Baseline techniques: {baseline_techniques}")
    print(f"\nAgent success rate: {success_rate:.0%}")
    print(f"Agent avg path length: {avg_length:.1f}")
    print(f"Same path as baseline: {report['comparison']['same_path_as_baseline']}")

    if agent_results:
        best = next((r for r in agent_results if r["reached_goal"]), agent_results[0])
        print(f"\nSample agent path: {' -> '.join(best['path'])}")
        print(f"Techniques: {best['techniques']}")

    print(f"\nFull report saved to {report_path}")


if __name__ == "__main__":
    main()
