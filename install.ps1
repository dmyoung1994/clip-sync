# clip-sync installer (PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "=== clip-sync Installer ===" -ForegroundColor Cyan

# 1. Check for Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
}

if (-not $python) {
    Write-Host "Error: Python is not installed. Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Found $($python.Source)" -ForegroundColor Green

# 2. Check for Pip
try {
    & $python.Source -m pip --version | Out-Null
    Write-Host "✅ Found pip" -ForegroundColor Green
} catch {
    Write-Host "Error: pip is not installed for $($python.Name)." -ForegroundColor Red
    exit 1
}

# 3. Check for Git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Error: git is not installed. You need git to install from GitHub." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Found git" -ForegroundColor Green

# 4. Install the package
Write-Host "Installing clip-sync..." -ForegroundColor Cyan
& $python.Source -m pip install git+https://github.com/dmyoung1994/clip-sync.git

if ($?) {
    Write-Host "`n✨ Success! clip-sync is installed." -ForegroundColor Green
    Write-Host "Usage: clip-sync --hub http://your-ip:8081" -ForegroundColor Cyan
} else {
    Write-Host "`n❌ Installation failed." -ForegroundColor Red
    exit 1
}
