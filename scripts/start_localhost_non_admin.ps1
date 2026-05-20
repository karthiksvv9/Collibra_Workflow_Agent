param(
    [int]$Port = 8088,
    [switch]$SkipInstall,
    [switch]$SkipNpmInstall,
    [switch]$SkipFrontendBuild,
    [switch]$NoBrowser,
    [switch]$NoApiKeyPrompt,
    [string]$ApiKeyEnv = "AI_GATEWAY_API_KEY"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$RunAll = Join-Path $ProjectRoot "run_all.ps1"
$ConfigPath = Join-Path $ProjectRoot "config.yaml"

function Get-YamlScalar {
    param(
        [string[]]$Lines,
        [string]$Section,
        [string]$Key
    )
    $inSection = $false
    foreach ($line in $Lines) {
        if ($line -match "^\s*$Section\s*:\s*$") {
            $inSection = $true
            continue
        }
        if ($inSection -and $line -match "^\S") {
            $inSection = $false
        }
        if ($inSection -and $line -match "^\s+$Key\s*:\s*(.*)$") {
            return ($Matches[1].Trim() -replace '^["'']|["'']$', '')
        }
    }
    return ""
}

function Test-SharedYamlApiKey {
    if (-not (Test-Path -LiteralPath $ConfigPath)) {
        return $false
    }
    $lines = Get-Content -LiteralPath $ConfigPath
    $modelsKey = Get-YamlScalar -Lines $lines -Section "models" -Key "api_key"
    $openaiKey = Get-YamlScalar -Lines $lines -Section "openai" -Key "api_key"
    return (-not [string]::IsNullOrWhiteSpace($modelsKey)) -or (-not [string]::IsNullOrWhiteSpace($openaiKey))
}

function Set-SessionApiKey {
    if ($NoApiKeyPrompt -or [string]::IsNullOrWhiteSpace($ApiKeyEnv)) {
        return
    }
    if (Test-SharedYamlApiKey) {
        Write-Host "Shared API key found in config.yaml. No command prompt key entry needed." -ForegroundColor Green
        return
    }
    $currentValue = [Environment]::GetEnvironmentVariable($ApiKeyEnv, "Process")
    if (-not [string]::IsNullOrWhiteSpace($currentValue)) {
        return
    }
    Write-Host "No shared API key was found in config.yaml and $ApiKeyEnv is not set." -ForegroundColor Yellow
    Write-Host "Paste the one enterprise API key. The app will reuse it for every model profile." -ForegroundColor Yellow
    Write-Host "It will only be stored in this PowerShell process and inherited by the localhost server." -ForegroundColor Yellow
    $secure = Read-Host $ApiKeyEnv -AsSecureString
    if ($secure.Length -eq 0) {
        return
    }
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    try {
        [Environment]::SetEnvironmentVariable($ApiKeyEnv, [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr), "Process")
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
