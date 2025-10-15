"""
MCP Tools Server - 提供本地工具給 AI Agent 使用
使用 FastMCP 框架建立 MCP 工具伺服器
"""

from mcp.server import FastMCP
import os

# 建立 MCP 伺服器實例
# FastMCP 是 MCP SDK 提供的快速建立工具伺服器的框架
server = FastMCP("local-tools")

@server.tool()
def read_file(path: str) -> str:
    """
    讀取本地文件內容
    
    Args:
        path: 文件的絕對或相對路徑
        
    Returns:
        文件內容或錯誤訊息
    """
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return f"Error: File not found at {path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

@server.tool()
def list_directory(path: str = ".") -> str:
    """
    列出目錄中的文件和子目錄
    
    Args:
        path: 目錄路徑（預設為當前目錄）
        
    Returns:
        目錄內容列表
    """
    try:
        if not os.path.exists(path):
            return f"Error: Directory not found at {path}"
        
        items = os.listdir(path)
        # 分類文件和目錄
        dirs = [f"[DIR]  {item}" for item in items if os.path.isdir(os.path.join(path, item))]
        files = [f"[FILE] {item}" for item in items if os.path.isfile(os.path.join(path, item))]
        
        result = f"Contents of {path}:\n"
        result += "\n".join(sorted(dirs) + sorted(files))
        return result
    except Exception as e:
        return f"Error listing directory: {str(e)}"

@server.tool()
def write_file(path: str, content: str) -> str:
    """
    寫入內容到文件
    
    Args:
        path: 目標文件路徑
        content: 要寫入的內容
        
    Returns:
        成功或錯誤訊息
    """
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

@server.tool()
def create_directory(path: str) -> str:
    """
    創建目錄

    Args:
        path: 目錄路徑

    Returns:
        成功或錯誤訊息
    """
    try:
        os.makedirs(path)
        return f"Successfully created directory at {path}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"

@server.tool()
def delete_file(path: str) -> str:
    """
    刪除文件
    需要用戶確認才能執行（確認機制在客戶端實現）

    Args:
        path: 文件路徑

    Returns:
        成功或錯誤訊息
    """
    try:
        if not os.path.exists(path):
            return f"Error: File not found at {path}"
        os.remove(path)
        return f"Successfully deleted file at {path}"
    except Exception as e:
        return f"Error deleting file: {str(e)}"

# 運行伺服器
# FastMCP 使用 stdio 傳輸協定，通過標準輸入/輸出與客戶端通訊
if __name__ == "__main__":
    server.run()
