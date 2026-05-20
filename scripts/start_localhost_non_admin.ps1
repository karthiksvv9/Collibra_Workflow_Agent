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

function Set-SessionApiKey {
    if ($NoApiKeyPrompt -or [string]::IsNullOrWhiteSpace($ApiKeyEnv)) {
        return
    }
    $currentValue = [Environment]::GetEnvironmentVariable($ApiKeyEnv, "Process")
    if (-not [string]::IsNullOrWhiteSpace($currentValue)) {
        return
    }
    Write-Host "$ApiKeyEnv is not set. Paste the API key for the model profile you want to use." -ForegroundColor Yellow
    Write-Host "It will only be stored in this PowerShell process and inherited by the localhost server." -ForegroundColor Yellow
    Write-Host "For direct OpenAI use -ApiKeyEnv OPENAI_API_KEY. For Claude use -ApiKeyEnv CLAUDE_API_KEY. For Gemini use -ApiKeyEnv GEMINI_API_KEY." -ForegroundColor Yellow
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
