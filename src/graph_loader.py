"""Load AD attack graphs from Neo4j (BloodHound) or JSON exports."""

from __future__ import annotations

import json
from pathlib import Path

import networkx as nx

from .techniques import map_edge_type


def load_graph_from_neo4j(uri: str, user: str, password: str) -> nx.DiGraph:
    """Query a running Neo4j instance populated by BloodHound."""
    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(uri, auth=(user, password))
    g = nx.DiGraph()

    query = """
    MATCH (n)-[r]->(m)
    RETURN coalesce(n.name, n.samaccountname, n.displayname, id(n)) AS src,
           type(r) AS rel,
           coalesce(m.name, m.samaccountname, m.displayname, id(m)) AS dst,
           labels(n) AS src_labels,
           labels(m) AS dst_labels
    """

    with driver.session() as session:
        result = session.run(query)
        for record in result:
            src = str(record["src"]).upper()
            dst = str(record["dst"]).upper()
            rel = record["rel"]
            technique = map_edge_type(rel)
            if technique is None:
                continue

            if not g.has_node(src):
                g.add_node(src, type=_label_to_type(record["src_labels"]))
            if not g.has_node(dst):
                g.add_node(dst, type=_label_to_type(record["dst_labels"]))

            g.add_edge(src, dst, technique=technique, bloodhound_rel=rel)

    driver.close()
    return g


def _label_to_type(labels) -> str:
    if not labels:
        return "Unknown"
    label_set = {l.lower() for l in labels}
    if "user" in label_set:
        return "User"
    if "computer" in label_set:
        return "Computer"
    if "group" in label_set:
        return "Group"
    if "domain" in label_set:
        return "Domain"
    return labels[0]


def load_graph_from_json(json_path: str | Path) -> nx.DiGraph:
    """
    Parse a BloodHound-style JSON export.
    Expects a list of {src, rel, dst} records or Neo4j-style node/relationship export.
    """
    path = Path(json_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    g = nx.DiGraph()

    if isinstance(data, list):
        for record in data:
            src = str(record.get("src") or record.get("source") or "").upper()
            dst = str(record.get("dst") or record.get("target") or "").upper()
            rel = (
                record.get("rel")
                or record.get("relationship")
                or record.get("edge_type")
                or record.get("type", "")
            )
            if not src or not dst:
                continue
            technique = map_edge_type(str(rel))
            if technique is None:
                continue
            g.add_edge(src, dst, technique=technique, bloodhound_rel=rel)

    elif isinstance(data, dict) and "edges" in data:
        for edge in data["edges"]:
            src = str(edge.get("source", edge.get("src", ""))).upper()
            dst = str(edge.get("target", edge.get("dst", ""))).upper()
            rel = edge.get("rel") or edge.get("type") or edge.get("edge_type") or ""
            technique = map_edge_type(str(rel))
            if technique is None:
                continue
            g.add_edge(src, dst, technique=technique, bloodhound_rel=rel)
            
        for node in data.get("nodes", []):
            node_id = str(node.get("id", "")).upper()
            if node_id and not g.has_node(node_id):
                g.add_node(node_id, **node)

    return g


def normalize_node_name(name: str, domain: str = "CORP.LOCAL") -> str:
    """Normalize BloodHound node names for start/goal lookup."""
    name = name.upper()
    if "@" in name:
        name = name.split("@")[0]
    if "." in name and domain.split(".")[0].upper() in name:
        return name
    return name


def auto_select_start_goal(
    graph: nx.DiGraph, preferred_start: str | None = None, preferred_goal: str | None = None
) -> tuple[str, str]:
    """Dynamically find a valid start and goal node in an arbitrary BloodHound graph."""
    nodes = list(graph.nodes())
    if not nodes:
        raise ValueError("Graph is empty, cannot select nodes.")

    goal = preferred_goal if (preferred_goal and graph.has_node(preferred_goal)) else None
    if not goal:
        # Prioritize 'DOMAIN ADMINS' group
        domain_admins = [n for n in nodes if "DOMAIN ADMIN" in str(n).upper()]
        if domain_admins:
            goal = domain_admins[0]
        else:
            # Fallback: Node with highest in-degree (likely an admin or highly privileged group)
            goal = sorted(nodes, key=lambda n: graph.in_degree(n), reverse=True)[0]

    start = preferred_start if (preferred_start and graph.has_node(preferred_start)) else None
    
    # If preferred start doesn't exist or has no path to goal, calculate a valid one
    if not start or not nx.has_path(graph, start, goal):
        valid_starts = [n for n in nodes if n != goal and nx.has_path(graph, n, goal)]
        
        if valid_starts:
            # Pick the starting node with the longest shortest path to make training meaningful
            start = max(valid_starts, key=lambda n: len(nx.shortest_path(graph, n, goal)))
        else:
            # If nothing can reach the goal, fallback to random node to avoid crash
            start = nodes[0] if nodes[0] != goal else (nodes[1] if len(nodes) > 1 else nodes[0])

    return start, goal
