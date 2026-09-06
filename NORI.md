# Nori.TTS

Nori.TTS 是基于 Audio8 TTS 的下游运行配置，当前将 **0.6B INT4 ONNX Runtime** 作为 Nori 的默认本地 TTS 路线。

仓库保留上游 Audio8 TTS 的训练、推理与其他运行时实现；Nori 自己的 Windows 启动、音色注册和流式延迟测试集中放在 `onnx_runtime/` 中，尽量减少对上游核心代码的侵入，方便后续同步更新。

## 当前默认方案

- Runtime：Audio8 0.6B INT4 ONNX
- Execution Provider：ONNX Runtime CPU
- 默认音色名：`nori`
- 默认端口：`127.0.0.1:8024`
- OpenAI 兼容接口：`POST /v1/audio/speech`
- 流式接口：`POST /api/tts/stream`
- Windows：PowerShell 7 + Python 3.11+

0.1B runtime 仍随上游源码保留，但当前 Nori 部署不以它作为默认方案。

## Windows 快速开始

进入 0.6B ONNX Runtime：

```powershell
cd .\onnx_runtime
```

首次安装并下载模型：

```powershell
.\setup.ps1 -DownloadModel
```

启动 Nori TTS：

```powershell
.\start_nori.ps1
```

浏览器打开：

```text
http://127.0.0.1:8024
```

`nori_server.py` 会在 Windows 上绕开上游 `os.uname()` 导致的音色注册异常，同时保留上游 Audio8 服务、API 和流式实现。

## 注册 Nori 音色

Nori 当前使用的参考原文为：

```text
这是用我训练好的专属模型合成的一段语音，验证API调用完全正常。
```

网页里可以直接上传对应参考音频并注册为 `nori`。

PowerShell 也可以一条命令完成：

```powershell
.\register_nori.ps1 -Audio .\api_nori.wav
```

需要覆盖已有音色时：

```powershell
.\register_nori.ps1 -Audio .\api_nori.wav -Overwrite
```

生成后的音色 profile 存放在：

```text
onnx_runtime/voices/nori/
```

模型、音色 profile 和输出文件均已由仓库 `.gitignore` 排除，不会误提交权重或本地语音数据。

## 生成语音

```powershell
.\speak_nori.ps1 -Text "早上好，今天也要一起努力哦。"
```

默认输出：

```text
onnx_runtime/outputs/nori.wav
```

也可以直接调用 OpenAI 兼容接口：

```json
{
  "model": "arktts",
  "input": "早上好，今天也要一起努力哦。",
  "voice": "nori",
  "response_format": "wav"
}
```

## 流式延迟测试

完整生成耗时并不能代表 Nori 真正的开口延迟。`benchmark_stream.py` 会同时测量首个音频块到达时间、总耗时、生成音频长度和 RTF。

```powershell
.\.venv\Scripts\python.exe .\benchmark_stream.py `
  --text "早上好，今天也要一起努力哦。" `
  --output .\outputs\stream_test.wav
```

输出示例：

```text
TTFA: 1.234 s
Total: 6.310 s
Audio: 1.040 s
RTF: 6.067
Codec frames: 23
```

其中：

- `TTFA`：从发送请求到首个音频块到达的时间
- `Total`：整个流式请求结束时间
- `Audio`：实际生成音频长度
- `RTF`：总生成耗时 / 音频时长

对 Nori Desktop 来说，TTFA 比完整生成时间更接近用户感受到的响应速度。

## 上游与许可

Nori.TTS 基于 Audio8 TTS，保留原项目的 `LICENSE` 与 `NOTICE`。上游代码和模型权重采用 Apache License 2.0。

本仓库不会提交 Nori 的参考音频、已注册 voice profile 或模型权重；这些资源应单独管理。
