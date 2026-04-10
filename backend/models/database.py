import sqlite3
import os
from datetime import datetime
from typing import List, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "ai客服.db")

def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    
    # 系统配置表
    c.execute("""CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY,
        value TEXT
    )""")
    
    # AI 人设表
    c.execute("""CREATE TABLE IF NOT EXISTS personas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        gender TEXT DEFAULT '未知',
        age TEXT DEFAULT '未知',
        personality TEXT DEFAULT '',
        speaking_style TEXT DEFAULT '',
        expertise TEXT DEFAULT '',
        greeting TEXT DEFAULT '',
        farewell TEXT DEFAULT '',
        unknown_response TEXT DEFAULT '',
        habits TEXT DEFAULT '[]',
        favorite_emoji TEXT DEFAULT '[]',
        speaking_speed TEXT DEFAULT 'normal',
        message_length TEXT DEFAULT 'short',
        status TEXT DEFAULT 'active',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # 添加新字段（如果不存在）
    try:
        c.execute("ALTER TABLE personas ADD COLUMN habits TEXT DEFAULT '[]'")
    except:
        pass
    try:
        c.execute("ALTER TABLE personas ADD COLUMN favorite_emoji TEXT DEFAULT '[]'")
    except:
        pass
    try:
        c.execute("ALTER TABLE personas ADD COLUMN speaking_speed TEXT DEFAULT 'normal'")
    except:
        pass
    try:
        c.execute("ALTER TABLE personas ADD COLUMN message_length TEXT DEFAULT 'short'")
    except:
        pass
    
    # 对话记录表
    c.execute("""CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        platform TEXT DEFAULT 'telegram',
        persona_id INTEGER,
        messages TEXT DEFAULT '[]',
        status TEXT DEFAULT 'active',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    
    # 记忆表
    c.execute("""CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        persona_id INTEGER,
        content TEXT NOT NULL,
        category TEXT DEFAULT 'general',
        importance TEXT DEFAULT 'normal',
        is_pinned INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        expires_at TEXT
    )""")
    
    # 添加category列（如果不存在）
    try:
        c.execute("ALTER TABLE memories ADD COLUMN category TEXT DEFAULT 'general'")
    except:
        pass

    # 话题追踪表
    c.execute("""CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        persona_id INTEGER,
        topic TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, persona_id, topic)
    )""")

    # 情绪状态表
    c.execute("""CREATE TABLE IF NOT EXISTS emotions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        persona_id INTEGER,
        emotion TEXT DEFAULT 'neutral',
        intensity INTEGER DEFAULT 50,
        triggered_by TEXT DEFAULT '',
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    
    # Telegram 账号表
    c.execute("""CREATE TABLE IF NOT EXISTS tg_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        session_file TEXT DEFAULT '',
        phone TEXT DEFAULT '',
        api_id INTEGER,
        api_hash TEXT DEFAULT '',
        status TEXT DEFAULT 'offline',
        persona_id INTEGER,
        auto_reply INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    
    conn.commit()
    conn.close()
    print(f"数据库初始化完成: {DB_PATH}")

# 配置相关
def get_config(key: str, default: str = "") -> str:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT value FROM config WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row["value"] if row else default

def set_config(key: str, value: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

# 人设相关
def get_personas() -> List[dict]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM personas ORDER BY created_at DESC")
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows

def get_persona(id: int) -> Optional[dict]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM personas WHERE id = ?", (id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def create_persona(data: dict) -> int:
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT INTO personas (name, gender, age, personality, speaking_style,
                 expertise, greeting, farewell, unknown_response, habits, favorite_emoji,
                 speaking_speed, message_length)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (data["name"], data.get("gender", "未知"), data.get("age", "未知"),
               data.get("personality", ""), data.get("speaking_style", ""),
               data.get("expertise", ""), data.get("greeting", ""),
               data.get("farewell", ""), data.get("unknown_response", ""),
               data.get("habits", "[]"), data.get("favorite_emoji", "[]"),
               data.get("speaking_speed", "normal"), data.get("message_length", "short")))
    conn.commit()
    conn.close()
    return c.lastrowid

def update_persona(id: int, data: dict):
    conn = get_conn()
    c = conn.cursor()
    fields = ["name", "gender", "age", "personality", "speaking_style",
              "expertise", "greeting", "farewell", "unknown_response", "status",
              "habits", "favorite_emoji", "speaking_speed", "message_length"]
    for field in fields:
        if field in data:
            c.execute(f"UPDATE personas SET {field} = ? WHERE id = ?", (data[field], id))
    conn.commit()
    conn.close()

# 对话相关
def get_conversation(user_id: str, platform: str = "telegram") -> Optional[dict]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT * FROM conversations WHERE user_id = ? AND platform = ? 
                 AND status = 'active' ORDER BY updated_at DESC LIMIT 1""",
              (user_id, platform))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def save_conversation(user_id: str, platform: str, messages: list, persona_id: int = None):
    import json
    conn = get_conn()
    c = conn.cursor()
    msg_str = json.dumps(messages, ensure_ascii=False)
    
    # 查找是否存在
    c.execute("SELECT id FROM conversations WHERE user_id = ? AND platform = ? AND status = 'active'",
              (user_id, platform))
    row = c.fetchone()
    
    if row:
        c.execute("""UPDATE conversations SET messages = ?, updated_at = CURRENT_TIMESTAMP 
                     WHERE id = ?""", (msg_str, row["id"]))
    else:
        c.execute("""INSERT INTO conversations (user_id, platform, messages, persona_id)
                     VALUES (?, ?, ?, ?)""", (user_id, platform, msg_str, persona_id))
    conn.commit()
    conn.close()

# 记忆相关
def get_memories(user_id: str, persona_id: int = None) -> List[dict]:
    conn = get_conn()
    c = conn.cursor()
    if persona_id:
        c.execute("""SELECT * FROM memories WHERE user_id = ? AND persona_id = ?
                     ORDER BY is_pinned DESC, created_at DESC""", (user_id, persona_id))
    else:
        c.execute("""SELECT * FROM memories WHERE user_id = ?
                     ORDER BY is_pinned DESC, created_at DESC""", (user_id,))
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows

def add_memory(user_id: str, content: str, persona_id: int = None,
              importance: str = "normal", is_pinned: bool = False):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT INTO memories (user_id, persona_id, content, importance, is_pinned)
                 VALUES (?, ?, ?, ?, ?)""", (user_id, persona_id, content, importance, 1 if is_pinned else 0))
    conn.commit()
    conn.close()

def save_user_memory(user_id: str, persona_id: int, memory):
    """保存从AI提取的用户记忆（按类别去重）"""
    conn = get_conn()
    c = conn.cursor()

    # 检查是否已存在相似记忆
    content = memory.content if hasattr(memory, 'content') else str(memory)
    category = getattr(memory, 'category', 'general')
    importance = getattr(memory, 'importance', 'normal')

    # 对于重要类别（name, preference, fact），同类别只保留一条
    if category in ['name', 'preference', 'fact']:
        # 检查是否已存在同类别记忆
        c.execute("""SELECT id, content FROM memories
                     WHERE user_id = ? AND persona_id = ? AND category = ?""",
                  (user_id, persona_id, category))
        existing = c.fetchone()

        if existing:
            # 更新旧记忆
            c.execute("""UPDATE memories SET content = ?, importance = ?, created_at = CURRENT_TIMESTAMP
                         WHERE id = ?""", (content, importance, existing[0]))
        else:
            # 插入新记忆
            c.execute("""INSERT INTO memories (user_id, persona_id, content, category, importance)
                         VALUES (?, ?, ?, ?, ?)""",
                      (user_id, persona_id, content, category, importance))
    else:
        # 其他类别用内容匹配去重
        c.execute("SELECT id FROM memories WHERE user_id = ? AND content = ?", (user_id, content))
        existing = c.fetchone()

        if not existing:
            c.execute("""INSERT INTO memories (user_id, persona_id, content, category, importance)
                         VALUES (?, ?, ?, ?, ?)""",
                      (user_id, persona_id, content, category, importance))

    conn.commit()
    conn.close()

# 话题相关
def save_topic(user_id: str, topic: str, persona_id: int = None):
    """保存用户讨论过的话题"""
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("""INSERT OR IGNORE INTO topics (user_id, persona_id, topic)
                     VALUES (?, ?, ?)""",
                  (user_id, persona_id, topic))
        conn.commit()
    except:
        pass
    conn.close()

def get_topics(user_id: str, persona_id: int = None) -> List[str]:
    """获取用户讨论过的话题列表"""
    conn = get_conn()
    c = conn.cursor()
    if persona_id:
        c.execute("""SELECT topic FROM topics WHERE user_id = ? AND persona_id = ?
                     ORDER BY created_at DESC""", (user_id, persona_id))
    else:
        c.execute("""SELECT topic FROM topics WHERE user_id = ?
                     ORDER BY created_at DESC""", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

# 情绪相关
def get_emotion(user_id: str, persona_id: int = None) -> dict:
    conn = get_conn()
    c = conn.cursor()
    if persona_id:
        c.execute("""SELECT * FROM emotions WHERE user_id = ? AND persona_id = ?
                     ORDER BY updated_at DESC LIMIT 1""", (user_id, persona_id))
    else:
        c.execute("""SELECT * FROM emotions WHERE user_id = ?
                     ORDER BY updated_at DESC LIMIT 1""", (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else {"emotion": "neutral", "intensity": 50}

def update_emotion(user_id: str, emotion: str, intensity: int, 
                   triggered_by: str, persona_id: int = None):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT OR REPLACE INTO emotions (user_id, persona_id, emotion, intensity, triggered_by, updated_at)
                 VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
              (user_id, persona_id, emotion, intensity, triggered_by))
    conn.commit()
    conn.close()

# Telegram 账号相关
def get_tg_accounts() -> List[dict]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM tg_accounts ORDER BY created_at DESC")
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows

def add_tg_account(data: dict) -> int:
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT INTO tg_accounts (name, session_file, phone, api_id, api_hash, persona_id)
                 VALUES (?, ?, ?, ?, ?, ?)""",
              (data["name"], data.get("session_file", ""), data.get("phone", ""),
               data.get("api_id", 0), data.get("api_hash", ""), data.get("persona_id")))
    conn.commit()
    conn.close()
    return c.lastrowid

def update_tg_account(id: int, data: dict):
    conn = get_conn()
    c = conn.cursor()
    fields = ["name", "session_file", "phone", "api_id", "api_hash", "status", "persona_id", "auto_reply"]
    for field in fields:
        if field in data:
            c.execute(f"UPDATE tg_accounts SET {field} = ? WHERE id = ?", (data[field], id))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
