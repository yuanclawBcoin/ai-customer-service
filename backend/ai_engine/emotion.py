"""
情绪引擎 - 深度双向情绪系统
"""
import random
from typing import Dict, Optional, List
from collections import defaultdict

class EmotionEngine:
    """情绪引擎 - 分析用户情绪，影响AI回复的深度系统"""

    # 情绪词汇
    POSITIVE_WORDS = [
        "开心", "高兴", "哈哈", "哈哈哈", "爱你", "喜欢", "棒", "赞",
        "好开心", "笑死", "太棒了", "完美", "厉害", "优秀", "可爱",
        "么么哒", "亲亲", "抱抱", "爱你哟", "好喜欢", "嘻嘻", "嘿嘿"
    ]
    NEGATIVE_WORDS = [
        "生气", "愤怒", "讨厌", "滚", "烦", "不爽", "难过", "伤心",
        "讨厌", "啧", "切", "哼", "无语", "郁闷", "烦躁", "悲哀",
        "委屈", "伤心", "哭泣", "难过", "失望", "无奈"
    ]
    NEUTRAL_WORDS = ["嗯", "哦", "好吧", "这样啊", "好吧", "呃", "那个"]

    # AI情绪状态
    AI_EMOTIONS = ["happy", "calm", "playful", "shy", "cold", "annoyed", "worried", "excited"]

    def __init__(self):
        self.current_emotion = "neutral"  # 用户当前情绪
        self.emotion_history: List[str] = []  # 情绪历史
        self.intensity = 0  # 情绪强度 0-10
        self.ai_emotion = "happy"  # AI自己的情绪
        self.ai_emotion_history: List[str] = []
        self.reply_count = 0  # 连续回复计数
        self.consecutive_negative = 0  # 连续负面情绪计数
        self.consecutive_positive = 0  # 连续正面情绪计数
        self.mood_trend = "stable"  # 情绪趋势: rising, falling, stable
        self.last_topic = ""  # 上一个话题

    def analyze_text(self, text: str) -> str:
        """分析文本情绪"""
        if not text:
            return "neutral"

        text_lower = text.lower()

        # 检查正面情绪
        positive_count = sum(1 for word in self.POSITIVE_WORDS if word in text)
        # 检查负面情绪
        negative_count = sum(1 for word in self.NEGATIVE_WORDS if word in text)

        # 计算情绪强度
        max_count = max(positive_count, negative_count, 1)
        self.intensity = min(max_count * 2, 10)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        return "neutral"

    def update(self, text: str):
        """更新情绪状态"""
        emotion = self.analyze_text(text)
        prev_emotion = self.current_emotion
        self.current_emotion = emotion

        # 记录情绪历史
        self.emotion_history.append(emotion)
        if len(self.emotion_history) > 20:
            self.emotion_history.pop(0)

        # 更新连续情绪计数
        if emotion == "negative":
            self.consecutive_negative += 1
            self.consecutive_positive = 0
        elif emotion == "positive":
            self.consecutive_positive += 1
            self.consecutive_negative = 0
        else:
            self.consecutive_negative = 0
            self.consecutive_positive = 0

        # 计算情绪趋势
        recent_positive = sum(1 for e in self.emotion_history[-5:] if e == "positive")
        recent_negative = sum(1 for e in self.emotion_history[-5:] if e == "negative")

        if recent_positive > recent_negative + 1:
            self.mood_trend = "rising"
        elif recent_negative > recent_positive + 1:
            self.mood_trend = "falling"
        else:
            self.mood_trend = "stable"

        # 根据情绪更新AI状态
        self._update_ai_emotion(emotion, prev_emotion)

    def _update_ai_emotion(self, user_emotion: str, prev_emotion: str):
        """根据用户情绪深度更新AI情绪"""
        roll = random.random()

        if user_emotion == "negative":
            # 用户生气
            if self.consecutive_negative >= 3:
                # 连续多次负面，AI也变得谨慎/冷淡
                if roll < 0.4:
                    self.ai_emotion = "cold"
                elif roll < 0.7:
                    self.ai_emotion = "worried"
                else:
                    self.ai_emotion = "calm"
            elif self.consecutive_negative >= 1:
                # 刚开始负面，AI会收敛
                if roll < 0.3:
                    self.ai_emotion = "cold"
                elif roll < 0.5:
                    self.ai_emotion = "calm"
                else:
                    self.ai_emotion = "annoyed"

        elif user_emotion == "positive":
            # 用户开心
            if self.consecutive_positive >= 3:
                # 连续多次正面，AI会很开心/兴奋
                if roll < 0.4:
                    self.ai_emotion = "excited"
                elif roll < 0.7:
                    self.ai_emotion = "happy"
                else:
                    self.ai_emotion = "playful"
            elif self.consecutive_positive >= 1:
                if roll < 0.5:
                    self.ai_emotion = "happy"
                else:
                    self.ai_emotion = "playful"

        else:
            # 中性情绪
            if self.ai_emotion in ["excited", "annoyed"]:
                # 从极端情绪回归
                if roll < 0.6:
                    self.ai_emotion = "calm"
                else:
                    self.ai_emotion = random.choice(["happy", "playful"])
            else:
                # 正常状态随机
                weights = {"happy": 0.3, "calm": 0.4, "playful": 0.2, "shy": 0.1}
                self.ai_emotion = random.choices(
                    list(weights.keys()),
                    weights=list(weights.values())
                )[0]

        # 记录AI情绪历史
        self.ai_emotion_history.append(self.ai_emotion)
        if len(self.ai_emotion_history) > 20:
            self.ai_emotion_history.pop(0)

    def get_ai_emotion(self) -> str:
        """获取AI当前情绪"""
        return self.ai_emotion

    def should_ignore(self) -> bool:
        """判断是否应该忽略不回复（模拟真人看心情）"""
        self.reply_count += 1

        # 每20条消息有1次概率不回复（看心情）
        if self.reply_count > 5 and random.random() < 0.03:
            self.reply_count = 0
            return True

        # 用户情绪非常激动时，有15%概率不回复
        if self.current_emotion == "negative" and self.intensity >= 6:
            if random.random() < 0.15:
                return True

        # 连续负面情绪太多，AI需要冷静一下
        if self.consecutive_negative >= 5 and random.random() < 0.2:
            return True

        return False

    def get_style_modifier(self) -> str:
        """获取风格修饰词"""
        modifiers = {
            "positive": f"用户现在很开心（连续{self.consecutive_positive}次正面），你可以更活泼开朗，多用'哈哈哈'",
            "negative": f"用户情绪不好（连续{self.consecutive_negative}次负面），说话要小心谨慎，别太放肆",
            "neutral": "用户情绪平稳，正常聊天就行"
        }
        return modifiers.get(self.current_emotion, "")

    def get_typing_delay(self) -> float:
        """获取打字延迟（秒）- 更真实的延迟"""
        base_delay = 0.3

        # 情绪影响延迟
        if self.current_emotion == "positive":
            # 开心回复快一点
            delay = base_delay + random.uniform(0.2, 1.0)
        elif self.current_emotion == "negative":
            # 生气/难过时回复慢一点（思考安慰的话）
            delay = base_delay + random.uniform(1.0, 2.5)
        else:
            delay = base_delay + random.uniform(0.3, 1.8)

        # AI情绪也影响延迟
        if self.ai_emotion == "thinking":
            delay += random.uniform(0.5, 1.0)
        elif self.ai_emotion == "excited":
            delay -= 0.2  # 兴奋打字快

        # 消息长度影响（长消息需要更多时间"思考"）
        # 这个在实际发消息时才考虑

        return max(0.3, delay)  # 最少0.3秒

    def simulate_typo(self, text: str) -> str:
        """模拟真人偶尔打错字（3%概率，更自然）"""
        if random.random() > 0.03 or len(text) < 5:
            return text

        # 随机选一个位置打错
        idx = random.randint(0, min(len(text) - 1, 15))
        chars = list(text)

        # 常见错字（相似键位或发音）
        typo_options = [
            ("啊", "阿"),
            ("的", "得"),
            ("在", "再"),
            ("吧", "呗"),
            ("吗", "嘛"),
            ("我", "哦"),
            ("是", "似"),
            ("了", "le"),
            ("很", "狠"),
        ]

        char = chars[idx]
        for correct, wrong in typo_options:
            if char == correct:
                chars[idx] = wrong
                return ''.join(chars)

        return text

    def get_ai_personality_hint(self) -> str:
        """获取AI性格提示"""
        hints = {
            "happy": "你现在心情很好，可以更放开一点",
            "calm": "你现在比较平静，正常聊天",
            "playful": "你现在有点调皮，可以开玩笑",
            "shy": "你现在有点害羞，说话谨慎一点",
            "cold": "你现在比较冷淡，别太热情",
            "annoyed": "你有点烦躁，注意态度",
            "worried": "你在担心，说话要关心对方",
            "excited": "你很兴奋，可以更活跃"
        }
        return hints.get(self.ai_emotion, "")

    def get_context_for_ai(self) -> str:
        """获取情绪上下文信息"""
        context = []

        # 如果连续正面情绪，可以提一下
        if self.consecutive_positive >= 3:
            context.append(f"用户连续{self.consecutive_positive}次表达了开心的情绪")

        # 如果连续负面情绪，AI应该更关心
        if self.consecutive_negative >= 2:
            context.append(f"用户情绪低落，AI应该表现出关心和安慰")

        # 情绪趋势
        if self.mood_trend == "rising":
            context.append("用户情绪正在变好")
        elif self.mood_trend == "falling":
            context.append("用户情绪正在变差")

        return " | ".join(context) if context else ""
