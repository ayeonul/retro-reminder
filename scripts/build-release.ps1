param(
    [switch]$SkipFrontendBuild
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

if (-not $SkipFrontendBuild) {
    npm.cmd --prefix frontend run build
}

conda run -n reminder pyinstaller --noconfirm --clean --windowed --name Reminder --paths backend --icon backend\assets\reminder-icon.ico --add-data "frontend\dist;frontend\dist" --add-data "backend\assets;assets" backend\desktop.py

Write-Host "빌드 완료: $ProjectRoot\dist\Reminder\Reminder.exe"
