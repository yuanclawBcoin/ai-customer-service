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
async def list_conversations(user_id: str = None, platform: str = "telegram", all: bool = False):
    """获取对话记录"""
    from backend.models.database import get_conversation, get_all_conversations

    # 如果需要所有对话记录
    if all:
        return get_all_conversations(user_id, platform)

    # 否则返回单个用户的最新对话
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
    """自动启动 Telegram 客户端"""
    try:
        await asyncio.sleep(2)  # 等待数据库初始化
        await start_all_clients()
    except Exception as e:
        print(f"自动启动 Telegram 失败: {e}")

async def handle_tg_message(account_id: int, message):
    """处理 Telegram 消息"""
    try:
        from models.database import get_tg_accounts, get_persona, save_user_memory
        from ai_engine.generator import get_generator
        from ai_engine.emotion import EmotionEngine
        from ai_engine.memory import MemorySystem, MemoryExtractor

        # 获取账号配置
        accounts = get_tg_accounts()
        account = next((a for a in accounts if a["id"] == account_id), None)
        if not account:
            print(f"[TG-{account_id}] 账号未找到")
            return

        # 检查是否开启自动回复
        if not account.get("auto_reply"):
            print(f"[TG-{account_id}] 自动回复已关闭")
            return

        # 获取人设
        persona_id = account.get("persona_id")
        if not persona_id:
            print(f"[TG-{account_id}] 未绑定人设")
            return

        persona = get_persona(persona_id)
        if not persona:
            print(f"[TG-{account_id}] 人设未找到: {persona_id}")
            return

        # 获取用户信息
        user_id = str(message.from_user.id)
        user_message = message.text or ""

        # 初始化情绪引擎、记忆系统和话题（每个用户独立）
        if not hasattr(handle_tg_message, 'user_emotions'):
            handle_tg_message.user_emotions = {}
        if not hasattr(handle_tg_message, 'user_memories'):
            handle_tg_message.user_memories = {}
        if not hasattr(handle_tg_message, 'user_topics'):
            handle_tg_message.user_topics = {}  # 内存缓存

        if user_id not in handle_tg_message.user_emotions:
            emotion_engine = EmotionEngine()
            # 从数据库加载情绪状态
            from models.database import get_emotion
            db_emotion = get_emotion(user_id, persona_id)
            emotion_engine.current_emotion = db_emotion.get("emotion", "neutral")
            emotion_engine.intensity = db_emotion.get("intensity", 0)
            handle_tg_message.user_emotions[user_id] = emotion_engine
        if user_id not in handle_tg_message.user_memories:
            memory_system = MemorySystem()

            # 从数据库加载该用户的历史记忆（按人设ID查询）
            from models.database import get_memories
            db_memories = get_memories(user_id, persona_id)
            for mem in db_memories:
                from ai_engine.memory import Memory
                memory_system.add_long_term(Memory(
                    content=mem["content"],
                    importance=mem.get("importance", "normal"),
                    category=mem.get("category", "general")
                ))

            handle_tg_message.user_memories[user_id] = memory_system

        # 加载话题（从数据库）
        if user_id not in handle_tg_message.user_topics:
            from models.database import get_topics
            db_topics = get_topics(user_id, persona_id)
            handle_tg_message.user_topics[user_id] = {topic: True for topic in db_topics}

        emotion_engine = handle_tg_message.user_emotions[user_id]
        memory_system = handle_tg_message.user_memories[user_id]
        # 分析用户情绪（update内部会调用analyze_text）
        emotion_engine.update(user_message)

        # 获取AI的情绪状态
        ai_emotion = emotion_engine.get_ai_emotion()

        # 检查是否应该忽略（模拟真人偶尔不回复）
        if emotion_engine.should_ignore():
            print(f"[TG-{account_id}] 看心情，暂时不回复用户 {user_id}")
            return

        # 判断是否是第一条消息
        is_first_message = len(memory_system.short_term) == 0

        # 添加用户消息到记忆
        memory_system.add_short_term("user", user_message, persona_id)

        # 构建消息列表（包含对话历史）
        messages = []
        for msg in memory_system.short_term[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # 构建系统提示词
        from ai_engine.persona import Persona
        persona_obj = Persona(persona)

        # 获取人设的个性化设置
        persona_habits = persona_obj.get_habits()

        # 只有第一条消息才加开场白
        emotion_style = emotion_engine.get_style_modifier()
        system_prompt = persona_obj.get_system_prompt(emotion_style, ai_emotion=ai_emotion)

        if is_first_message:
            system_prompt += f"\n\n【开场白】{persona_obj.get_greeting()}"

        # 加入记忆上下文
        context = memory_system.get_context_for_ai()
        if context:
            system_prompt += f"\n\n{context}"

        # 加入讨论过的话题上下文
        if user_id in handle_tg_message.user_topics:
            topics = list(handle_tg_message.user_topics[user_id].keys())
            if topics:
                system_prompt += f"\n\n【你们之前聊过的话题】{', '.join(topics[:5])}"

        # 加入情绪上下文
        emotion_context = emotion_engine.get_context_for_ai()
        if emotion_context:
            system_prompt += f"\n\n【当前对话情绪】{emotion_context}"

        # 调用 AI 生成回复
        generator = get_generator()
        response = await generator.generate(
            system_prompt=system_prompt,
            messages=messages,
            persona_habits=persona_habits
        )

        if response:
            # 模拟真人打字延迟
            typing_delay = emotion_engine.get_typing_delay()
            await asyncio.sleep(typing_delay)

            # 模拟真人偶尔打错字
            response = emotion_engine.simulate_typo(response)

            # 发送回复
            await message.reply(response)

            # 添加AI回复到记忆
            memory_system.add_short_term("assistant", response, persona_id)

            # 用AI提取重要信息并存入数据库
            conversation = f"用户: {user_message}\n助手: {response}"
            extracted_memories = await MemoryExtractor.extract(conversation, generator)
            for mem in extracted_memories:
                save_user_memory(user_id, persona_id, mem)  # 用persona_id而不是account_id
                memory_system.add_long_term(mem)

            # 提取讨论话题（持久化到数据库）
            topic_extracted = await extract_topic(user_message, generator)
            if topic_extracted:
                memory_system.add_topic(topic_extracted)
                if user_id not in handle_tg_message.user_topics:
                    handle_tg_message.user_topics[user_id] = {}
                handle_tg_message.user_topics[user_id][topic_extracted] = True
                # 保存到数据库
                from models.database import save_topic
                save_topic(user_id, topic_extracted, persona_id)

            print(f"[TG-{account_id}] [{ai_emotion}] 已回复用户 {user_id}: {response[:30]}...")

            # 持久化情绪状态到数据库
            from models.database import update_emotion
            update_emotion(
                user_id=user_id,
                emotion=emotion_engine.current_emotion,
                intensity=emotion_engine.intensity,
                triggered_by=user_message[:50],
                persona_id=persona_id
            )

            # 持久化对话历史到数据库
            from models.database import save_conversation
            conversation_history = memory_system.short_term[-20:]  # 保存最近20条
            save_conversation(
                user_id=user_id,
                platform="telegram",
                messages=conversation_history,
                persona_id=persona_id
            )
        else:
            print(f"[TG-{account_id}] AI 未生成回复")

    except Exception as e:
        print(f"[TG-{account_id}] 处理消息异常: {e}")
        import traceback
        traceback.print_exc()


async def extract_topic(text: str, generator) -> str:
    """从消息中提取讨论话题"""
    try:
        prompt = f"从下面文本中提取一个讨论话题关键词（如：股票、电影、美食、游戏、旅行等），只返回一个词，没有就返回空：\n{text}"
        result = await generator.generate(
            system_prompt="你是一个话题提取器。",
            messages=[{"role": "user", "content": prompt}]
        )
        result = result.strip()
        if result and len(result) <= 10 and not result.startswith("没有"):
            return result
    except:
        pass
    return ""

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
