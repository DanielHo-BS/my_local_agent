# 使用指南 - Local AI Agent

這是一個使用 Ollama 本地 LLM 和 MCP 工具的簡單 AI Agent。

## 前置需求

1. **Docker 和 Ollama 容器運行中**
2. **已安裝 Python 依賴** (執行 `uv sync`)

## 快速開始

### 1. 確認 Ollama 正在運行

首先確認 Ollama 容器已經啟動並下載了模型：

```bash
# 啟動 Ollama 容器（如果還沒啟動）
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

# 下載 llama3.1 模型（或您想用的其他模型）
docker exec -it ollama ollama pull llama3.1

# 測試 Ollama 是否運行
curl http://localhost:11434/api/tags
```

### 2. 運行 AI Agent

```bash
cd /home/daniel/my_local_agent
uv run src/main.py
```

## 功能說明

### 可用工具

Agent 有以下本地工具可以使用：

1. **read_file** - 讀取文件內容
   - 參數：`path` (文件路徑)

2. **list_directory** - 列出目錄內容
   - 參數：`path` (目錄路徑，預設為當前目錄)

3. **write_file** - 寫入文件
   - 參數：`path` (文件路徑), `content` (要寫入的內容)

4. **create_directory** - 創建目錄
   - 參數：`path` (目錄路徑)

5. **delete_file** - 刪除文件 ⚠️
   - 參數：`path` (文件路徑)
   - 注意：此操作會要求用戶確認

### 範例對話

```
You: 幫我列出當前目錄有哪些文件？

[Tool Call] list_directory({'path': '.'})