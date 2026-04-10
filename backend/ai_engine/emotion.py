"""
情绪引擎 - 双向情绪系统
"""
import random
from typing import Dict, Optional

class EmotionEngine:
    """情绪引擎 - 分析用户情绪，影响AI回复"""
    
    # 情绪词汇
    POSITIVE_WORDS = ["开心", "高兴", "哈哈", "哈哈哈", "爱你", "喜欢", "棒", "赞", "好开心", "笑死", "太棒了"]
    NEGATIVE_WORDS = ["生气", "愤怒", "讨厌", "滚", "烦", "不爽", "难过", "伤心", "讨厌", "啧", "切"]
    NEUTRAL_WORDS = ["嗯", "哦", "好吧", "这样啊", "好吧"]
    
    # AI情绪状态
    AI_EMOTIONS = ["happy", "calm", "playful", "shy", "cold", "annoyed"]
    
    def __init__(self):
        self.current_emotion = "calm"  # 用户当前情绪
        self.emotion_history = []  # 情绪历史
        self.intensity = 0  # 情绪强度 0-10
        self.ai_emotion = "happy"  # AI自己的情绪
        self.reply_count = 0  # 连续回复计数
    
    def analyze_text(self, text: str) -> str:
        """分析文本情绪"""
        text_lower = text.lower()
        
        # 检查正面情绪
        positive_count = sum(1 for word in self.POSITIVE_WORDS if word in text)
        # 检查负面情绪
        negative_count = sum(1 for word in self.NEGATIVE_WORDS if word in text)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        return "neutral"
    
    def update(self, text: str):
        """更新情绪状态"""
        emotion = self.analyze_text(text)
        self.current_emotion = emotion
        
        # 记录情绪历史
        self.emotion_history.append(emotion)
        if len(self.emotion_history) > 10:
            self.emotion_history.pop(0)
        
        # 根据情绪更新AI状态
        self._update_ai_emotion(emotion)
    
    def _update_ai_emotion(self, user_emotion: str):
        """根据用户情绪更新AI情绪（双向互动）"""
        if user_emotion == "negative":
            # 用户生气，AI收敛一点
            if random.random() < 0.3:
                self.ai_emotion = "cold"
            else:
                self.ai_emotion = "calm"
        elif user_emotion == "positive":
            # 用户开心，AI也开心
            if random.random() < 0.5:
                self.ai_emotion = "happy"
            else:
                self.ai_emotion = "playful"
        else:
            # 中性情绪，AI随机状态
            self.ai_emotion = random.choice(["happy", "calm", "playful"])
    
    def get_ai_emotion(self) -> str:
        """获取AI当前情绪"""
        return self.ai_emotion
    
    def should_ignore(self) -> bool:
        """判断是否应该忽略不回复（模拟真人看心情）"""
        # 连续回复太多次，偶尔不回复
        self.reply_count += 1
        
        # 每20条消息有1次概率不回复（看心情）
        if self.reply_count > 5 and random.random() < 0.05:
            self.reply_count = 0
            return True
        
        # 用户情绪非常激动时，有20%概率不回复
        if self.current_emotion == "negative" and random.random() < 0.2:
            return True
        
        return False
    
    def get_style_modifier(self) -> str:
        """获取风格修饰词"""
        modifiers = {
            "positive": "用户现在很开心，你可以更活泼一点，多用'哈哈哈'",
            "negative": "用户情绪不好，说话要小心一点，别太放肆",
            "neutral": "正常聊天就行"
        }
        return modifiers.get(self.current_emotion, "")
    
    def get_typing_delay(self) -> float:
        """获取打字延迟（秒）"""
        base_delay = 0.5
        
        # 情绪影响延迟
        if self.current_emotion == "positive":
            # 开心回复快一点
            return base_delay + random.uniform(0.3, 1.5)
        elif self.current_emotion == "negative":
            # 生气回复慢一点（思考一下）
            return base_delay + random.uniform(1.0, 2.5)
        else:
            return base_delay + random.uniform(0.5, 2.0)
    
    def simulate_typo(self, text: str) -> str:
        """模拟真人偶尔打错字（5%概率）"""
        if random.random() > 0.05 or len(text) < 5:
            return text
        
        # 随机选一个位置打错
        idx = random.randint(0, min(len(text) - 1, 20))
        chars = list(text)
        
        # 常见错字
        typo_options = [
            ("啊", "阿"),
            ("的", "得"),
            ("在", "再"),
            ("吧", "呗"),
            ("吗", "嘛"),
        ]
        
        char = chars[idx]
        for correct, wrong in typo_options:
            if char == correct:
                chars[idx] = wrong
                # 添加纠正
                correction = f"（{correct}不对，是{wrong}）"
                return ''.join(chars) + correction
        
        return text
    
    def get_ai_personality_hint(self) -> str:
        """获取AI性格提示"""
        hints = {
            "happy": "你现在心情很好，可以更放开一点",
            "calm": "你现在比较平静，正常聊天",
            "playful": "你现在有点调皮，可以开玩笑",
            "shy": "你现在有点害羞，说话谨慎一点",
            "cold": "你现在比较冷淡，别太热情",
            "annoyed": "你有点烦躁，注意态度"
        }
        return hints.get(self.ai_emotion, "")
