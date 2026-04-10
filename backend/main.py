"""
AI 客服系统 - FastAPI 主入口
"""
import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from models.database import init_db, get_config, set_config, get_personas, get_persona, create_persona, update_persona
from models.database import get_tg_accounts, add_tg_account, update_tg_account
from tg_client import start_all_clients, stop_all_clients

# 初始化数据库
init_db()

# 确保data目录存在
os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动和关闭时的处理"""
    # 启动时
    print("🚀 AI 客服系统启动中...")
    
    # 尝试自动启动 Telegram 客户端
    asyncio.create_task(auto_start_telegram())
    
    yield
    
    # 关闭时
    print("👋 关闭 AI 客服系统...")
    await stop_all_clients()

app = FastAPI(
    title="AI 客服系统",
    description="管理后台 + Telegram 个人号 AI 客服",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件和模板
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "frontend", "dist", "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "frontend", "dist"))

# ============ API 路由 ============

@app.get("/")
async def root():
    """前端页面"""
    from fastapi.responses import FileResponse
    index_path = os.path.join(BASE_DIR, "frontend", "dist", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "AI 客服系统 API", "version": "1.0.0"}

# --- 系统配置 API ---

@app.get("/api/config")
async def get_all_config():
    """获取所有配置"""
    return {
        "minimax_api_key": get_config("minimax_api_key", ""),
        "tg_api_id": get_config("tg_api_id", ""),
        "tg_api_hash": get_config("tg_api_hash", ""),
        "admin_username": get_config("admin_username", settings.admin_username),
        "max_history_length": int(get_config("max_history_length", str(settings.max_history_length))),
    }

@app.post("/api/config")
async def save_config(data: dict):
    """保存配置"""
    for key, value in data.items():
        set_config(key, str(value))
    return {"success": True, "message": "配置已保存"}

# --- 人设管理 API ---

@app.get("/api/personas")
async def list_personas():
    """获取所有人设"""
    return get_personas()

@app.get("/api/personas/{persona_id}")
async def get_single_persona(persona_id: int):
    """获取单个 人设"""
    persona = get_persona(persona_id)
    if not persona:
        raise HTTPException(status_code=404, message="人设不存在")
    return persona

@app.post("/api/personas")
async def create_new_persona(data: dict):
    """创建新人设"""
    persona_id = create_persona(data)
    return {"success": True, "id": persona_id}

@app.put("/api/personas/{persona_id}")
async def update_persona_data(persona_id: int, data: dict):
    """更新人设"""
    update_persona(persona_id, data)
    return {"success": True}

@app.get("/api/personas/options/personalities")
async def get_personality_options():
    """获取可选性格"""
    from backend.ai_engine.persona import Persona
    return Persona.get_available_personalities()

@app.get("/api/personas/options/styles")
async def get_style_options():
    """获取可选风格"""
    from backend.ai_engine.persona import Persona
    return Persona.get_available_styles()

# --- Telegram 账号 API ---

@app.get("/api/tg-accounts")
async def list_tg_accounts():
    """获取所有 TG 账号"""
    return get_tg_accounts()

@app.post("/api/tg-accounts")
async def create_tg_account(data: dict):
    """添加 TG 账号"""
    account_id = add_tg_account(data)
    return {"success": True, "id": account_id}

@app.put("/api/tg-accounts/{account_id}")
async def update_tg_account_data(account_id: int, data: dict):
    """更新 TG 账号"""
    update_tg_account(account_id, data)
    return {"success": True}

@app.post("/api/tg-accounts/{account_id}/send-code")
async def send_tg_code(account_id: int, data: dict):
    """发送验证码到手机"""
    from tg_client import TelegramClient, set_client
    
    phone = data.get("phone")
    if not phone:
        return {"success": False, "error": "请提供手机号"}
    
    client = TelegramClient(account_id)
    result = await client.send_code(phone)
    
    if result.get("success"):
        set_client(account_id, client)
    
    return result

@app.post("/api/tg-accounts/{account_id}/verify-code")
async def verify_tg_code(account_id: int, data: dict):
    """验证验证码"""
    from tg_client import get_client, set_client
    
    code = data.get("code")
    password = data.get("password")  # 2FA密码（可选）
    if not code:
        return {"success": False, "error": "请提供验证码"}
    
    client = get_client(account_id)
    if not client:
        return {"success": False, "error": "请先发送验证码"}
    
    result = await client.verify_code(code, password)
    
    if result.get("success"):
        update_tg_account(account_id, {"status": "online"})
    
    return result

@app.post("/api/tg-accounts/{account_id}/connect")
async def connect_tg_account(account_id: int):
    """连接 TG 账号（使用已有 session）"""
    from tg_client import get_client
    
    # 检查是否已连接
    client = get_client(account_id)
    if client:
        return {"success": True, "message": "已连接"}
    
    # 尝试启动（有 session 文件时直接启动）
    from tg_client import TelegramClient
    client = TelegramClient(account_id)
    success = await client.start()
    
    if success:
        set_client(account_id, client)
        update_tg_account(account_id, {"status": "online"})
        return {"success": True, "message": "连接成功"}
    else:
        return {"success": False, "need_auth": True, "message": "需要先验证账号"}

@app.post("/api/tg-accounts/{account_id}/disconnect")
async def disconnect_tg_account(account_id: int):
    """断开 TG 账号"""
    from backend.tg_client import get_client
    
    client = get_client(account_id)
    if client:
        await client.stop()
        update_tg_account(account_id, {"status": "offline"})
        return {"success": True}
    return {"success": False, "message": "未连接"}

# --- 对话记录 API ---

@app.get("/api/conversations")
async def list_conversations(user_id: str = None, platform: str = "telegram"):
    """获取对话记录"""
    from backend.models.database import get_conversation
    if user_id:
        conv = get_conversation(user_id, platform)
        return conv if conv else {"messages": []}
    return []

# --- 记忆管理 API ---

@app.get("/api/memories")
async def list_memories(user_id: str, persona_id: int = None):
    """获取记忆"""
    from backend.models.database import get_memories
    return get_memories(user_id, persona_id)

@app.post("/api/memories")
async def add_new_memory(data: dict):
    """添加记忆"""
    from backend.models.database import add_memory
    add_memory(data["user_id"], data["content"], data.get("persona_id"), 
               data.get("importance", "normal"), data.get("is_pinned", False))
    return {"success": True}

# --- 情绪状态 API ---

@app.get("/api/emotions")
async def get_emotion_state(user_id: str, persona_id: int = None):
    """获取情绪状态"""
    from backend.models.database import get_emotion
    return get_emotion(user_id, persona_id)

# ============ 辅助函数 ============

async def auto_start_telegram():
    """自动启动 Telegram"""
    await asyncio.sleep(2)  # 等待配置加载
    try:
        await start_all_clients()
    except Exception as e:
        print(f"自动启动 Telegram 失败: {e}")

# ============ 错误处理 ============

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
