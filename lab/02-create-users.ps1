# Run on Domain Controller after promotion
# Creates 8 test users with password Passw0rd!

$Password = ConvertTo-SecureString "Passw0rd!" -AsPlainText -Force
$DomainDN = (Get-ADDomain).DistinguishedName

1..8 | ForEach-Object {
    $Name = "user$_"
    if (-not (Get-ADUser -Filter "SamAccountName -eq '$Name'" -ErrorAction SilentlyContinue)) {
        New-ADUser `
            -Name $Name `
            -SamAccountName $Name `
            -UserPrincipalName "$Name@corp.local" `
            -AccountPassword $Password `
            -Enabled $true `
            -PasswordNeverExpires $true
        Write-Host "Created $Name"
    } else {
        Write-Host "$Name already exists, skipping"
    }
}

# Service account for Kerberoasting
if (-not (Get-ADUser -Filter "SamAccountName -eq 'svc_backup'" -ErrorAction SilentlyContinue)) {
    New-ADUser `
        -Name "svc_backup" `
        -SamAccountName "svc_backup" `
        -UserPrincipalName "svc_backup@corp.local" `
        -AccountPassword $Password `
        -Enabled $true `
        -PasswordNeverExpires $true
    Write-Host "Created svc_backup"
}

Write-Host "Done. Users: user1-user8, svc_backup (password: Passw0rd!)"
