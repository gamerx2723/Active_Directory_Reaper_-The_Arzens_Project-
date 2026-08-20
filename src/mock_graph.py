"""Synthetic AD attack graph for development before real BloodHound data arrives."""

import networkx as nx


def build_mock_graph() -> nx.DiGraph:
    """
    Minimal graph mirroring the three planted misconfigs from Module 1:
    Kerberoastable svc account, ACL abuse on Domain Admins, unconstrained delegation chain.
    """
    g = nx.DiGraph()

    nodes = [
        ("domain_admin", {"type": "Group", "privilege": 10}),
        ("domain_controller", {"type": "Computer", "privilege": 10}),
        ("svc_backup", {"type": "User", "privilege": 0}),
    ]
    # Add 30 users
    for i in range(1, 31):
        if i not in [1, 3]: # Don't duplicate core path users
            nodes.append((f"user{i}", {"type": "User", "privilege": 0}))
    nodes.append(("user1", {"type": "User", "privilege": 0}))
    nodes.append(("user3", {"type": "User", "privilege": 0}))
    
    # Add 10 workstations
    for i in range(1, 11):
        nodes.append((f"workstation{i}", {"type": "Computer", "privilege": 1}))

    g.add_nodes_from(nodes)

    # Core guaranteed attack path
    edges = [
        ("user1", "svc_backup", {"technique": "Kerberoast", "bloodhound_rel": "Kerberoastable"}),
        ("user3", "domain_admin", {"technique": "WriteDacl", "bloodhound_rel": "AddMember"}),
        ("svc_backup", "workstation1", {"technique": "UnconstrainedDelegation", "bloodhound_rel": "AllowedToDelegate"}),
        ("workstation1", "domain_controller", {"technique": "DCSync", "bloodhound_rel": "CanDCSync"}),
        ("domain_controller", "domain_admin", {"technique": "WriteDacl", "bloodhound_rel": "MemberOf"}),
    ]

    # Add random noisy connections mapped to valid techniques
    import random
    random.seed(42)
    for i in range(1, 31):
        # AdminTo workstation (Lateral Movement via Delegation)
        if random.random() < 0.4:
            target_ws = f"workstation{random.randint(1, 10)}"
            edges.append((f"user{i}", target_ws, {"technique": "UnconstrainedDelegation", "bloodhound_rel": "AdminTo"}))
        
        # User-to-User ACL abuse
        if random.random() < 0.2:
            target_user = f"user{random.randint(1, 30)}"
            if target_user != f"user{i}" and target_user not in ["user1", "user3", "svc_backup"]:
                edges.append((f"user{i}", target_user, {"technique": "WriteDacl", "bloodhound_rel": "ForceChangePassword"}))

    # Ensure EVERY node is connected to at least one other node
    all_node_names = [n[0] for n in nodes]
    for n in nodes:
        node_name = n[0]
        # If node has no outgoing and no incoming edges
        if not any(e[0] == node_name or e[1] == node_name for e in edges):
            target = random.choice([x for x in all_node_names if x != node_name])
            technique = random.choice([
                {"technique": "UnconstrainedDelegation", "bloodhound_rel": "AdminTo"},
                {"technique": "WriteDacl", "bloodhound_rel": "ForceChangePassword"}
            ])
            
            # 50/50 chance to be source or target
            if random.random() > 0.5:
                edges.append((node_name, target, technique))
            else:
                edges.append((target, node_name, technique))

    g.add_edges_from(edges)

    return g


def bloodhound_shortest_path(g: nx.DiGraph, start: str, goal: str) -> list[str]:
    """Return the shortest node path (BloodHound-style baseline)."""
    try:
        return nx.shortest_path(g, start, goal)
    except nx.NetworkXNoPath:
        return []
