# Run on Domain Controller
# Plants the three misconfigurations from Module 1 of the playbook

Import-Module ActiveDirectory

Write-Host "=== (a) Kerberoastable service account ==="
Set-ADUser -Identity svc_backup -ServicePrincipalNames @{Add="MSSQLSvc/svc_backup.corp.local:1433"}
Write-Host "SPN added to svc_backup"

Write-Host "=== (b) Unconstrained delegation on workstation1 ==="
# Create workstation1 computer object if joining manually, or configure existing
$ComputerName = "workstation1"
try {
    Set-ADComputer -Identity $ComputerName -TrustedForDelegation $true
    Write-Host "Unconstrained delegation enabled on $ComputerName"
} catch {
    Write-Host "WARNING: $ComputerName not found. Enable delegation after joining the VM:"
    Write-Host "  AD Users & Computers -> $ComputerName -> Account -> Trust for delegation to any service"
}

Write-Host "=== (c) Bad ACL: user3 can add members to Domain Admins ==="
$TargetGroup = "Domain Admins"
$LowPrivUser = "user3"

# Grant GenericWrite / WriteProperty on the group
dsacls "CN=$TargetGroup,CN=Users,$((Get-ADDomain).DistinguishedName)" /G "CORP\$LowPrivUser:WP;member"

Write-Host "ACL granted: $LowPrivUser can WriteProperty 'member' on $TargetGroup"
Write-Host ""
Write-Host "Known attack path for BloodHound baseline:"
Write-Host "  user1 -> Kerberoast svc_backup -> UnconstrainedDelegation workstation1 -> DCSync Domain Admins"
Write-Host "  OR user3 -> WriteDacl/AddMember -> Domain Admins (direct)"
Write-Host ""
Write-Host "Take VM snapshots NOW on DC + both workstations."
