param(
    [int]$Threads = 5,
    [int]$Port = 8024,
    [string]$ListenHost = "127.0.0.1"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw "Virtual environment was not found. Run .\setup.ps1 first."
}
if (-not (Test-Path (Join-Path $Root "model\runtime_manifest.json"))) {
    throw "Audio8 0.6B ONNX model was not found. Run .\setup.ps1 -DownloadModel or place the model in .\model."
}

$Voices = Join-Path $Root "voices"
New-Item -ItemType Directory -Force $Voices | Out-Null

$env:ARKTTS_MODEL_DIR = (Resolve-Path (Join-Path $Root "model")).Path
$env:ARKTTS_VOICES_DIR = (Resolve-Path $Voices).Path
$env:ARKTTS_REGISTRATION_DIR = Join-Path $env:ARKTTS_MODEL_DIR "registration"
$env:ARKTTS_PRECISION = "int4"
$env:ARKTTS_CODEC_PRECISION = "fp16"
$env:ARKTTS_THREADS = "$Threads"

Write-Host "Starting Nori TTS on http://$ListenHost`:$Port"
Write-Host "Threads: $Threads | Voice directory: $env:ARKTTS_VOICES_DIR"

& $Python -m uvicorn nori_server:app `
    --app-dir $Root `
    --host $ListenHost `
    --port $Port
