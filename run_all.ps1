param(
    [ValidateSet("All", "Setup", "Test", "Build", "Serve")]
    [string]$Mode = "All",

    [string]$Prompt = "Create a Collibra governed asset intake workflow with steward approval and optional relation creation.",
    [string]$OutputName = "generated_collibra_workflow",
    [int]$Port = 8088,

    [switch]$SkipInstall,
    [switch]$SkipNpmInstall,
    [switch]$SkipFrontendBuild,
    [switch]$SkipTests,
    [switch]$SkipSmokeBuild,
    [switch]$NoBrowser,
    [switch]$StopExisting
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $ProjectRoot ".venv"
$PythonExe = Join-Path $VenvDir "Scripts\python.exe"
$PipExe = Join-Path $VenvDir "Scripts\pip.exe"
$Activate = Join-Path $VenvDir "Scripts\Activate.ps1"
$ConfigPath = Join-Path $ProjectRoot "config.yaml"
$OutputDir = Join-Path $ProjectRoot "output"
$DocsDir = Join-Path $ProjectRoot "docs\rag_training"
$JarsDir = Join-Path $ProjectRoot "jars"
$UiDir = Join-Path $ProjectRoot "src\ui"

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Ensure-Directory {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path | Out-Null
    }
}

function Ensure-Venv {
    Write-Step "Preparing Python virtual environment"
    if (-not (Test-Path -LiteralPath $PythonExe)) {
        python -m venv $VenvDir
    }
    . $Activate
    & $PythonExe -m pip install --upgrade pip
    if (-not $SkipInstall) {
        & $PipExe install -r (Join-Path $ProjectRoot "requirements.txt")
    }
}

function Ensure-Frontend {
    if ($SkipFrontendBuild) {
        Write-Host "Skipping React frontend build." -ForegroundColor Yellow
        return
    }
    Write-Step "Preparing React workflow designer"
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        throw "npm was not found on PATH. Install Node.js or run with -SkipFrontendBuild."
    }
    Push-Location $UiDir
    try {
        $env:NODE_OPTIONS = "--use-system-ca"
        if ((-not $SkipNpmInstall) -and (-not (Test-Path -LiteralPath (Join-Path $UiDir "node_modules")))) {
            npm install --no-audit --no-fund
        } elseif ($SkipNpmInstall) {
            Write-Host "Skipping npm install." -ForegroundColor Yellow
        }
        npm run build
    } finally {
        Remove-Item Env:\NODE_OPTIONS -ErrorAction SilentlyContinue
        Pop-Location
    }
}

function Ensure-ProjectFolders {
    Write-Step "Checking project folders"
    Ensure-Directory $OutputDir
    Ensure-Directory $DocsDir
    Ensure-Directory $JarsDir

    if (-not (Test-Path -LiteralPath $ConfigPath)) {
        throw "Missing config.yaml at $ConfigPath"
    }

    $JarCount = @(Get-ChildItem -Path $JarsDir -Filter "*.jar" -ErrorAction SilentlyContinue).Count
    if ($JarCount -eq 0) {
        Write-Host "No Collibra/Groovy JARs found in $JarsDir. Groovy compile will fall back to static linting." -ForegroundColor Yellow
    } else {
        Write-Host "Found $JarCount JAR file(s) in $JarsDir." -ForegroundColor Green
    }

    if (-not (Get-Command groovy -ErrorAction SilentlyContinue)) {
        Write-Host "Groovy executable not found on PATH. Live Groovy syntax compilation will be skipped." -ForegroundColor Yellow
    } else {
        Write-Host "Groovy executable found." -ForegroundColor Green
    }
}

function Run-Tests {
    if ($SkipTests) {
        Write-Host "Skipping tests." -ForegroundColor Yellow
        return
    }
    Write-Step "Running test suite"
    Push-Location $ProjectRoot
    try {
        & $PythonExe -m pytest -q
        & $PythonExe -m compileall -q src tests
    } finally {
        Pop-Location
    }
}

