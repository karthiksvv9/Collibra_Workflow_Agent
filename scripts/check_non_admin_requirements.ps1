param(
    [int]$Port = 8088
)

$ErrorActionPreference = "Continue"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

function Test-CommandAvailable {
    param([string]$Name)
    $command = Get-Command $Name -ErrorAction SilentlyContinue
    [pscustomobject]@{
        Name = $Name
        Found = [bool]$command
        Path = if ($command) { $command.Source } else { "" }
    }
}

function Find-Java {
    $command = Get-Command "java" -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }
    $roots = @(
        $env:ProgramFiles,
        ${env:ProgramFiles(x86)}
    ) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    $patterns = @(
        "Java\*\bin\java.exe",
        "Eclipse Adoptium\*\bin\java.exe",
        "Microsoft\jdk*\bin\java.exe",
        "JetBrains\*\jbr\bin\java.exe"
    )
    foreach ($root in $roots) {
        foreach ($pattern in $patterns) {
            $candidate = Get-ChildItem -Path (Join-Path $root $pattern) -File -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($candidate) {
                return $candidate.FullName
            }
        }
    }
    if ($env:JAVA_HOME) {
        $candidate = Join-Path $env:JAVA_HOME "bin\java.exe"
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }
    return ""
}

function Write-Check {
    param([string]$Name, [bool]$Ok, [string]$Detail)
    $color = if ($Ok) { "Green" } else { "Yellow" }
    $status = if ($Ok) { "OK" } else { "ACTION" }
    Write-Host ("[{0}] {1}: {2}" -f $status, $Name, $Detail) -ForegroundColor $color
}

Write-Host "DSC Collibra Workflow Agent non-admin requirements check" -ForegroundColor Cyan
Write-Host "Project: $ProjectRoot"
Write-Host ""

$python = Test-CommandAvailable "python"
$node = Test-CommandAvailable "node"
$npm = Test-CommandAvailable "npm"
$javaPath = Find-Java

Write-Check "Python" $python.Found $python.Path
Write-Check "Node.js" $node.Found $node.Path
Write-Check "npm" $npm.Found $npm.Path
Write-Check "Java" (-not [string]::IsNullOrWhiteSpace($javaPath)) $javaPath

$canWrite = $true
try {
    $probe = Join-Path $ProjectRoot "output\\.write_check"
    New-Item -ItemType Directory -Path (Split-Path -Parent $probe) -Force | Out-Null
    "ok" | Set-Content -Path $probe -Encoding UTF8
    Remove-Item -LiteralPath $probe -Force
} catch {
    $canWrite = $false
}
Write-Check "Workspace write access" $canWrite "Needed for .venv, src/ui/dist, output, and RAG vector store."

$portInUse = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
Write-Check "Port $Port" (-not $portInUse) $(if ($portInUse) { "Already used by PID $($portInUse.OwningProcess)" } else { "Available" })

$jarCount = @(Get-ChildItem -Path (Join-Path $ProjectRoot "jars") -Filter "*.jar" -ErrorAction SilentlyContinue).Count
Write-Check "JAR folder" ($jarCount -gt 0) "$jarCount jar file(s) found under jars."

$apiKeyPresent = -not [string]::IsNullOrWhiteSpace($env:MERCK_API_KEY)
Write-Check "MERCK_API_KEY" $apiKeyPresent "Set in current user/session environment or enter it when start script prompts."

Write-Host ""
Write-Host "This check does not require administrator permissions." -ForegroundColor Cyan
