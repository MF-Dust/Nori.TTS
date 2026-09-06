from __future__ import annotations

import gc
import os
import time

from arktts_runtime import service


DEFAULT_VOICE = "nori"
NORI_REFERENCE_TEXT = (
    "这是用我训练好的专属模型合成的一段语音，验证API调用完全正常。"
)


def _patch_windows_allocator_release() -> None:
    """Keep Audio8's macOS allocator optimization from breaking on Windows."""
    if os.name != "nt":
        return

    def release_allocator_memory() -> None:
        gc.collect()

    service.release_allocator_memory = release_allocator_memory


def _patch_test_page() -> None:
    """Apply Nori defaults while keeping the upstream Audio8 test UI."""
    page = service.TEST_PAGE
    replacements = {
        "<title>Audio8 TTS 本地测试</title>": "<title>Nori TTS</title>",
        "<h1>Audio8 TTS</h1>": "<h1>Nori TTS</h1>",
        "你好，这是 Audio8 TTS 的本地语音合成测试。": "你好，我是 Nori。今天也请多关照。",
        'download="audio8_output.wav"': 'download="nori_output.wav"',
        'placeholder="speaker_a"': 'value="nori" placeholder="nori"',
        '<textarea id="referenceText" class="register-text"></textarea>': (
            '<textarea id="referenceText" class="register-text">'
            + NORI_REFERENCE_TEXT
            + "</textarea>"
        ),
        "if (selected && names.includes(selected)) $('voice').value = selected;": (
            "if (selected && names.includes(selected)) $('voice').value = selected; "
            "else if (names.includes('nori')) $('voice').value = 'nori';"
        ),
        "if (!response.ok) throw new Error((await response.json()).detail || `HTTP ${response.status}`);": (
            "if (!response.ok) { const raw = await response.text(); let message = raw; "
            "try { message = JSON.parse(raw).detail || raw; } catch (_) {} "
            "throw new Error(message || `HTTP ${response.status}`); }"
        ),
    }
    for old, new in replacements.items():
        page = page.replace(old, new)
    service.TEST_PAGE = page


_patch_windows_allocator_release()
_patch_test_page()

service.app.title = "Nori TTS"
service.app.description = (
    "Nori local TTS service based on the Audio8 0.6B INT4 ONNX runtime."
)


@service.app.get("/api/nori/info")
def nori_info() -> dict[str, str | int]:
    return {
        "service": "Nori TTS",
        "default_voice": DEFAULT_VOICE,
        "runtime": "Audio8 0.6B INT4 ONNX",
        "threads": service.THREADS,
    }


@service.app.middleware("http")
async def add_nori_timing_header(request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - started
    response.headers["X-Nori-TTS-Elapsed"] = f"{elapsed:.6f}"
    response.headers["Server-Timing"] = f"nori;dur={elapsed * 1000:.2f}"
    return response


app = service.app
