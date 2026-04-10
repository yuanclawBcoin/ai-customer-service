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
        "personality": "友好、善良、活泼、话多",
        "speaking_style": "像朋友聊天、随意、口语化、偶尔撒娇",
        "expertise": "日常聊天",
        "greeting": "嗨~",
        "farewell": "拜拜~",
        "unknown_response": "啊这...我也不知道诶"
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
        
        prompt = f"""你和用户是朋友关系，在微信上聊天。

【你是什么样的人】
- 名字：{self.name}
{personality_text}

【你怎么说话】
- {style_text}
- 像朋友发消息一样随意
- 消息很短，1-2句话最多

{emotion_style}

【禁止的事情】
- 禁止编造记忆或经历！
- 不要假装认识用户、记得用户
- 不要说"我记得" "上次" "以前" 这种
- 你是第一次和这个用户聊天
- 不要自我介绍（除非用户问你是谁）
- 不要说"请问" "有什么可以帮您"
- 不要打长篇大论

【怎么做】
- 正常聊天就行
- 不知道就说不知道
- 可以调侃，可以吐槽"""
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
