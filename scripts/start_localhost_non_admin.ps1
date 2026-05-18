param(
    [int]$Port = 8088,
    [switch]$SkipInstall,
    [switch]$SkipNpmInstall,
    [switch]$SkipFrontendBuild,
    [switch]$NoBrowser,
    [switch]$NoApiKeyPrompt
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$RunAll = Join-Path $ProjectRoot "run_all.ps1"

function Set-SessionApiKey {
    if ($NoApiKeyPrompt -or -not [string]::IsNullOrWhiteSpace($env:MERCK_API_KEY)) {
        return
    }
    Write-Host "MERCK_API_KEY is not set. Paste the API key from your approved gateway access." -ForegroundColor Yellow
    Write-Host "It will only be stored in this PowerShell process and inherited by the localhost server." -ForegroundColor Yellow
    $secure = Read-Host "MERCK_API_KEY" -AsSecureString
    if ($secure.Length -eq 0) {
        return
    }
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    try {
        $env:MERCK_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    } finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    }
}

Set-SessionApiKey

$arguments = @(
    "-ExecutionPolicy", "Bypass",
    "-File", $RunAll,
    "-Mode", "Serve",
    "-Port", "$Port",
    "-StopExisting"
)
if ($SkipInstall) { $arguments += "-SkipInstall" }
if ($SkipNpmInstall) { $arguments += "-SkipNpmInstall" }
if ($SkipFrontendBuild) { $arguments += "-SkipFrontendBuild" }
if ($NoBrowser) { $arguments += "-NoBrowser" }

Write-Host "Starting DSC Collibra Workflow Agent on http://127.0.0.1:$Port/ui/index.html" -ForegroundColor Cyan
& powershell @arguments
