# Docker Setup Guide

本專案使用 Docker Compose 部署，包含兩個服務：
1. **Ollama** - 本地 LLM 服務
2. **Agent** - AI Agent 應用程式（使用 uv 管理 Python 依賴）

## 架構說明

```
┌─────────────────────────────────────────┐
│         Docker Compose 環境              │
│                                          │
│  ┌────────────┐      ┌────────────┐    │
│  │   Ollama   │◄─────┤   Agent    │    │
│  │  (LLM)     │      │  (Python)  │    │
│  │            │      │            │    │
│  │ Port: 11434│      │  uv image  │    │
│  └────────────┘      └────────────┘    │
│       │                    │            │
│       │                    │            │
│  [GPU Support]      [Workspace]        │
└─────────────────────────────────────────┘
```

## 前置需求

### 基本需求
- Docker (>= 20.10)
- Docker Compose (>= 2.0)

### GPU 支援（可選）
如果您有 NVIDIA GPU：
- NVIDIA Driver
- NVIDIA Container Toolkit

安裝 NVIDIA Container Toolkit：
```bash
# 配置 repository
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
    | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -fsSL https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
    | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
    | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update

# 安裝套件
sudo apt-get install -y nvidia-container-toolkit

# 配置 Docker
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

如果沒有 GPU，請在 `docker-compose.yml` 中註解掉 GPU 配置部分。

## 快速開始

### 1. 構建和啟動服務

```bash
# 構建並啟動所有服務
docker-compose up -d

# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f
```

### 2. 下載 Ollama 模型

首次使用需要下載模型：

```bash
# 進入 Ollama 容器
docker-compose exec ollama bash

# 下載模型（例如 gpt-oss, llama3.1 等）
ollama pull gpt-oss
ollama pull llama3.1

# 列出已安裝的模型
ollama list

# 退出容器
exit
```

### 3. 運行 AI Agent

```bash
# 方式 1: 使用 docker-compose
docker-compose run --rm agent

# 方式 2: 進入容器後運行
docker-compose exec agent bash
uv run src/main.py
```

## 配置說明

### 環境變量

在 `docker-compose.yml` 中可以配置以下環境變量：

```yaml
environment:
  # Ollama API 地址
  - OLLAMA_BASE_URL=http://ollama:11434/v1
  
  # 使用的模型名稱
  - OLLAMA_MODEL=gpt-oss
```

### 數據持久化

- **Ollama 模型數據**: 儲存在 Docker volume `ollama_data`
- **工作空間**: 掛載到 `./workspace` 目錄

## 常用命令

### 服務管理

```bash
# 啟動服務
docker-compose up -d

# 停止服務
docker-compose down

# 重啟服務
docker-compose restart

# 停止並刪除所有數據
docker-compose down -v

# 重新構建鏡像
docker-compose build --no-cache
```

### 查看日誌

```bash
# 查看所有服務日誌
docker-compose logs -f

# 只查看 agent 服務日誌
docker-compose logs -f agent

# 只查看 ollama 服務日誌
docker-compose logs -f ollama
```

### 進入容器

```bash
# 進入 agent 容器
docker-compose exec agent bash

# 進入 ollama 容器
docker-compose exec ollama bash
```

### 開發模式

如果需要修改代碼並即時測試：

```bash
# 代碼已經掛載，修改後重啟 agent 服務即可
docker-compose restart agent

# 或者在容器內直接運行
docker-compose exec agent uv run src/main.py
```

## 測試

### 測試 Ollama 連接

```bash
# 從主機測試
curl http://localhost:11434/api/tags

# 從 agent 容器測試
docker-compose exec agent curl http://ollama:11434/api/tags
```

### 測試 Agent

```bash
# 互動式運行 agent
docker-compose run --rm agent

# 在提示符中測試
You: list files
You: say a joke
You: exit
```

## 故障排除

### Ollama 服務無法啟動

```bash
# 檢查日誌
docker-compose logs ollama

# 如果是 GPU 相關問題，註解掉 docker-compose.yml 中的 GPU 配置
```

### Agent 無法連接到 Ollama

```bash
# 確認 Ollama 服務健康狀態
docker-compose ps

# 測試網路連接
docker-compose exec agent ping ollama
docker-compose exec agent curl http://ollama:11434/api/tags
```

### 模型下載失敗

```bash
# 檢查網路連接
docker-compose exec ollama ping github.com

# 手動重試下載
docker-compose exec ollama ollama pull gpt-oss
```

### 權限問題

```bash
# 確保當前用戶在 docker 群組中
sudo usermod -aG docker $USER

# 登出並重新登入，或執行
newgrp docker
```

## 清理

```bash
# 停止並刪除所有容器和網路
docker-compose down

# 同時刪除 volumes（會刪除 Ollama 模型數據）
docker-compose down -v

# 刪除構建的鏡像
docker-compose down --rmi all

# 完全清理（包含未使用的 Docker 資源）
docker system prune -a --volumes
```

## 生產環境部署

在生產環境中，建議：

1. **固定模型版本**：在 docker-compose.yml 中指定確切的鏡像版本
2. **資源限制**：添加 CPU 和記憶體限制
3. **日誌管理**：配置日誌驅動和大小限制
4. **監控**：添加健康檢查和監控
5. **備份**：定期備份 ollama_data volume

範例：
```yaml
services:
  agent:
    # ... other config ...
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 參考資源

- [uv 官方文檔](https://docs.astral.sh/uv/)
- [Ollama 官方文檔](https://docs.ollama.com/)
- [Docker Compose 文檔](https://docs.docker.com/compose/)

