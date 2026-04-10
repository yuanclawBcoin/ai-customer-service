"""
回复生成器 - 调用 MiniMax API 生成回复
"""
import json
import httpx
from typing import List, Dict, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import settings

class ReplyGenerator:
    """AI 回复生成器"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.minimax_api_key
        self.api_url = settings.minimax_api_url
        self.model = settings.minimax_model
    
    async def generate(
        self,
        system_prompt: str,
        messages: List[Dict],
        temperature: float = 0.8,
        max_tokens: int = 500,
        persona_habits: Dict = None
    ) -> str:
        """生成回复"""

        if not self.api_key:
            return "【未配置 API Key，请在管理后台设置 MiniMax API Key】"

        # 构建消息
        full_messages = []

        # 系统提示词（已包含context）
        system_content = system_prompt

        # 加入人设习惯
        if persona_habits:
            habits = persona_habits.get("habits", [])
            if habits:
                habits_text = "、".join(habits)
                system_content += f"\n\n【你的说话习惯】可以适当使用这些口头禅：{habits_text}"

            # 加入常用emoji
            emojis = persona_habits.get("favorite_emoji", [])
            if emojis:
                emoji_text = "、".join(emojis)
                system_content += f"\n\n【你的常用emoji】{emoji_text}（偶尔使用，不要每句都用）"
        
        full_messages.append({
            "role": "system",
            "content": system_content
        })
        
        # 对话历史
        for msg in messages:
            full_messages.append({
                "role": msg.get("role", "user"),
                "content": msg["content"]
            })
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.api_url}/text/chatcompletion_v2",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": full_messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("choices", [{}])[0].get("message", {}).get("content", "")
                else:
                    return f"【API 错误: {response.status_code}】{response.text[:100]}"
        
        except Exception as e:
            return f"【请求失败: {str(e)}】"
    
    def build_conversation_for_api(self, short_term: List[Dict]) -> List[Dict]:
        """构建发送给API的对话格式"""
        result = []
        for msg in short_term:
            role = "user" if msg["role"] == "user" else "assistant"
            result.append({
                "role": role,
                "content": msg["content"]
            })
        return result

# 全局实例
_generator: Optional[ReplyGenerator] = None

def get_generator() -> ReplyGenerator:
    global _generator
    # 每次都从数据库读取最新的 API Key
    from models.database import get_config
    api_key = get_config("minimax_api_key", "")
    _generator = ReplyGenerator(api_key)
    return _generator

def update_generator(api_key: str):
    global _generator
    _generator = ReplyGenerator(api_key)
