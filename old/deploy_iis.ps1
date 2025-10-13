# ========================================
# GTIN Scanner Live - IIS Deployment Script
# PowerShell script for IIS deployment
# ========================================

param(
    [string]$SiteName = "GTIN-Scanner",
    [string]$AppPoolName = "GTIN-Scanner-Pool",
    [string]$PhysicalPath = "C:\inetpub\wwwroot\gtin-scanner",
    [int]$Port = 80,
    [string]$HostName = ""
)

# Check administrator rights
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "[ERROR] This script requires administrator rights!" -ForegroundColor Red
    Write-Host "Run PowerShell as Administrator" -ForegroundColor Yellow
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GTIN Scanner Live - IIS Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Import IIS module
Import-Module WebAdministration

# 1. Check HttpPlatformHandler
Write-Host "[1/10] Checking HttpPlatformHandler..." -ForegroundColor Yellow
$httpPlatformHandler = Get-WindowsFeature -Name Web-AppInit
if (-not $httpPlatformHandler.Installed) {
    Write-Host "[WARNING] HttpPlatformHandler not installed!" -ForegroundColor Yellow
    Write-Host "Download and install HttpPlatformHandler v2:" -ForegroundColor Yellow
    Write-Host "https://www.iis.net/downloads/microsoft/httpplatformhandler" -ForegroundColor Yellow
    $continue = Read-Host "Continue installation? (y/n)"
    if ($continue -ne "y") {
        exit 1
    }
}
Write-Host "[OK] HttpPlatformHandler checked" -ForegroundColor Green
Write-Host ""

# 2. Check Python
Write-Host "[2/10] Checking Python..." -ForegroundColor Yellow
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pythonPath) {
    Write-Host "[ERROR] Python not found in PATH!" -ForegroundColor Red
    Write-Host "Install Python 3.8+ and add to PATH" -ForegroundColor Yellow
    exit 1
}
Write-Host "[OK] Python found: $pythonPath" -ForegroundColor Green
Write-Host ""

# 3. Create physical directory
Write-Host "[3/10] Creating application directory..." -ForegroundColor Yellow
if (-not (Test-Path $PhysicalPath)) {
    New-Item -ItemType Directory -Path $PhysicalPath -Force | Out-Null
    Write-Host "[OK] Directory created: $PhysicalPath" -ForegroundColor Green
} else {
    Write-Host "[OK] Directory already exists: $PhysicalPath" -ForegroundColor Green
}
Write-Host ""

# 4. Copy application files
Write-Host "[4/10] Copying application files..." -ForegroundColor Yellow
$sourceFiles = @(
    "gtin_scanner_live.py",
    "gtin_scanner_live_iis.py",
    "web.config",
    "requirements.txt"
)

foreach ($file in $sourceFiles) {
    if (Test-Path $file) {
        Copy-Item $file -Destination $PhysicalPath -Force
        Write-Host "  - Copied: $file" -ForegroundColor Gray
    } else {
        Write-Host "  [WARNING] File not found: $file" -ForegroundColor Yellow
    }
}
Write-Host "[OK] Files copied" -ForegroundColor Green
Write-Host ""

# 5. Create Python virtual environment
Write-Host "[5/10] Creating Python virtual environment..." -ForegroundColor Yellow
$venvPath = Join-Path $PhysicalPath "venv"
if (-not (Test-Path $venvPath)) {
    & python -m venv $venvPath
    Write-Host "[OK] Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "[OK] Virtual environment already exists" -ForegroundColor Green
}
Write-Host ""

# 6. Install dependencies
Write-Host "[6/10] Installing Python dependencies..." -ForegroundColor Yellow
$pipPath = Join-Path $venvPath "Scripts\pip.exe"
$requirementsPath = Join-Path $PhysicalPath "requirements.txt"
& $pipPath install --upgrade pip
& $pipPath install -r $requirementsPath
Write-Host "[OK] Dependencies installed" -ForegroundColor Green
Write-Host ""

