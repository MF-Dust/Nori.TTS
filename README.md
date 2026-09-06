<div align="center">

# Nori.TTS

**为 Nori 准备的本地语音合成服务，基于 Audio8 TTS 0.6B ONNX INT4。**

Windows 优先 · CPU 可运行 · 零样本音色克隆 · OpenAI 兼容 API · 流式输出

</div>

> 本仓库由 [Audio8 TTS](https://github.com/Edge0-AI/Audio8_TTS) 派生，保留上游模型与运行时实现，并增加了 Nori 专用的 Windows 启动、音色注册、测速和 API 使用流程。

## 当前方案

Nori.TTS 当前默认使用：

- Audio8 TTS Preview 0.6B
- ONNX Runtime CPUExecutionProvider
- Slow/Fast AR INT4 权重
- FP16 codec
- `nori` 作为默认音色名
- OpenAI 兼容接口 `/v1/audio/speech`
- NDJSON 流式接口 `/api/tts/stream`

仓库中的 0.1B Runtime 保留用于上游兼容与实验，但不作为 Nori 的默认运行方案。

## Windows 快速开始

需要 Python 3.11 或更高版本。

```powershell
cd .\onnx_runtime
.\setup.ps1 -DownloadModel
```

`setup.ps1` 会创建独立的 `.venv`，安装 ONNX Runtime 依赖，并下载 `Audio8-TTS-Preview-0.6B-ONNX-INT4` 模型。

随后启动 Nori TTS：

```powershell
.\start_nori.ps1
```

默认服务地址：

```text
http://127.0.0.1:8024
```

浏览器打开该地址即可使用本地 Web UI。

## 内置 Nori 参考音频

Nori 的参考音频文件放在：

```text
onnx_runtime/api_nori.wav
```

对应的准确参考文本已经写入 Nori 注册脚本：

```text
这是用我训练好的专属模型合成的一段语音，验证API调用完全正常。
```

首次使用时，在服务已经启动的情况下执行：

```powershell
cd .\onnx_runtime
.\register_nori.ps1 -Audio .\api_nori.wav
```

注册成功后会在本地生成：

```text
onnx_runtime/voices/nori/
├─ codes.npy
└─ meta.json
```

`voices/` 不提交到仓库，因此换机器或清理本地数据后，可以直接使用仓库内的 `api_nori.wav` 再次注册。

如果需要覆盖已有的 Nori 音色：

```powershell
.\register_nori.ps1 -Audio .\api_nori.wav -Overwrite
```

## 生成 Nori 语音

最简单的方式：

```powershell
.\speak_nori.ps1 -Text "早上好，今天也要一起努力哦。"
```

默认输出到：

```text
onnx_runtime/outputs/nori.wav
```

也可以指定输出文件：

```powershell
.\speak_nori.ps1 `
  -Text "检测完成，目前系统运行状态正常。" `
  -Output ".\outputs\status.wav"
```

## API

### OpenAI 兼容接口

```http
POST /v1/audio/speech
```

请求示例：

```json
{
  "model": "nori-tts",
  "input": "早上好，今天也要一起努力哦。",
  "voice": "nori",
  "response_format": "wav"
}
```

PowerShell 示例：

```powershell
$body = @{
    model = "nori-tts"
    input = "早上好，今天也要一起努力哦。"
    voice = "nori"
    response_format = "wav"
} | ConvertTo-Json -Compress

Invoke-WebRequest `
  -Uri "http://127.0.0.1:8024/v1/audio/speech" `
  -Method POST `
  -ContentType "application/json; charset=utf-8" `
  -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) `
  -OutFile ".\outputs\nori.wav"
```

### 原生接口

完整 WAV：

```text
POST /api/tts
```

流式 PCM：

```text
POST /api/tts/stream
```

取消当前流：

```text
POST /api/tts/cancel
```

音色列表：

```text
GET /api/voices
```

注册音色：

```text
POST /api/voices/register
```

运行状态：

```text
GET /api/health
GET /api/system
```

FastAPI 的交互式 API 文档位于：

```text
http://127.0.0.1:8024/docs
```

## 流式性能测试

仓库附带 `benchmark_stream.py`，用于测量首个音频块延迟、总生成时间、音频长度和 RTF：

```powershell
.\.venv\Scripts\python.exe .\benchmark_stream.py `
  --text "早上好，今天也要一起努力哦。" `
  --voice nori `
  --output .\outputs\stream_test.wav
```

其中：

- TTFA 表示从发出请求到收到第一段音频的时间
- Total 表示整次生成完成的时间
- Audio duration 表示最终音频时长
- RTF = 总生成时间 / 音频时长，越低越好

对于桌面角色交互，TTFA 往往比完整 WAV 的生成时间更能反映实际体感。

## Windows 兼容层

`nori_server.py` 在尽量不修改上游核心 Runtime 的前提下提供 Nori 专用启动层，包括：

- Windows 下安全处理上游 macOS allocator helper
- 默认选择 `nori` 音色
- 预填 Nori 的参考文本
- 改善注册失败时的错误提示
- 为请求增加服务端耗时信息

这样可以降低未来同步 Audio8 上游更新时的冲突范围。

## 目录说明

```text
Nori.TTS/
├─ onnx_runtime/
│  ├─ api_nori.wav          # Nori 参考音频
│  ├─ nori_server.py        # Nori 专用服务入口
│  ├─ setup.ps1             # Windows 环境与模型安装
│  ├─ start_nori.ps1        # 启动服务
│  ├─ register_nori.ps1     # 注册 Nori 音色
│  ├─ speak_nori.ps1        # 快速生成语音
│  ├─ benchmark_stream.py   # 流式性能测试
│  ├─ model/                # 本地 ONNX 模型，不提交
│  ├─ voices/               # 本地音色 profile，不提交
│  └─ outputs/              # 生成结果，不提交
├─ NORI.md                  # 更详细的 Nori Runtime 文档
└─ README_zh.md             # 上游 Audio8 中文说明
```

## 上游 Audio8 TTS

Audio8 TTS Preview 是一个支持多语言语音生成和零样本音色克隆的 0.6B 参数 TTS 模型，采用 DualAR 架构，并提供 44.1 kHz 神经音频 codec。

推荐语言包括中文、粤语、英语、日语、韩语、法语、德语、意大利语、西班牙语、荷兰语和波兰语。

更多模型架构、训练、SFT、SGLang Omni 与评测信息可以查看：

- [Audio8 TTS upstream](https://github.com/Edge0-AI/Audio8_TTS)
- [上游中文说明](README_zh.md)
- [ONNX Runtime 文档](onnx_runtime/README_zh.md)

## 模型与仓库文件

ONNX 模型权重不直接提交到本仓库，`setup.ps1 -DownloadModel` 会从 Hugging Face 下载：

```text
Audio8/Audio8-TTS-Preview-0.6B-ONNX-INT4
```

本地生成的以下目录默认被 Git 忽略：

```text
onnx_runtime/model/
onnx_runtime/voices/
onnx_runtime/outputs/
```

## License

上游 Audio8 TTS 代码与模型使用 Apache License 2.0。请同时查看本仓库的 [LICENSE](LICENSE) 与 [NOTICE](NOTICE)。

使用音色克隆与生成语音时，请确保对参考音频拥有相应授权，并在适合的场景中说明音频为合成内容。
