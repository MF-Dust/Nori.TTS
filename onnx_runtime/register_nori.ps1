param(
    [Parameter(Mandatory = $true)]
    [string]$Audio,
    [string]$BaseUrl = "http://127.0.0.1:8024",
    [switch]$Overwrite
)

$ErrorActionPreference = "Stop"
$AudioPath = (Resolve-Path $Audio).Path
$ReferenceText = "这是用我训练好的专属模型合成的一段语音，验证API调用完全正常。"

$Form = @{
    audio = Get-Item $AudioPath
    text = $ReferenceText
    name = "nori"
    overwrite = $(if ($Overwrite) { "true" } else { "false" })
}

Write-Host "Registering Nori voice from: $AudioPath"
$result = Invoke-RestMethod `
    -Uri "$BaseUrl/api/voices/register" `
    -Method Post `
    -Form $Form

$frames = $result.voice.shape[1]
Write-Host "Registered: $($result.voice.name) ($frames frames)"
$result
