$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$CompilerPaths = @(
    "C:\Program Files\Inno Setup 7\ISCC.exe",
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)
$CompilerPath = $CompilerPaths | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $CompilerPath) {
    throw "Inno Setup Compiler(ISCC.exe)를 찾지 못했습니다. Inno Setup을 설치한 뒤 다시 실행하세요."
}

& $CompilerPath (Join-Path $ProjectRoot "installer\Reminder.iss")

Write-Host "설치 파일 생성 완료: $ProjectRoot\release\Reminder-Setup-0.1.0.exe"
