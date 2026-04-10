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
        context: str = "",
        temperature: float = 0.8,
        max_tokens: int = 500
    ) -> str:
        """生成回复"""
        
        if not self.api_key:
            return "【未配置 API Key，请在管理后台设置 MiniMax API Key】"
        
        # 构建消息
        full_messages = []
        
        # 系统提示词
        system_content = system_prompt
        if context:
            system_content += f"\n\n【已知信息】\n{context}"
        
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
    if _generator is None:
        _generator = ReplyGenerator()
    return _generator

def update_generator(api_key: str):
    global _generator
    _generator = ReplyGenerator(api_key)
