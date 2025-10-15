# My Local Agent 🤖

一個使用 Ollama 本地 LLM 和 MCP 工具的 AI Agent，支援文件系統操作。

## ✨ 特色功能

- 🔧 **本地 LLM**: 使用 Ollama 運行本地語言模型
- 📁 **文件操作**: 讀取、寫入、列出、刪除文件和目錄
- 🐳 **Docker 支援**: 完整的 Docker Compose 配置
- ⚡ **現代工具**: 使用 uv 進行快速的 Python 包管理
- 🔒 **安全確認**: 危險操作需要用戶確認

## 🚀 快速開始

### 方式 1: Docker Compose（推薦）

```bash
# 啟動服務
docker-compose up -d

# 下載模型
docker-compose exec ollama ollama pull gpt-oss

# 運行 Agent
docker-compose run --rm agent
```

詳細說明請參閱 [DOCKER_SETUP.md](DOCKER_SETUP.md)

### 方式 2: 本地運行

**前置需求**:
- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Docker (用於運行 Ollama)

**步驟**:

```bash
# 1. 啟動 Ollama
docker run -d --gpus=all -v ollama:/root/.ollama \
  -p 11434:11434 --name ollama ollama/ollama

# 2. 下載模型
docker exec -it ollama ollama pull gpt-oss

# 3. 安裝依賴
uv sync

# 4. 運行 Agent
uv run src/main.py
```

詳細說明請參閱 [SETUP_OLLAMA.md](SETUP_OLLAMA.md)

## 📖 可用工具

| 工具 | 功能 | 參數 |
|------|------|------|
| `read_file` | 讀取文件內容 | `path` |
| `list_directory` | 列出目錄內容 | `path` (可選) |
| `write_file` | 寫入文件 | `path`, `content` |
| `create_directory` | 創建目錄 | `path` |
| `delete_file` | 刪除文件 ⚠️ | `path` |

⚠️ 刪除操作會要求用戶確認

## 💬 使用範例

```
You: list files in current directory

🔧 [Tool Call] list_directory({})
📋 [Tool Result] Contents of .:
[DIR]  src
[FILE] README.md
[FILE] pyproject.toml
...