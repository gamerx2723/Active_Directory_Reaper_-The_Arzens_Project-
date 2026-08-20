"""Train a DQN agent on the AD privilege escalation environment."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
from stable_baselines3 import DQN
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.monitor import Monitor

from src.ad_env import ADEnv
from src.graph_loader import load_graph_from_json, load_graph_from_neo4j
from src.mock_graph import build_mock_graph


class RewardLogger(BaseCallback):
    def __init__(self):
        super().__init__()
        self.episode_rewards: list[float] = []

    def _on_step(self) -> bool:
        infos = self.locals.get("infos", [])
        for info in infos:
            if info and "episode" in info:
                self.episode_rewards.append(info["episode"]["r"])
        return True


def get_graph(args) -> tuple:
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


def main():
    parser = argparse.ArgumentParser(
        description="Train DQN agent for AD privilege escalation"
    )
    parser.add_argument("--source", choices=["mock", "neo4j", "json"], default="mock")
    parser.add_argument("--neo4j-uri", default="bolt://localhost:7687")
    parser.add_argument("--neo4j-user", default="neo4j")
    parser.add_argument("--neo4j-password", default="")
    parser.add_argument("--json-path", default="data/bloodhound_export.json")
    parser.add_argument("--start", default=None, help="Starting compromised node")
    parser.add_argument("--goal", default=None, help="Goal node (Domain Admin group)")
    parser.add_argument("--timesteps", type=int, default=30000)
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    graph, start, goal = get_graph(args)
    print(f"Graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    print(f"Start: {start} | Goal: {goal}")

    env = Monitor(ADEnv(graph, start_node=start, goal_node=goal))
    callback = RewardLogger()

    model = DQN(
        "MlpPolicy",
        env,
        learning_rate=1e-3,
        buffer_size=20000,
        learning_starts=500,
        batch_size=64,
        exploration_fraction=0.3,
        target_update_interval=500,
        verbose=1,
    )

    model.learn(total_timesteps=args.timesteps, callback=callback)
    model_path = output_dir / "ad_dqn_agent"
    model.save(str(model_path))
    print(f"Model saved to {model_path}.zip")

    if callback.episode_rewards:
        import json
        metrics_data = {
            "episodes": list(range(1, len(callback.episode_rewards) + 1)),
            "rewards": callback.episode_rewards
        }
        with open(output_dir / "metrics.json", "w") as f:
            json.dump(metrics_data, f)

        plt.figure(figsize=(10, 5))
        plt.plot(callback.episode_rewards)
        plt.xlabel("Episode")
        plt.ylabel("Reward")
        plt.title("DQN Training Progress")
        plt.grid(True, alpha=0.3)
        curve_path = output_dir / "training_curve.png"
        plt.savefig(curve_path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"Training curve saved to {curve_path}")
    else:
        rewards = env.get_episode_rewards()
        if rewards:
            plt.figure(figsize=(10, 5))
            plt.plot(rewards)
            plt.xlabel("Episode")
            plt.ylabel("Reward")
            plt.title("DQN Training Progress")
            plt.savefig(output_dir / "training_curve.png", dpi=150)
            plt.close()


if __name__ == "__main__":
    main()
