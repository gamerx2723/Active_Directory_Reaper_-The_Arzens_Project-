"""Gymnasium environment for AD privilege escalation on a NetworkX attack graph."""

from __future__ import annotations

import gymnasium as gym
import networkx as nx
from gymnasium import spaces

from .techniques import TECHNIQUES


class ADEnv(gym.Env):
    """
    State: index of the currently compromised node.
    Action: one of four offensive primitives (TECHNIQUES).
    Reward: -1 per step, +100 on reaching goal, -5 for invalid technique at current node.
    """

    metadata = {"render_modes": ["human"]}

    def __init__(
        self,
        graph: nx.DiGraph,
        start_node: str = "user1",
        goal_node: str = "domain_admin",
        max_steps: int = 50,
    ):
        super().__init__()
        self.graph = graph
        self.nodes = sorted(graph.nodes())
        self.start_node = start_node
        self.goal_node = goal_node
        self.max_steps = max_steps

        if start_node not in self.nodes:
            raise ValueError(f"start_node '{start_node}' not in graph")
        if goal_node not in self.nodes:
            raise ValueError(f"goal_node '{goal_node}' not in graph")

        self.action_space = spaces.Discrete(len(TECHNIQUES))
        self.observation_space = spaces.Discrete(len(self.nodes))

        self.current: str = start_node
        self.steps: int = 0
        self.last_technique: str | None = None
        self.path_history: list[str] = []

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current = self.start_node
        self.steps = 0
        self.last_technique = None
        self.path_history = [self.current]
        return self.nodes.index(self.current), {}

    def step(self, action: int):
        technique = TECHNIQUES[int(action)]
        self.steps += 1
        reward = -1
        moved = False

        for neighbor in self.graph.successors(self.current):
            edge_data = self.graph.edges[self.current, neighbor]
            edge_technique = edge_data.get("technique", "")
            if edge_technique == technique:
                self.current = neighbor
                self.last_technique = technique
                moved = True
                break

        terminated = self.current == self.goal_node
        if terminated:
            reward = 100
        elif not moved:
            reward = -5

        self.path_history.append(self.current)
        truncated = self.steps >= self.max_steps

        return (
            self.nodes.index(self.current),
            reward,
            terminated,
            truncated,
            {
                "technique": technique,
                "moved": moved,
                "current_node": self.current,
            },
        )

    def get_techniques_on_path(self) -> list[str]:
        """Return techniques used along path_history."""
        techniques = []
        for i in range(len(self.path_history) - 1):
            src, dst = self.path_history[i], self.path_history[i + 1]
            if self.graph.has_edge(src, dst):
                techniques.append(
                    self.graph.edges[src, dst].get("technique", "unknown")
                )
        return techniques

    def render(self):
        print(
            f"Step {self.steps} | Current: {self.current} | Path: {' -> '.join(self.path_history)}"
        )
