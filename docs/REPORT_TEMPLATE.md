# Red Team Assessment Report — ARZENS RL Privilege Escalation PoC

**Prepared by:** gamerx & teammate  
**Date:** [FILL IN]  
**Scope:** Isolated local cyber range only — no external network engagement

---

## 1. Executive Summary

[Half page — plain language summary]

We built a minimal Active Directory lab with three deliberate misconfigurations (Kerberoastable service account, unconstrained delegation, ACL abuse on Domain Admins). We mapped the environment with BloodHound and trained a Deep Q-Network (DQN) reinforcement learning agent to discover privilege escalation paths on the resulting attack graph.

**Key findings:**
- BloodHound static shortest path length: [X] hops
- DQN agent success rate: [X]%
- Agent average path length: [X] hops
- Agent found [same / different] path compared to BloodHound baseline

This is a **small-scale proof-of-concept**, not the full 8-week enterprise vision. See Section 6 for honest scope limitations.

---

## 2. Methodology

### 2.1 Lab Topology

| VM | Role | OS | IP (example) |
|----|------|----|----|
| DC01 | Domain Controller | Windows Server 2019/2022 | 192.168.56.10 |
| WS01 | Workstation | Windows 10/11 | 192.168.56.11 |
| WS02 | Workstation | Windows 10/11 | 192.168.56.12 |

- **Domain:** corp.local
- **Users:** user1–user8, svc_backup (all password: Passw0rd!)

### 2.2 Planted Misconfigurations

| # | Misconfiguration | MITRE ATT&CK | BloodHound Edge |
|---|------------------|--------------|-----------------|
| a | SPN on svc_backup (Kerberoastable) | T1558.003 | Kerberoastable |
| b | Unconstrained delegation on workstation1 | T1550 / T1187 | AllowedToDelegate |
| c | user3 WriteProperty on Domain Admins | T1222 | AddMember / GenericWrite |

### 2.3 Graph Extraction

1. SharpHound `-c All` on domain-joined workstation
2. Imported zip into BloodHound Community Edition + Neo4j
3. Confirmed "Shortest Paths to Domain Admins" query
4. [Screenshot: attach BloodHound baseline path screenshot]

---

## 3. RL Framework Design

### 3.1 State Space
Index of the currently compromised node in the NetworkX attack graph.

### 3.2 Action Space (4 primitives)
| Action | Technique | Description |
|--------|-----------|-------------|
| 0 | Kerberoast | Extract service ticket hash from SPN account |
| 1 | WriteDacl | Abuse ACL to modify privileged group |
| 2 | UnconstrainedDelegation | Abuse delegation to impersonate |
| 3 | DCSync | Replicate domain credentials |

### 3.3 Reward Function
- **-1** per step (encourage short paths)
- **+100** on reaching Domain Admins
- **-5** for invalid technique at current node
- Episode truncated at 20 steps

### 3.4 Algorithm
DQN (Deep Q-Network) via Stable-Baselines3
- Learning rate: 1e-3
- Buffer size: 10,000
- Batch size: 32
- Total timesteps: 20,000

---

## 4. Results

### 4.1 Training Curve
[Insert: output/training_curve.png]

### 4.2 Benchmark Comparison

| Metric | BloodHound (static) | DQN Agent |
|--------|---------------------|-----------|
| Path length | [X] | [X] avg |
| Techniques used | [list] | [list] |
| Success rate | N/A (deterministic) | [X]% |
| Same path? | — | [Yes/No] |

**Agent sample path:** user1 → svc_backup → workstation1 → domain_admin  
**Baseline path:** [from BloodHound screenshot]

---

## 5. MITRE ATT&CK Mapping

| Technique Used | ATT&CK ID | Tactic |
|----------------|-----------|--------|
| Kerberoasting | T1558.003 | Credential Access |
| ACL Abuse (WriteDacl) | T1222 | Defense Evasion / Privilege Escalation |
| Unconstrained Delegation | T1550 / T1187 | Lateral Movement |
| DCSync | T1003.006 | Credential Access |

*Verify IDs against current MITRE ATT&CK Navigator before final submission.*

---

## 6. Honest Scope & Limitations

This 10-day proof-of-concept deliberately scoped down from the original 8-week proposal:

| Original Scope | What We Built |
|----------------|---------------|
| Full GOAD forest (4–6 VMs) | 1 DC + 2 workstations |
| DQN vs PPO comparison | DQN only |
| Large action space | 4 offensive primitives |
| Exhaustive benchmarking | Lightweight path-length comparison |

**How it extends:** A larger graph, more action primitives, and PPO/A3C algorithms could be evaluated on GOAD-scale forests. The Gymnasium environment is graph-agnostic and accepts real BloodHound Neo4j data.

---

## 7. Remediation Recommendations

1. **Kerberoasting:** Use gMSAs for service accounts; disable RC4; enforce strong service account passwords.
2. **Unconstrained delegation:** Replace with constrained delegation or resource-based constrained delegation; audit `TRUSTED_FOR_DELEGATION` flag.
3. **ACL abuse:** Regular BloodHound audits; remove unnecessary WriteProperty/GenericWrite on privileged groups; implement tiered admin model.

---

## Appendix: Deliverables Checklist

- [ ] Source code (`src/`, `scripts/`)
- [ ] Lab scripts (`lab/`)
- [ ] `output/training_curve.png`
- [ ] `output/ad_dqn_agent.zip`
- [ ] `output/benchmark_report.json`
- [ ] BloodHound baseline screenshot
- [ ] This report (PDF/DOCX)