function Run-SmokeBuild {
    if ($SkipSmokeBuild) {
        Write-Host "Skipping workflow smoke build." -ForegroundColor Yellow
        return
    }
    Write-Step "Running RAG ingest and workflow smoke build"
    Push-Location $ProjectRoot
    try {
        $env:DSC_MASTER_PROMPT = $Prompt
        $env:DSC_OUTPUT_NAME = $OutputName
        $env:PYTHONPATH = $ProjectRoot
        $SmokeScript = Join-Path $OutputDir "_run_smoke_build.py"
        @'
import os
from src.agents.workflow_agent import CollibraWorkflowAgent
from src.rag.engine import RAGEngine

def main() -> None:
    prompt = os.environ["DSC_MASTER_PROMPT"]
    output_name = os.environ["DSC_OUTPUT_NAME"]

    rag = RAGEngine()
    report = rag.ingest()
    print(f"RAG: documents={report.documents}, chunks={report.chunks}, relations={report.relations}, vectors={report.vector_count}")
    if report.warnings:
        for warning in report.warnings:
            print(f"RAG warning: {warning}")

    agent = CollibraWorkflowAgent(rag=rag)
    result = agent.build(prompt, output_name)
    print(f"Workflow package: {result.output_zip}")
    print(f"Validation errors: {result.package.validate()}")
    print(f"Simulation steps: {len(result.simulation.steps)}")
    for task_id, compile_result in result.compile_results.items():
        print(f"Groovy {task_id}: ok={compile_result.ok}, skipped={compile_result.skipped}")
        if compile_result.stderr:
            print(f"Groovy {task_id} note: {compile_result.stderr}")

if __name__ == "__main__":
    main()
'@ | Set-Content -Path $SmokeScript -Encoding UTF8
        & $PythonExe $SmokeScript
    } finally {
        if ($SmokeScript -and (Test-Path -LiteralPath $SmokeScript)) {
            Remove-Item -LiteralPath $SmokeScript -Force
        }
        Remove-Item Env:\DSC_MASTER_PROMPT -ErrorAction SilentlyContinue
        Remove-Item Env:\DSC_OUTPUT_NAME -ErrorAction SilentlyContinue
        Pop-Location
    }
}

function Stop-ExistingServer {
    $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($connection) {
        if ($StopExisting) {
            Write-Step "Stopping existing process on port $Port"
            Stop-Process -Id $connection.OwningProcess -Force
            Start-Sleep -Seconds 1
        } else {
            Write-Host "Port $Port is already in use by process $($connection.OwningProcess)." -ForegroundColor Yellow
            Write-Host "Use -StopExisting to stop it, or pass -Port <otherPort>."
            return $false
        }
    }
    return $true
}

function Start-Server {
    Write-Step "Starting DSC Collibra Workflow Agent server"
    if (-not (Stop-ExistingServer)) {
        return
    }

    $env:PYTHONPATH = $ProjectRoot

    $ServerLog = Join-Path $OutputDir "server.log"
    $ServerErr = Join-Path $OutputDir "server.err.log"
    $Arguments = @("-m", "uvicorn", "src.api.server:app", "--host", "127.0.0.1", "--port", "$Port")

    $Process = Start-Process `
        -FilePath $PythonExe `
        -ArgumentList $Arguments `
        -WorkingDirectory $ProjectRoot `
        -WindowStyle Hidden `
        -RedirectStandardOutput $ServerLog `
        -RedirectStandardError $ServerErr `
        -PassThru

    Start-Sleep -Seconds 3

    $Url = "http://127.0.0.1:$Port/ui/index.html"
    try {
        $Health = Invoke-RestMethod "http://127.0.0.1:$Port/" -TimeoutSec 8
        Write-Host "Server PID: $($Process.Id)" -ForegroundColor Green
        Write-Host "Health: $($Health.name)" -ForegroundColor Green
        Write-Host "Canvas: $Url" -ForegroundColor Green
        Write-Host "Logs: $ServerLog"
        Write-Host "Errors: $ServerErr"
        if (-not $NoBrowser) {
            Start-Process $Url
        }
    } catch {
        Write-Host "Server did not become healthy. Check logs:" -ForegroundColor Red
        Write-Host $ServerLog
        Write-Host $ServerErr
        throw
    }
}

Write-Host "DSC Collibra Workflow Automation Agent Orchestrator" -ForegroundColor Green
Write-Host "Project: $ProjectRoot"

Ensure-ProjectFolders
Ensure-Venv

switch ($Mode) {
    "Setup" {
        Ensure-Frontend
        Write-Host "Setup complete." -ForegroundColor Green
    }
    "Test" {
        Run-Tests
    }
    "Build" {
        Run-SmokeBuild
    }
    "Serve" {
        Ensure-Frontend
        Start-Server
    }
    "All" {
        Ensure-Frontend
        Run-Tests
        Run-SmokeBuild
        Start-Server
    }
}
