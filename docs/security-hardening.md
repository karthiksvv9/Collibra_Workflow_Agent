# Security Hardening Notes

This workbench is designed as a local-only engineering tool for Collibra workflow generation and validation.

## Secrets

- Do not commit API keys in `config.yaml`.
- Runtime API keys should come from `MERCK_API_KEY` or another approved environment variable.
- `scripts/start_localhost_non_admin.ps1` prompts for `MERCK_API_KEY` and keeps it only in the process environment.
- `.gitignore` excludes `.env`, `.env.*`, `config.local.yaml`, `secrets*.yaml`, JVM crash logs, heap dumps, and replay logs.

## Localhost Boundary

- The orchestrator binds the API to `127.0.0.1` by default.
- Do not change the host to `0.0.0.0` on an untrusted network unless you add authentication and TLS in front of the service.

## Upload Safety

- Uploads are size-limited.
- ZIP imports are checked for path traversal, maximum file count, and maximum member size.
- Uploaded filenames are normalized before being written to the RAG upload folder.
- ZIP members are read in memory for analysis only; they are not extracted to arbitrary filesystem paths.

## RAG And Generated Code

- Treat RAG documents as trusted internal training material. Do not ingest untrusted executable content.
- Groovy scripts are compiled locally for syntax and standards validation, but final workflow execution must be performed in a non-production Collibra tenant first.
- Temporary dependency stubs are used only for local syntax validation when tenant runtime JARs are not available. They are not packaged as real Collibra runtime dependencies.

## Git Publishing Checklist

- Search for leaked keys before publishing:

```powershell
rg -n "API_KEY|MERCK_API_KEY|X-Merck-APIKey|sk-|secret|password|token" .
```

- Confirm non-admin requirements:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_non_admin_requirements.ps1
```

- Run tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

- Run dependency checks. On corporate laptops, install the corporate root CA first; do not disable TLS verification to make an audit pass.

```powershell
.\.venv\Scripts\python.exe -m pip_audit -r requirements.txt
Set-Location src\ui
$env:NODE_OPTIONS="--use-system-ca"
npm audit --omit=dev
```

- Build UI:

```powershell
Set-Location src\ui
npm run build
```
