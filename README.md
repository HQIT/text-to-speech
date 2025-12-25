# text-to-speech

文本转语音工具，支持命令行和 Python API。

## 功能特性

- 支持文本转语音
- 支持多种说话人
- 流式输出支持
- 命令行工具和 Python API 两种使用方式
- **Provider 抽象层**，可扩展支持不同 TTS 服务

## 安装

### 从源码安装

```bash
cd text-to-speech
pip install -e .
```

### 使用 pip 安装

```bash
pip install text-to-speech
```

## 配置

设置环境变量（可选）：

```bash
export TTS_URL="http://your-tts-server:8002/tts_stream"
export TTS_SPK_ID="xiaoyan"
```

或创建 `.env` 文件：

```
TTS_URL=http://your-tts-server:8002/tts_stream
TTS_SPK_ID=xiaoyan
```

## 命令行使用

### 基本用法

```bash
# 直接输入文本
text-to-speech "你好世界" -o output.wav

# 从文件读取文本
text-to-speech -i input.txt -o output.wav
```

### 选项

```bash
# 指定说话人
text-to-speech "你好世界" -o output.wav --spk-id female

# 指定 TTS 服务 URL
text-to-speech "你好世界" -o output.wav --tts-url http://localhost:8002/tts_stream

# 详细输出
text-to-speech "你好世界" -o output.wav -v
```

### 命令行参数

| 参数 | 说明 |
|------|------|
| `text` | 要转换的文本内容 |
| `-i, --input` | 输入文本文件路径 |
| `-o, --output` | 输出音频文件路径（必需） |
| `--spk-id` | 说话人 ID（默认 xiaoyan） |
| `--tts-url` | TTS 服务 URL |
| `-v, --verbose` | 详细输出 |
| `--version` | 显示版本号 |

## Python API

### 基本用法

```python
from text_to_speech import TTSClient

# 创建客户端
client = TTSClient(content="你好世界", spk_id="xiaoyan")

# 转换并保存
audio = client.convert(output_path="output.wav")
```

### 使用自定义 Provider

```python
from text_to_speech import TTSClient, StreamTTSProvider

# 创建自定义 provider
provider = StreamTTSProvider(url="http://custom-server:8002/tts")

# 使用 provider 创建客户端
client = TTSClient(content="你好世界", provider=provider)
audio = client.convert(output_path="output.wav")
```

### 使用回调函数

```python
from text_to_speech import TTSClient, TTSResult

def on_progress(result: TTSResult):
    if result.type == 0:
        print(f"Processing: received {len(result.audio)} bytes")
    elif result.type == 1:
        print("Completed!")
    else:
        print(f"Error: {result.message}")

client = TTSClient(
    content="你好世界",
    spk_id="xiaoyan",
    callback=on_progress
)
client.start()
```

### 便捷函数

```python
from text_to_speech import text_to_speech

# 一行代码完成转换
audio = text_to_speech("你好世界", output_path="output.wav")
```

## 扩展 TTS 服务

通过实现 `TTSProvider` 基类，可以添加新的 TTS 服务支持：

```python
from text_to_speech.providers import TTSProvider
from typing import Iterator

class MyTTSProvider(TTSProvider):
    def __init__(self, api_key: str, ...):
        self.api_key = api_key
    
    def synthesize(self, text: str, spk_id: str) -> Iterator[bytes]:
        # 实现你的 TTS 服务调用逻辑
        # 返回音频数据流
        ...
        yield audio_chunk

# 使用自定义 provider
provider = MyTTSProvider(api_key="xxx")
client = TTSClient(content="你好", provider=provider)
```

## API 参考

### TTSClient

```python
TTSClient(
    content: str,              # 要转换的文本
    spk_id: str = "xiaoyan",   # 说话人 ID
    callback: Callable = None, # 进度回调
    provider: TTSProvider = None, # TTS 服务提供者
    tts_url: str = None        # TTS 服务 URL（向后兼容）
)
```

### TTSResult

```python
@dataclass
class TTSResult:
    type: int       # 0=处理中, 1=完成, -1=错误
    message: str    # 错误消息
    audio: bytes    # 音频数据
    process: int    # 处理进度
```

### TTSProvider

```python
class TTSProvider(ABC):
    @abstractmethod
    def synthesize(self, text: str, spk_id: str) -> Iterator[bytes]:
        """将文本转换为语音，返回音频数据流"""
        pass
```

## 作为模块运行

```bash
python -m text_to_speech "你好世界" -o output.wav
```

## License

MIT License
