# JAR Drop Zone

Place Collibra Java API v2 workflow/runtime JARs and any Groovy library dependencies here.

The Groovy compile loop reads `config.yaml > groovy.default_classpath` and expands `./jars/*`.
Keep this folder out of source control when it contains licensed Collibra artifacts.

## Java-Only Groovy Runtime

This workbench does not require a Groovy desktop/server installation. If `groovy.exe`
is unavailable, the compiler falls back to:

```text
java -cp ./jars/* org.codehaus.groovy.tools.FileSystemCompiler
```

Required open-source Apache Groovy runtime modules are downloaded from Maven Central:

- `org.apache.groovy:groovy`
- `org.apache.groovy:groovy-jsr223`
- `org.apache.groovy:groovy-json`
- `org.apache.groovy:groovy-xml`
- `org.apache.groovy:groovy-dateutil`
- `org.apache.groovy:groovy-nio`

Re-download them with:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\download_groovy_jars.ps1
```

The downloader writes `groovy-runtime-manifest.json` with source URLs and SHA-256
hashes. Collibra JARs are proprietary and must be supplied by the user or your
organization; they are not downloaded by the script.
