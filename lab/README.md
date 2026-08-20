# ARZENS AD Lab Setup Scripts
# Run these on your Domain Controller (Windows Server) after promotion.
# Domain: corp.local

## Prerequisites
- Windows Server 2019/2022 evaluation ISO (DC)
- 2x Windows 10/11 evaluation ISOs (workstations)
- VirtualBox or Hyper-V
- Static IP on DC: 192.168.56.10 (adjust if needed)

## Quick Start Order
1. `01-install-dc.ps1` — on fresh Windows Server VM
2. Join workstations to corp.local
3. `02-create-users.ps1` — on DC
4. `03-plant-misconfigs.ps1` — on DC
5. Take VM snapshots on all 3 machines

## After Lab Is Ready (Day 3)
- Download SharpHound to a workstation
- Run: `SharpHound.exe -c All`
- Import zip into BloodHound + Neo4j on your host
- Provide Neo4j credentials OR export JSON for the RL scripts
