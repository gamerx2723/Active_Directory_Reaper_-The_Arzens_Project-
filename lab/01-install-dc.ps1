# Run on Windows Server VM BEFORE promotion (as Administrator)
# Installs AD DS and promotes to forest root: corp.local

$DomainName = "corp.local"
$NetBIOSName = "CORP"
$SafeModePassword = ConvertTo-SecureString "P@ssw0rd123!" -AsPlainText -Force

Write-Host "Installing AD Domain Services..."
Install-WindowsFeature -Name AD-Domain-Services -IncludeManagementTools

Write-Host "Promoting to Domain Controller..."
Install-ADDSForest `
    -DomainName $DomainName `
    -DomainNetbiosName $NetBIOSName `
    -SafeModeAdministratorPassword $SafeModePassword `
    -InstallDns:$true `
    -Force

Write-Host "DC promotion initiated. VM will reboot."
Write-Host "After reboot, log in as CORP\Administrator with password P@ssw0rd123!"
