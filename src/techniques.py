"""Offensive technique definitions and BloodHound edge-type mapping."""

TECHNIQUES = [
    "Kerberoast",
    "WriteDacl",
    "UnconstrainedDelegation",
    "DCSync",
]

# Map BloodHound / Neo4j relationship types to our four action primitives.
BLOODHOUND_EDGE_MAP = {
    "Kerberoastable": "Kerberoast",
    "Kerberoast": "Kerberoast",
    "GenericWrite": "WriteDacl",
    "WriteDacl": "WriteDacl",
    "WriteOwner": "WriteDacl",
    "AddMember": "WriteDacl",
    "ForceChangePassword": "WriteDacl",
    "AllExtendedRights": "WriteDacl",
    "AllowedToDelegate": "UnconstrainedDelegation",
    "AllowedToAct": "UnconstrainedDelegation",
    "UnconstrainedDelegation": "UnconstrainedDelegation",
    "HasSession": "UnconstrainedDelegation",
    "AdminTo": "UnconstrainedDelegation",
    "CanDCSync": "DCSync",
    "DCSync": "DCSync",
    "GetChanges": "DCSync",
    "GetChangesAll": "DCSync",
    "MemberOf": "WriteDacl",
    "Contains": "WriteDacl",
}

MITRE_MAPPING = {
    "Kerberoast": {
        "id": "T1558.003",
        "tactic": "Credential Access",
        "name": "Kerberoasting",
    },
    "WriteDacl": {
        "id": "T1222",
        "tactic": "Defense Evasion / Privilege Escalation",
        "name": "ACL Abuse",
    },
    "UnconstrainedDelegation": {
        "id": "T1550 / T1187",
        "tactic": "Lateral Movement",
        "name": "Unconstrained Delegation",
    },
    "DCSync": {"id": "T1003.006", "tactic": "Credential Access", "name": "DCSync"},
}


def map_edge_type(rel_type: str) -> str | None:
    """Return the action primitive for a BloodHound edge, or None if unmappable."""
    if rel_type in BLOODHOUND_EDGE_MAP:
        return BLOODHOUND_EDGE_MAP[rel_type]
    for key, value in BLOODHOUND_EDGE_MAP.items():
        if key.lower() in rel_type.lower():
            return value
    return None
