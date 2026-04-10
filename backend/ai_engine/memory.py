"""
记忆系统 - 管理AI对用户的记忆
"""
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class Memory:
    """记忆条目"""
    def __init__(self, content: str, importance: str = "normal", is_pinned: bool = False):
        self.content = content
        self.importance = importance  # low, normal, high, critical
        self.is_pinned = is_pinned
        self.created_at = datetime.now()
        self.access_count = 0
    
    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "importance": self.importance,
            "is_pinned": self.is_pinned,
            "created_at": self.created_at.isoformat(),
            "access_count": self.access_count
        }

class MemorySystem:
    """记忆系统"""
    
    # 重要信息模式
    IMPORTANT_PATTERNS = [
        r"我叫(.+?)[，,。]",
        r"我叫(.+?)$",
        r"我喜欢(.+?)[，,。]",
        r"我是(.+?人)[，,。]",
        r"我的(.+?)[是为](.+?)[，,。]",
        r"(.+?)\s*@\s*(.+?\.com)",  # 邮箱
        r"电话[:：]?\s*(\d{11})",  # 手机号
        r"(\d{4}-\d{2}-\d{2})",  # 日期
    ]
    
    def __init__(self, max_short_term: int = 20):
        self.short_term = []  # 短期记忆（对话上下文）
        self.long_term = []   # 长期记忆
        self.max_short_term = max_short_term
    
    def extract_important_info(self, text: str) -> List[str]:
        """从文本中提取重要信息"""
        extracted = []
        for pattern in self.IMPORTANT_PATTERNS:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    info = " ".join(m for m in match if m)
                else:
                    info = match
                if info and len(info) > 1:
                    extracted.append(info.strip())
        return extracted
    
    def add_short_term(self, role: str, content: str, persona_id: int = None):
        """添加短期记忆"""
        self.short_term.append({
            "role": role,  # "user" or "assistant"
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        # 保持短期记忆在限制内
        if len(self.short_term) > self.max_short_term:
            self.short_term = self.short_term[-self.max_short_term:]
        
        # 自动提取重要信息加入长期记忆
        important = self.extract_important_info(content)
        for info in important:
            # 检查是否已存在
            if not any(info in mem["content"] for mem in self.long_term):
                self.long_term.append(Memory(info, importance="high"))
    
    def add_long_term(self, content: str, importance: str = "normal", is_pinned: bool = False):
        """添加长期记忆"""
        self.long_term.append(Memory(content, importance, is_pinned))
    
    def get_context_for_ai(self, max_tokens: int = 2000) -> str:
        """生成发送给AI的上下文"""
        context_parts = []
        
        # 长期记忆（重要信息优先）
        pinned = [m for m in self.long_term if m.is_pinned]
        important = [m for m in self.long_term if m.importance in ("high", "critical")]
        normal = [m for m in self.long_term if m not in pinned and m not in important]
        
        for mem in pinned + important + normal:
            context_parts.append(f"- {mem.content}")
        
        # 短期记忆（最近对话）
        if self.short_term:
            context_parts.append("\n=== 最近对话 ===")
            for msg in self.short_term[-10:]:
                role = "用户" if msg["role"] == "user" else "AI"
                context_parts.append(f"{role}: {msg['content']}")
        
        context = "\n".join(context_parts)
        
        # 简单截断（实际应该按token计算）
        if len(context) > max_tokens:
            context = context[-max_tokens:]
        
        return context
    
    def load_from_db(self, memories: List[dict]):
        """从数据库加载记忆"""
        self.long_term = []
        for m in memories:
            mem = Memory(m["content"], m.get("importance", "normal"), bool(m.get("is_pinned", 0)))
            if m.get("created_at"):
                mem.created_at = datetime.fromisoformat(m["created_at"])
            self.long_term.append(mem)
    
    def save_to_db(self, user_id: str, persona_id: int = None):
        """保存记忆到数据库"""
        from backend.models.database import add_memory
        
        for mem in self.long_term:
            # 只有新记忆才保存
            add_memory(user_id, mem.content, persona_id, mem.importance, mem.is_pinned)
    
    def should_forget(self) -> bool:
        """判断是否应该遗忘一些不重要的记忆"""
        return len(self.long_term) > 50