# 7. Create logs directory
Write-Host "[7/10] Creating logs directory..." -ForegroundColor Yellow
$logsPath = Join-Path $PhysicalPath "logs"
if (-not (Test-Path $logsPath)) {
    New-Item -ItemType Directory -Path $logsPath -Force | Out-Null
}
Write-Host "[OK] Logs directory created" -ForegroundColor Green
Write-Host ""

# 8. Create Application Pool
Write-Host "[8/10] Creating Application Pool..." -ForegroundColor Yellow
if (Test-Path "IIS:\AppPools\$AppPoolName") {
    Write-Host "[INFO] Application Pool already exists, removing old..." -ForegroundColor Yellow
    Remove-WebAppPool -Name $AppPoolName
}

New-WebAppPool -Name $AppPoolName
Set-ItemProperty "IIS:\AppPools\$AppPoolName" -Name managedRuntimeVersion -Value ""
Set-ItemProperty "IIS:\AppPools\$AppPoolName" -Name processModel.identityType -Value 4  # ApplicationPoolIdentity
Set-ItemProperty "IIS:\AppPools\$AppPoolName" -Name startMode -Value "AlwaysRunning"
Set-ItemProperty "IIS:\AppPools\$AppPoolName" -Name processModel.idleTimeout -Value "00:00:00"
Write-Host "[OK] Application Pool created: $AppPoolName" -ForegroundColor Green
Write-Host ""

# 9. Create or update website
Write-Host "[9/10] Creating IIS website..." -ForegroundColor Yellow
if (Test-Path "IIS:\Sites\$SiteName") {
    Write-Host "[INFO] Website already exists, removing old..." -ForegroundColor Yellow
    Remove-Website -Name $SiteName
}

if ($HostName -eq "") {
    New-Website -Name $SiteName -PhysicalPath $PhysicalPath -ApplicationPool $AppPoolName -Port $Port
} else {
    New-Website -Name $SiteName -PhysicalPath $PhysicalPath -ApplicationPool $AppPoolName -Port $Port -HostHeader $HostName
}

Write-Host "[OK] Website created: $SiteName" -ForegroundColor Green
Write-Host ""

# 10. Configure permissions
Write-Host "[10/10] Configuring permissions..." -ForegroundColor Yellow
$acl = Get-Acl $PhysicalPath
$identity = "IIS AppPool\$AppPoolName"
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule($identity, "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow")
$acl.SetAccessRule($accessRule)
Set-Acl $PhysicalPath $acl
Write-Host "[OK] Permissions configured" -ForegroundColor Green
Write-Host ""

# Restart website
Write-Host "Restarting website..." -ForegroundColor Yellow
Stop-Website -Name $SiteName -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Start-Website -Name $SiteName
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[SUCCESS] Deployment completed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Website: $SiteName" -ForegroundColor White
Write-Host "Application Pool: $AppPoolName" -ForegroundColor White
Write-Host "Physical path: $PhysicalPath" -ForegroundColor White
Write-Host "Port: $Port" -ForegroundColor White
if ($HostName -ne "") {
    Write-Host "Host: $HostName" -ForegroundColor White
    Write-Host "URL: http://${HostName}:${Port}" -ForegroundColor White
} else {
    Write-Host "URL: http://localhost:${Port}" -ForegroundColor White
}
Write-Host ""
Write-Host "Application logs: $logsPath" -ForegroundColor Yellow
Write-Host "Stdout logs: $logsPath\stdout.log" -ForegroundColor Yellow
Write-Host ""
Write-Host "To check status:" -ForegroundColor Cyan
Write-Host "  Get-Website -Name $SiteName" -ForegroundColor Gray
Write-Host "  Get-WebAppPoolState -Name $AppPoolName" -ForegroundColor Gray
Write-Host ""
