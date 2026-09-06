param(
    [switch]$DownloadModel
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

function Resolve-Python {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        try {
            & py -3.11 -c "import sys; assert sys.version_info >= (3, 11)" 2>$null
            if ($LASTEXITCODE -eq 0) {
                return @{ Command = "py"; Prefix = @("-3.11") }
            }
        } catch {}
    }

    if (Get-Command python -ErrorAction SilentlyContinue) {
        & python -c "import sys; assert sys.version_info >= (3, 11)"
        if ($LASTEXITCODE -eq 0) {
            return @{ Command = "python"; Prefix = @() }
        }
    }

    throw "Python 3.11 or newer was not found."
}

$Python = Resolve-Python
$VenvArgs = @($Python.Prefix) + @("-m", "venv", ".venv")

Write-Host "Creating Nori TTS environment..."
& $Python.Command @VenvArgs
if ($LASTEXITCODE -ne 0) {
    throw "Failed to create the virtual environment."
}

$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"
& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r requirements.txt
& $VenvPython -m pip install --no-deps tokenizers==0.22.2

if ($DownloadModel) {
    & $VenvPython -m pip install -U "huggingface_hub[cli]"
    $Hf = Join-Path $Root ".venv\Scripts\hf.exe"
    if (-not (Test-Path $Hf)) {
        throw "hf.exe was not installed into the virtual environment."
    }
    Write-Host "Downloading Audio8 0.6B INT4 ONNX model..."
    & $Hf download Audio8/Audio8-TTS-Preview-0.6B-ONNX-INT4 --local-dir model
    if ($LASTEXITCODE -ne 0) {
        throw "Model download failed."
    }
}

Write-Host ""
Write-Host "Nori TTS environment is ready: $Root\.venv"
if (-not $DownloadModel) {
    Write-Host "Model download was skipped. Re-run with -DownloadModel when needed."
}
