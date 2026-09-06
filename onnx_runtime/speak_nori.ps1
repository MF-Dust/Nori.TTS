param(
    [Parameter(Mandatory = $true)]
    [string]$Text,
    [string]$Output = ".\outputs\nori.wav",
    [string]$BaseUrl = "http://127.0.0.1:8024"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$OutputPath = [System.IO.Path]::GetFullPath((Join-Path $Root $Output))
$OutputDir = Split-Path -Parent $OutputPath
New-Item -ItemType Directory -Force $OutputDir | Out-Null

$Body = @{
    model = "arktts"
    input = $Text
    voice = "nori"
    response_format = "wav"
} | ConvertTo-Json -Compress

$Bytes = [System.Text.Encoding]::UTF8.GetBytes($Body)
$Started = [System.Diagnostics.Stopwatch]::StartNew()
$response = Invoke-WebRequest `
    -Uri "$BaseUrl/v1/audio/speech" `
    -Method Post `
    -ContentType "application/json; charset=utf-8" `
    -Body $Bytes `
    -OutFile $OutputPath `
    -PassThru
$Started.Stop()

Write-Host "Saved: $OutputPath"
Write-Host ("Client elapsed: {0:N2} s" -f $Started.Elapsed.TotalSeconds)
if ($response.Headers["X-Nori-TTS-Elapsed"]) {
    Write-Host "Server elapsed: $($response.Headers['X-Nori-TTS-Elapsed']) s"
}
