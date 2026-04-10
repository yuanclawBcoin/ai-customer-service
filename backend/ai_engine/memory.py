"""
记忆系统 - 基于AI提取
"""
import re
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

@dataclass
class Memory:
    """单条记忆"""
    content: str
    importance: str = "normal"  # low, normal, high
    category: str = "general"    # name, preference, fact, topic
    created_at: str = ""
    is_pinned: bool = False
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class MemoryExtractor:
    """用AI从对话中提取重要信息"""
    
    EXTRACT_PROMPT = """你是一个记忆提取器。从对话中提取关于用户的重要信息。

对话内容：
{conversation}

请提取以下类型的信息：
1. 用户名字（如"我叫XX"、"叫我XX"）
2. 用户喜好（如"我喜欢XX"）
3. 用户身份/职业（如"我是学生"、"我在XX工作"）
4. 讨论过的话题（如聊过股票、电影等）
5. 重要事实（如电话号码、地址等）

输出格式（JSON数组）：
[
  {{"content": "用户叫小明", "category": "name", "importance": "high"}},
  {{"content": "用户喜欢打篮球", "category": "preference", "importance": "normal"}}
]

如果没有提取到任何信息，返回空数组：[]
只返回JSON，不要其他文字。"""
    
    @staticmethod
    async def extract(conversation: str, generator) -> List[Dict]:
        """从对话中提取重要信息"""
        try:
            prompt = MemoryExtractor.EXTRACT_PROMPT.format(conversation=conversation)
            result = await generator.generate(
                system_prompt="你是一个记忆提取器，擅长从对话中提取重要信息。",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # 解析JSON结果
            import json
            # 尝试提取JSON部分
            if "[" in result and "]" in result:
                start = result.find("[")
                end = result.rfind("]") + 1
                json_str = result[start:end]
                extracted = json.loads(json_str)
                
                # 转换为Memory对象
                memories = []
                for item in extracted:
                    if isinstance(item, dict) and "content" in item:
                        memories.append(Memory(
                            content=item["content"],
                            importance=item.get("importance", "normal"),
                            category=item.get("category", "general")
                        ))
                return memories
        except Exception as e:
            print(f"记忆提取失败: {e}")
        return []


class MemorySystem:
    """记忆系统 - 管理短期和长期记忆"""
    
    def __init__(self, max_short_term: int = 20):
        self.short_term = []  # 短期记忆（对话上下文）
        self.long_term = []   # 长期记忆（重要信息）
        self.max_short_term = max_short_term
        self.topics_discussed = set()  # 讨论过的话题
    
    def add_short_term(self, role: str, content: str, persona_id: int = None):
        """添加短期记忆"""
        self.short_term.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # 保持短期记忆在限制内
        if len(self.short_term) > self.max_short_term:
            self.short_term = self.short_term[-self.max_short_term:]
    
    def add_long_term(self, memory: Memory):
        """添加长期记忆"""
        # 检查是否已存在相似记忆
        if not any(memory.content in m.content or m.content in memory.content 
                   for m in self.long_term):
            self.long_term.append(memory)
    
    def get_context_for_ai(self, max_memories: int = 10) -> str:
        """生成发送给AI的上下文"""
        context_parts = []

        # 添加长期记忆（用户的重要信息）
        if self.long_term:
            important_memories = [m for m in self.long_term if m.importance == "high"]
            normal_memories = [m for m in self.long_term if m.importance != "high"]

            context_parts.append("【用户信息】")
            for m in important_memories[:5]:
                context_parts.append(f"- {m.content}")

            # 计算剩余可用记忆槽位
            remaining = max_memories - len(important_memories)
            if remaining > 0:
                for m in normal_memories[:remaining]:
                    context_parts.append(f"- {m.content}")

        # 添加讨论过的话题
        if self.topics_discussed:
            context_parts.append(f"\n【你们聊过的话题】{', '.join(list(self.topics_discussed)[:5])}")

        return "\n".join(context_parts) if context_parts else ""
    
    def add_topic(self, topic: str):
        """记录讨论过的话题"""
        self.topics_discussed.add(topic)
    
    def get_recent_conversation(self, count: int = 10) -> List[Dict]:
        """获取最近的对话"""
        return self.short_term[-count:]
    
    def to_dict(self) -> dict:
        """序列化为字典（用于存入数据库）"""
        return {
            "short_term": self.short_term,
            "long_term": [asdict(m) for m in self.long_term],
            "topics_discussed": list(self.topics_discussed)
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "MemorySystem":
        """从字典恢复（用于从数据库加载）"""
        system = cls()
        system.short_term = data.get("short_term", [])
        system.long_term = [Memory(**m) for m in data.get("long_term", [])]
        system.topics_discussed = set(data.get("topics_discussed", []))
        return system
