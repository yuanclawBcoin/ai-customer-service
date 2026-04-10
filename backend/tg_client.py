"""
Telegram 客户端 - Pyrogram 用户账号连接
"""
import asyncio
import json
import random
import time
from typing import Optional, Callable
from pyrogram import Client, filters
from pyrogram.types import Message

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from models.database import get_config, get_persona, get_emotion, update_emotion
from ai_engine.emotion import EmotionEngine
from ai_engine.memory import MemorySystem
from ai_engine.persona import Persona
from ai_engine.generator import get_generator, update_generator

class TelegramClient:
    """Telegram 个人号客户端"""
    
    def __init__(self, account_id: int):
        self.account_id = account_id
        self.client: Optional[Client] = None
        self.running = False
        
        # 加载配置
        self.api_id = int(get_config("tg_api_id", str(settings.tg_api_id))) or settings.tg_api_id
        self.api_hash = get_config("tg_api_hash", settings.tg_api_hash) or settings.tg_api_hash
        self.session_name = f"tg_account_{account_id}"
        
        # 每个人设独立的状态
        self.emotion_engines: dict[int, EmotionEngine] = {}
        self.memory_systems: dict[int, MemorySystem] = {}
        self.personas: dict[int, Persona] = {}
    
    def _get_or_create_emotion(self, persona_id: int) -> EmotionEngine:
        if persona_id not in self.emotion_engines:
            self.emotion_engines[persona_id] = EmotionEngine()
        return self.emotion_engines[persona_id]
    
    def _get_or_create_memory(self, persona_id: int) -> MemorySystem:
        if persona_id not in self.memory_systems:
            self.memory_systems[persona_id] = MemorySystem()
        return self.memory_systems[persona_id]
    
    def _get_or_create_persona(self, persona_id: int) -> Persona:
        if persona_id not in self.personas:
            if persona_id:
                persona_data = get_persona(persona_id)
                if persona_data:
                    self.personas[persona_id] = Persona(persona_data)
                    return self.personas[persona_id]
            self.personas[persona_id] = Persona()
        return self.personas[persona_id]
    
    async def start(self):
        """启动 Telegram 客户端"""
        if not self.api_id or not self.api_hash:
            print(f"[TG-{self.account_id}] 未配置 API ID/Hash，请在管理后台设置")
            return False
        
        try:
            self.client = Client(
                self.session_name,
                api_id=self.api_id,
                api_hash=self.api_hash
            )
            
            await self.client.start()
            self.running = True
            print(f"[TG-{self.account_id}] Telegram 已连接")
            
            # 注册处理器
            self.client.add_handler(
                filters.private & ~filters.bot,
                self._handle_message
            )
            
            return True
        except Exception as e:
            print(f"[TG-{self.account_id}] 连接失败: {e}")
            return False
    
    async def stop(self):
        """停止 Telegram 客户端"""
        self.running = False
        if self.client:
            await self.client.stop()
            print(f"[TG-{self.account_id}] Telegram 已断开")
    
    async def _handle_message(self, client: Client, message: Message):
        """处理收到的消息"""
        try:
            user_id = str(message.from_user.id)
            text = message.text or message.caption or ""
            
            if not text.strip():
                return
            
            print(f"[TG-{self.account_id}] 收到消息 from {user_id}: {text[:50]}...")
            
            # 获取该用户的persona_id（这里简化处理，实际应该关联）
            persona_id = 1  # 默认使用第一个
            
            # 获取组件
            emotion = self._get_or_create_emotion(persona_id)
            memory = self._get_or_create_memory(persona_id)
            persona = self._get_or_create_persona(persona_id)
            
            # 更新情绪
            emotion.update(text)
            
            # 检查是否应该忽略
            if emotion.should_ignore():
                print(f"[TG-{self.account_id}] 情绪触发忽略: {emotion.current_emotion}")
                return
            
            # 添加到记忆
            memory.add_short_term("user", text, persona_id)
            
            # 生成回复
            delay = emotion.get_typing_delay()
            await asyncio.sleep(delay)
            
            # 更新 API key（可能已在后台更改）
            api_key = get_config("minimax_api_key", settings.minimax_api_key)
            if api_key:
                update_generator(api_key)
            
            generator = get_generator()
            context = memory.get_context_for_ai()
            system_prompt = persona.get_system_prompt(emotion.get_style_modifier())
            
            # 构建消息历史
            messages = memory.short_term[-10:] if len(memory.short_term) > 1 else [{"role": "user", "content": text}]
            
            reply = await generator.generate(
                system_prompt=system_prompt,
                messages=messages,
                context=context
            )
            
            if reply:
                # 保存AI回复到记忆
                memory.add_short_term("assistant", reply, persona_id)
                
                # 随机决定是否加表情
                if random.random() < 0.3:
                    reply = self._add_random_emoji(reply)
                
                # 发送回复
                await message.reply_text(reply)
                print(f"[TG-{self.account_id}] 发送回复 to {user_id}: {reply[:50]}...")
                
                # 更新数据库中的情绪状态
                update_emotion(user_id, emotion.current_emotion, emotion.intensity, text[:30], persona_id)
            else:
                print(f"[TG-{self.account_id}] 未生成回复")
        
        except Exception as e:
            print(f"[TG-{self.account_id}] 处理消息出错: {e}")
            import traceback
            traceback.print_exc()
    
    def _add_random_emoji(self, text: str) -> str:
        """随机添加表情"""
        emojis = ["😂", "🤣", "😊", "🙈", "👍", "❤️", "💕", "😄", "😎", "🤔", "嗯", "哦", "哈"]
        if random.random() < 0.5:
            return text + random.choice(emojis)
        return text


# 全局客户端管理器
_clients: dict[int, TelegramClient] = {}

async def start_all_clients():
    """启动所有配置的 Telegram 账号"""
    from backend.models.database import get_tg_accounts
    
    accounts = get_tg_accounts()
    for account in accounts:
        if account.get("status") == "active":
            client = TelegramClient(account["id"])
            success = await client.start()
            if success:
                _clients[account["id"]] = client
            else:
                print(f"账号 {account['name']} 启动失败")

async def stop_all_clients():
    """停止所有客户端"""
    for client in _clients.values():
        await client.stop()
    _clients.clear()

def get_client(account_id: int) -> Optional[TelegramClient]:
    return _clients.get(account_id)
