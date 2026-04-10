"""
情绪引擎 - 管理AI的情绪状态
"""
import random
from typing import Dict

class EmotionEngine:
    # 情绪类型及强度
    EMOTIONS = {
        "happy": {"keywords": ["开心", "高兴", "哈哈", "笑", "好开心", "太棒了", "happy", "great"], "base_intensity": 70},
        "sad": {"keywords": ["难过", "伤心", "哭", "失落", "sad", "cry"], "base_intensity": 60},
        "angry": {"keywords": ["生气", "愤怒", "烦", "讨厌", "滚", "草", "fuck"], "base_intensity": 80},
        "annoyed": {"keywords": ["烦", "无语", "服了", "啥玩意", "whatever"], "base_intensity": 50},
        "surprised": {"keywords": ["卧槽", "牛", "厉害", "哇", "哇哦", "wow", "amazing"], "base_intensity": 65},
        "shy": {"keywords": ["害羞", "脸红", "不好意思", "尴尬"], "base_intensity": 55},
        "冷漠": {"keywords": ["哦", "嗯", "随便", "无所谓", "whatever"], "base_intensity": 40},
        "neutral": {"keywords": [], "base_intensity": 50}
    }
    
    # 情绪衰减率
    DECAY_RATE = 0.9
    
    def __init__(self):
        self.current_emotion = "neutral"
        self.intensity = 50
        self.history = []
    
    def analyze(self, text: str) -> tuple[str, int]:
        """分析文本，返回情绪和强度"""
        text_lower = text.lower()
        
        for emotion, data in self.EMOTIONS.items():
            if emotion == "neutral":
                continue
            for keyword in data["keywords"]:
                if keyword in text_lower:
                    # 找到关键词，返回该情绪
                    intensity = data["base_intensity"] + random.randint(-10, 10)
                    return emotion, min(100, max(20, intensity))
        
        return "neutral", 50
    
    def update(self, user_message: str):
        """根据用户消息更新情绪"""
        emotion, intensity = self.analyze(user_message)
        
        if emotion != "neutral":
            self.current_emotion = emotion
            self.intensity = intensity
            self.history.append({
                "emotion": emotion,
                "intensity": intensity,
                "triggered_by": user_message[:20]
            })
            # 保持历史记录在10条以内
            if len(self.history) > 10:
                self.history = self.history[-10:]
    
    def decay(self):
        """情绪自然衰减"""
        self.intensity = int(self.intensity * self.DECAY_RATE)
        if self.intensity < 30:
            self.current_emotion = "neutral"
    
    def get_style_modifier(self) -> str:
        """获取情绪对应的风格修饰"""
        modifiers = {
            "happy": "语气轻快活泼，带着笑意",
            "sad": "语气低沉，有些失落",
            "angry": "语气不耐烦，带着火气",
            "annoyed": "语气敷衍，略显不耐烦",
            "surprised": "语气惊讶，带着感叹",
            "shy": "语气害羞，有点扭捏",
            "冷漠": "语气冷淡，简短敷衍",
            "neutral": "语气平和，正常交流"
        }
        return modifiers.get(self.current_emotion, "语气平和")
    
    def should_ignore(self) -> bool:
        """根据情绪决定是否忽略消息（模拟真人偶尔不回复）"""
        if self.current_emotion == "angry" and self.intensity > 80:
            return random.random() < 0.15  # 15%概率不回
        return False
    
    def get_typing_delay(self) -> float:
        """获取模拟打字延迟（秒）"""
        base_delay = 1.0
        if self.current_emotion == "happy":
            base_delay = 0.8
        elif self.current_emotion == "angry":
            base_delay = 1.5  # 生气时打字更快？或者更慢？
        elif self.current_emotion == "冷漠":
            base_delay = 2.0  # 冷漠时回复慢
        return base_delay + random.uniform(0, 1.5)
