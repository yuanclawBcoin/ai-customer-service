"""
人设系统 - 管理AI人格设定
"""
from typing import Optional, Dict
import json

class Persona:
    """AI人设"""
    
    DEFAULT_PERSONA = {
        "name": "小智",
        "gender": "未知",
        "age": "保密",
        "personality": "友好、善良、活泼",
        "speaking_style": "口语化、轻松、带点幽默",
        "expertise": "日常聊天",
        "greeting": "你好呀！有什么我可以帮你的吗？",
        "farewell": "拜拜，下次再聊~",
        "unknown_response": "嗯...这个问题有点难倒我了，换个话题吧~"
    }
    
    def __init__(self, data: Optional[Dict] = None):
        if data:
            self.__dict__.update(data)
        else:
            self.__dict__.update(self.DEFAULT_PERSONA)
        
        # 解析JSON字段
        if isinstance(self.personality, str):
            try:
                self.personality = json.loads(self.personality)
            except:
                self.personality = [p.strip() for p in self.personality.split(",")]
        
        if isinstance(self.speaking_style, str):
            try:
                self.speaking_style = json.loads(self.speaking_style)
            except:
                self.speaking_style = [p.strip() for p in self.speaking_style.split(",")]
    
    def get_system_prompt(self, emotion_style: str = "") -> str:
        """生成系统提示词"""
        personality_text = ", ".join(self.personality) if isinstance(self.personality, list) else self.personality
        style_text = ", ".join(self.speaking_style) if isinstance(self.speaking_style, list) else self.speaking_style
        
        prompt = f"""你是一个真人，正在和用户微信聊天。你的设定如下：

【身份】
- 名字：{self.name}
- 性别：{self.gender}
- 年龄：{self.age}
- 职业/领域：{self.expertise}

【性格特点】
{personality_text}

【说话风格】
{style_text}

{emotion_style}

【重要规则】
1. 像真人一样回复，不要像AI助手
2. 可以用表情符号，但不要太多
3. 不要每次都自我介绍，除非对方问你是谁
4. 消息要简短，一般1-3句话
5. 可以适当转移话题
6. 如果不知道就说不知道，不要编造
7. 可以用口头禅或网络用语
8. 回复要自然，不要太正式
9. 不要用"您好"这种太客套的称呼
10. 可以用"嗯嗯" "哦哦" "哈哈" 这种自然的回应

请记住这些设定，像真人一样聊天！"""
        return prompt
    
    def get_greeting(self) -> str:
        """获取开场白"""
        return self.greeting or self.DEFAULT_PERSONA["greeting"]
    
    def get_farewell(self) -> str:
        """获取结束语"""
        return self.farewell or self.DEFAULT_PERSONA["farewell"]
    
    def get_unknown_response(self) -> str:
        """获取未知问题回复"""
        return self.unknown_response or self.DEFAULT_PERSONA["unknown_response"]
    
    @staticmethod
    def get_available_personalities() -> list:
        """获取可选的性格标签"""
        return [
            "开朗", "内向", "活泼", "高冷", "毒舌", "暖男/暖女",
            "幽默", "文艺", "理性", "感性", "傲娇", "撒娇",
            "御姐", "萝莉", "大叔", "小鲜肉", "成熟", "天真"
        ]
    
    @staticmethod
    def get_available_styles() -> list:
        """获取可选的说话风格"""
        return [
            "口语化", "正式", "网络用语", "文艺小清新", "段子手",
            "简洁干练", "话多", "高冷简短", "温柔细腻", "搞怪",
            "emoji狂魔", "偶尔飙车"
        ]
