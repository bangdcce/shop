# setup-db.ps1: make the PostgreSQL user + databases match backend/.env
# Run from backend/:   powershell -ExecutionPolicy Bypass -File scripts\setup-db.ps1
# psql asks for the password of the superuser "postgres" (you type it, it is never stored).
# Safe to run many times: it creates what is missing and resets the app user's password to the one in .env.
param(
    [string]$EnvFile = ".env",
    [string]$Psql = "D:\postgres\bin\psql.exe",
    [string]$SuperUser = "postgres"
)
$ErrorActionPreference = "Stop"
$env:LC_MESSAGES = "C"   # psql messages in English (Windows would show them in its own language)

# 1. Read DATABASE_URL and TEST_DATABASE_URL from .env
$vars = @{}
foreach ($line in Get-Content $EnvFile) {
    if ($line -match '^\s*([A-Z_]+)\s*=\s*(.+?)\s*$') { $vars[$Matches[1]] = $Matches[2] }
}
$pattern = '^postgresql\+psycopg://([^:]+):([^@]+)@([^:/]+):(\d+)/(.+)$'
if ($vars["DATABASE_URL"] -notmatch $pattern) { throw "DATABASE_URL in $EnvFile does not look like postgresql+psycopg://user:password@host:port/db" }
$user = $Matches[1]; $password = $Matches[2]; $dbHost = $Matches[3]; $port = $Matches[4]; $devDb = $Matches[5]
if ($vars["TEST_DATABASE_URL"] -notmatch $pattern) { throw "TEST_DATABASE_URL in $EnvFile is missing or wrong" }
if ($Matches[1] -ne $user -or $Matches[2] -ne $password) { throw "DATABASE_URL and TEST_DATABASE_URL must use the same user and password" }
$testDb = $Matches[5]

# 2. SQL: create the user if missing, set its password, create the 2 databases if missing
$pw = $password.Replace("'", "''")
$sql = @"
SELECT format('CREATE USER %I', '$user') WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '$user')\gexec
ALTER USER "$user" WITH PASSWORD '$pw';
SELECT format('CREATE DATABASE %I OWNER %I', '$devDb', '$user') WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = '$devDb')\gexec
SELECT format('CREATE DATABASE %I OWNER %I', '$testDb', '$user') WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = '$testDb')\gexec
SELECT datname AS database, pg_get_userbyid(datdba) AS owner FROM pg_database WHERE datname IN ('$devDb', '$testDb') ORDER BY 1;
"@
$tmp = New-TemporaryFile
try {
    Set-Content -Path $tmp -Value $sql -Encoding ascii
    & $Psql -U $SuperUser -h $dbHost -p $port -d postgres -v ON_ERROR_STOP=1 -q -f $tmp
    if ($LASTEXITCODE -ne 0) { throw "psql failed (exit $LASTEXITCODE)" }
} finally {
    Remove-Item $tmp -ErrorAction SilentlyContinue   # the temp file held the password: delete it
}
Write-Host "OK: user '$user' now has the password from $EnvFile; databases $devDb and $testDb exist."
