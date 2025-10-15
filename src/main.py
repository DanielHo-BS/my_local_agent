"""
Simple Local AI Agent
使用 Ollama LLM 和 MCP 工具伺服器建立本地 AI Agent
"""

from openai import OpenAI
import json
import os

# 從環境變量讀取配置，如果沒有則使用預設值
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss")

# 建立 Ollama 客戶端
# Ollama 提供 OpenAI 兼容的 API，所以可以直接使用 OpenAI SDK
client = OpenAI(
    base_url=OLLAMA_BASE_URL,  # Ollama API endpoint
    api_key="dummy"  # Ollama 不需要真實的 API key
)

# 設定使用的模型
MODEL = OLLAMA_MODEL

# 定義可用的工具（從 tools_server.py 提供的工具）
# 這些工具描述會告訴 LLM 可以使用哪些功能
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file from the local filesystem",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The file path to read"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List files and directories in a given path",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The directory path to list (default: current directory)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The file path to write to"
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write"
                    }
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_directory",
            "description": "Create a new directory at the specified path",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The directory path to create"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "Delete a file at the specified path. This is a destructive operation that requires user confirmation before execution.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The file path to delete"
                    }
                },
                "required": ["path"]
            }
        }
    }
]

def execute_tool(tool_name: str, arguments: dict) -> str:
    """
    執行工具調用
    在真實場景中，這裡會與 MCP 伺服器通訊
    現在暫時在本地直接執行功能
    """
    import os
    
    if tool_name == "read_file":
        path = arguments.get("path")
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            return f"Error: File not found at {path}"
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    elif tool_name == "list_directory":
        path = arguments.get("path", ".")
        try:
            if not os.path.exists(path):
                return f"Error: Directory not found at {path}"
            
            items = os.listdir(path)
            dirs = [f"[DIR]  {item}" for item in items if os.path.isdir(os.path.join(path, item))]
            files = [f"[FILE] {item}" for item in items if os.path.isfile(os.path.join(path, item))]
            
            result = f"Contents of {path}:\n"
            result += "\n".join(sorted(dirs) + sorted(files))
            return result
        except Exception as e:
            return f"Error listing directory: {str(e)}"
    
    elif tool_name == "write_file":
        path = arguments.get("path")
        content = arguments.get("content")
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"
    
    elif tool_name == "create_directory":
        path = arguments.get("path")
        try:
            os.makedirs(path, exist_ok=True)
            return f"Successfully created directory at {path}"
        except Exception as e:
            return f"Error creating directory: {str(e)}"
    
    elif tool_name == "delete_file":
        path = arguments.get("path")
        try:
            if not os.path.exists(path):
                return f"Error: File not found at {path}"
            
            # 在刪除前要求用戶確認
            print(f"\n⚠️  WARNING: You are about to delete: {path}")
            user_response = input("Are you sure you want to delete this file? (yes/no): ").strip().lower()
            
            if user_response not in ["yes", "y"]:
                return f"Operation cancelled: File deletion aborted by user"
            
            os.remove(path)
            return f"Successfully deleted file at {path}"
        except Exception as e:
            return f"Error deleting file: {str(e)}"
    
    return f"Unknown tool: {tool_name}"

def chat(user_message: str, conversation_history: list = None) -> tuple[str, list]:
    """
    與 AI 進行對話，支援工具調用
    
    Args:
        user_message: 用戶輸入的訊息
        conversation_history: 對話歷史記錄
        
    Returns:
        (AI 回應, 更新後的對話歷史)
    """
    if conversation_history is None:
        conversation_history = []
        # 添加系統提示詞來引導 LLM 行為
        conversation_history.append({
            "role": "system",
            "content": (
                "You are a helpful AI assistant with access to file system tools.\n\n"
                "IMPORTANT - When to use tools:\n"
                "- ONLY use tools when the user explicitly asks to interact with files or directories\n"
                "- DO NOT use tools for general conversation, questions, jokes, or information requests\n"
                "- Examples of when TO use tools: 'read file.txt', 'list files', 'delete test.py', 'create folder'\n"
                "- Examples of when NOT to use tools: 'say a joke', 'what is Python?', 'hello', 'help me understand'\n\n"
                "When using tools:\n"
                "1. Use the appropriate tool to complete the user's file system request\n"
                "2. After receiving tool results, provide a clear and concise summary\n"
                "3. If a tool operation succeeds, simply confirm the success\n"
                "4. If a tool operation fails, explain what went wrong\n\n"
                "For general conversation:\n"
                "- Respond directly without using any tools\n"
                "- Be helpful, friendly, and concise"
            )
        })
    
    # 添加用戶訊息到對話歷史
    conversation_history.append({
        "role": "user",
        "content": user_message
    })
    
    # 調用 LLM，允許最多 5 次工具調用循環
    max_iterations = 5
    for iteration in range(max_iterations):
        # 發送請求到 LLM
        response = client.chat.completions.create(
            model=MODEL,
            messages=conversation_history,
            tools=TOOLS,
            tool_choice="auto"  # 讓 LLM 自動決定是否使用工具
        )
        
        assistant_message = response.choices[0].message
        
        # 檢查是否有工具調用
        if assistant_message.tool_calls:
            # 添加 assistant 的回應（包含工具調用）到歷史
            conversation_history.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })
            
            # 執行每個工具調用
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"\n🔧 [Tool Call] {function_name}({function_args})")
                
                # 執行工具
                tool_result = execute_tool(function_name, function_args)
                
                # 顯示工具執行結果
                print(f"📋 [Tool Result] {tool_result}\n")
                
                # 添加工具結果到對話歷史
                conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })
            
            # 繼續循環，讓 LLM 處理工具結果
        else:
            # 沒有工具調用，返回最終回應
            conversation_history.append({
                "role": "assistant",
                "content": assistant_message.content
            })
            return assistant_message.content, conversation_history
    
    # 達到最大迭代次數
    return "Maximum iterations reached. Please try a simpler query.", conversation_history

def main():
    """
    主程式：簡單的命令行聊天介面
    """
    print("=" * 60)
    print("🤖 Local AI Agent with Ollama")
    print("=" * 60)
    print(f"Using model: {MODEL}")
    print("Type 'exit' or 'quit' to end the conversation")
    print("=" * 60)
    print()
    
    conversation_history = []
    
    while True:
        # 獲取用戶輸入
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        
        if not user_input:
            continue
        
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        
        # 調用 AI
        try:
            response, conversation_history = chat(user_input, conversation_history)
            print(f"\nAssistant: {response}\n")
        except Exception as e:
            print(f"\nError: {str(e)}\n")

if __name__ == "__main__":
    main()
