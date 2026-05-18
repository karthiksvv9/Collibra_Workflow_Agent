param(
  [string]$Version = "4.0.32",
  [string]$JarsDir = ".\jars"
)

$ErrorActionPreference = "Stop"

$modules = @(
  "groovy",
  "groovy-jsr223",
  "groovy-json",
  "groovy-xml",
  "groovy-dateutil",
  "groovy-nio"
)

$resolvedJarsDir = Resolve-Path $JarsDir -ErrorAction SilentlyContinue
if (-not $resolvedJarsDir) {
  New-Item -ItemType Directory -Force -Path $JarsDir | Out-Null
  $resolvedJarsDir = Resolve-Path $JarsDir
}

$manifest = @()
foreach ($module in $modules) {
  $base = "https://repo1.maven.org/maven2/org/apache/groovy/$module/$Version"
  $jar = "$module-$Version.jar"
  $url = "$base/$jar"
  $destination = Join-Path $resolvedJarsDir $jar

  Write-Host "Downloading $jar"
  Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $destination -TimeoutSec 120

  $expectedHash = (Invoke-WebRequest -UseBasicParsing -Uri "$url.sha256" -TimeoutSec 60).Content.Trim().Split(" ")[0]
  $actualHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $destination).Hash.ToLowerInvariant()
  if ($expectedHash -and ($expectedHash.ToLowerInvariant() -ne $actualHash)) {
    throw "SHA256 mismatch for $jar. Expected $expectedHash but got $actualHash."
  }

  $manifest += [pscustomobject]@{
    groupId = "org.apache.groovy"
    artifactId = $module
    version = $Version
    file = $jar
    url = $url
    sha256 = $actualHash
  }
}

$manifestPath = Join-Path $resolvedJarsDir "groovy-runtime-manifest.json"
$manifest | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 -LiteralPath $manifestPath
Write-Host "Wrote $manifestPath"
