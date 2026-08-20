# 10-Day Execution Checklist

Tick off as you complete each milestone.

## Days 1–2: Foundation
- [ ] **A:** VirtualBox/Hyper-V installed
- [ ] **A:** DC VM created, promoted to corp.local (`lab/01-install-dc.ps1`)
- [ ] **A:** 2 workstation VMs domain-joined
- [ ] **A:** Users created (`lab/02-create-users.ps1`)
- [ ] **A:** Misconfigs planted (`lab/03-plant-misconfigs.ps1`)
- [ ] **A:** Snapshots taken on all 3 VMs
- [ ] **B:** Python deps installed (`pip install -r requirements.txt`)
- [ ] **B:** Mock graph env works (`python scripts/test_env.py`)

## Day 3: BloodHound
- [ ] **A:** SharpHound downloaded to workstation
- [ ] **A:** `SharpHound.exe -c All` run, zip collected
- [ ] **A:** BloodHound + Neo4j installed on host
- [ ] **A:** Data ingested, "Shortest Paths to Domain Admins" confirmed
- [ ] **A:** Screenshot saved for report
- [ ] **A:** Neo4j credentials OR JSON export shared with B

## Day 4: Integration
- [ ] **Both:** Real graph loaded (`python scripts/train.py --source neo4j ...`)
- [ ] **Both:** env.reset() and env.step() work on real graph

## Days 5–6: Training
- [ ] **B:** DQN trained 20k timesteps (`python scripts/train.py`)
- [ ] **B:** training_curve.png shows upward trend
- [ ] **B:** ad_dqn_agent.zip saved
- [ ] **A:** Lab documented in report template
- [ ] **A:** MITRE draft started

## Day 7: Benchmark
- [ ] **Both:** `python scripts/benchmark.py` run
- [ ] **Both:** Agent vs BloodHound comparison filled into report

## Day 8: Polish
- [ ] **A:** MITRE table finalized
- [ ] **B:** Code cleaned up, model saved

## Days 9–10: Report & Submit
- [ ] **Both:** Report completed from `docs/REPORT_TEMPLATE.md`
- [ ] **Both:** Final proofread
- [ ] **Both:** Package: code + lab scripts + model + report + screenshots
