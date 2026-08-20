import json
import random
import os

def generate():
    random.seed(1337)
    nodes = []
    edges = []
    
    # Core nodes
    nodes.append({"id": "DOMAIN_ADMINS", "type": "Group", "name": "DOMAIN_ADMINS@CORP.LOCAL"})
    nodes.append({"id": "DC01", "type": "Computer", "name": "DC01.CORP.LOCAL"})
    nodes.append({"id": "SVC_SQL", "type": "User", "name": "SVC_SQL@CORP.LOCAL"})
    
    # 30 users
    for i in range(1, 31):
        nodes.append({"id": f"USER{i}", "type": "User", "name": f"USER{i}@CORP.LOCAL"})
        
    # 10 workstations
    for i in range(1, 11):
        nodes.append({"id": f"WS{i}", "type": "Computer", "name": f"WS{i}.CORP.LOCAL"})
        
    # Core attack path
    edges.append({"source": "USER1", "target": "SVC_SQL", "rel": "Kerberoast"})
    edges.append({"source": "SVC_SQL", "target": "WS1", "rel": "AllowedToDelegate"})
    edges.append({"source": "WS1", "target": "DC01", "rel": "CanDCSync"})
    edges.append({"source": "DC01", "target": "DOMAIN_ADMINS", "rel": "AddMember"})
    
    # Random noisy edges
    for i in range(1, 31):
        user = f"USER{i}"
        
        # User to workstation (AdminTo)
        if random.random() < 0.3:
            ws = f"WS{random.randint(1, 10)}"
            edges.append({"source": user, "target": ws, "rel": "AdminTo"})
            
        # User to user (ForceChangePassword)
        if random.random() < 0.2:
            target_user = f"USER{random.randint(1, 30)}"
            if user != target_user and target_user != "SVC_SQL":
                edges.append({"source": user, "target": target_user, "rel": "ForceChangePassword"})

    # Ensure EVERY node is connected to at least one other node
    all_node_ids = [n["id"] for n in nodes]
    for n in nodes:
        node_id = n["id"]
        # If node has no outgoing and no incoming edges
        if not any(e["source"] == node_id or e["target"] == node_id for e in edges):
            target = random.choice([x for x in all_node_ids if x != node_id])
            rel = random.choice(["AdminTo", "ForceChangePassword"])
            
            # 50/50 chance to be source or target
            if random.random() > 0.5:
                edges.append({"source": node_id, "target": target, "rel": rel})
            else:
                edges.append({"source": target, "target": node_id, "rel": rel})

    data = {"nodes": nodes, "edges": edges}
    
    os.makedirs("data", exist_ok=True)
    out_path = os.path.abspath("data/bloodhound_export.json")
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
        
    print(f"Generated massive graph with {len(nodes)} nodes and {len(edges)} edges at {out_path}")

if __name__ == "__main__":
    generate()
