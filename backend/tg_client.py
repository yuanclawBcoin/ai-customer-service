"""
Telegram 客户端 - 支持 Web 验证码流程
"""
import asyncio
import os
from typing import Optional, Dict
from pyrogram import Client
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

import sys
import os as os_module
sys.path.insert(0, os_module.path.dirname(os_module.path.dirname(os_module.path.abspath(__file__))))

from config import settings
from models.database import get_config, get_persona, update_emotion

class PendingAuth:
    """待验证的认证状态"""
    def __init__(self):
        self.phone_code_hash: Optional[str] = None
        self.phone_number: Optional[str] = None

# 全局认证状态管理
_pending_auth: Dict[int, PendingAuth] = {}

class TelegramClient:
    """Telegram 个人号客户端"""
    
    def __init__(self, account_id: int):
        self.account_id = account_id
        self.client: Optional[Client] = None
        self.running = False
        self._connected = False
        
        # 加载配置
        self.api_id = int(get_config("tg_api_id", str(settings.tg_api_id))) or settings.tg_api_id
        self.api_hash = get_config("tg_api_hash", settings.tg_api_hash) or settings.tg_api_hash
        self.session_name = f"tg_account_{account_id}"
        
        # 检查是否有现成的 session 文件
        self.session_path = os.path.join(settings.database_url.replace("sqlite:///", "").replace(".db", ""), "..", "sessions", f"{self.session_name}.session")
        if not os.path.exists(self.session_path):
            # 尝试在 backend/sessions 目录
            alt_path = os.path.join(os_module.path.dirname(os_module.path.abspath(__file__)), "..", "sessions", f"{self.session_name}.session")
            if os.path.exists(alt_path):
                self.session_path = alt_path
            else:
                sessions_dir = os.path.join(os_module.path.dirname(os_module.path.abspath(__file__)), "..", "sessions")
                os.makedirs(sessions_dir, exist_ok=True)
                self.session_path = os.path.join(sessions_dir, f"{self.session_name}.session")
    
    async def send_code(self, phone_number: str) -> dict:
        """发送验证码"""
        try:
            # 创建临时客户端
            self.client = Client(
                self.session_name,
                api_id=self.api_id,
                api_hash=self.api_hash,
                in_memory=True  # 内存模式，不立即创建文件
            )
            
            await self.client.connect()
            
            # 发送验证码
            sent_code = await self.client.send_code(phone_number)
            
            # 保存认证状态
            if self.account_id not in _pending_auth:
                _pending_auth[self.account_id] = PendingAuth()
            _pending_auth[self.account_id].phone_code_hash = sent_code.phone_code_hash
            _pending_auth[self.account_id].phone_number = phone_number
            
            await self.client.disconnect()
            
            return {"success": True, "need_verify": True, "message": "验证码已发送"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def verify_code(self, code: str, password: str = None) -> dict:
        """验证验证码（可能需要2FA密码）"""
        try:
            auth = _pending_auth.get(self.account_id)
            if not auth or not auth.phone_code_hash:
                return {"success": False, "error": "请先发送验证码"}

            # 创建客户端并验证
            self.client = Client(
                self.session_name,
                api_id=self.api_id,
                api_hash=self.api_hash
            )

            await self.client.connect()

            # 尝试登录
            if password:
                # 有2FA密码的情况
                await self.client.sign_in(
                    phone_number=auth.phone_number,
                    phone_code_hash=auth.phone_code_hash,
                    phone_code=code,
                    password=password
                )
            else:
                try:
                    await self.client.sign_in(
                        phone_number=auth.phone_number,
                        phone_code_hash=auth.phone_code_hash,
                        phone_code=code
                    )
                except Exception as e:
                    # 检查是否需要2FA密码
                    error_str = str(e).lower()
                    if "password" in error_str or "2fa" in error_str or "two-factor" in error_str:
                        return {"success": False, "need_2fa": True, "error": "请输入2FA密码"}
                    raise

            # 保存 session 文件
            self.client.save_session()
            self._connected = True
            self.running = True

            # 清理待验证状态
            if self.account_id in _pending_auth:
                del _pending_auth[self.account_id]

            return {"success": True, "message": "登录成功"}

        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def check_session(self) -> bool:
        """检查是否有有效的 session"""
        try:
            if not self.api_id or not self.api_hash:
                return False
            
            self.client = Client(
                self.session_name,
                api_id=self.api_id,
                api_hash=self.api_hash
            )
            
            await self.client.connect()
            
            # 检查是否已授权
            if self.client.get_me():
                self._connected = True
                self.running = True
                return True
            
            return False
        except Exception:
            return False
        finally:
            if self.client:
                await self.client.disconnect()
    
    async def start(self):
        """启动客户端（有 session 文件时直接启动）"""
        if not self.api_id or not self.api_hash:
            print(f"[TG-{self.account_id}] 未配置 API ID/Hash")
            return False
        
        try:
            # 尝试直接启动（如果有 session）
            self.client = Client(
                self.session_name,
                api_id=self.api_id,
                api_hash=self.api_hash
            )
            
            await self.client.start()
            self._connected = True
            self.running = True
            print(f"[TG-{self.account_id}] Telegram 已连接")
            return True
            
        except Exception as e:
            print(f"[TG-{self.account_id}] 连接失败: {e}")
            return False
    
    async def stop(self):
        """停止客户端"""
        self.running = False
        if self.client and self.client.is_connected:
            await self.client.stop()
        self._connected = False
        print(f"[TG-{self.account_id}] Telegram 已断开")
    
    async def restart(self):
        """重启客户端"""
        await self.stop()
        await asyncio.sleep(1)
        await self.start()


# 全局客户端管理器
_clients: dict[int, TelegramClient] = {}

async def start_all_clients():
    """启动所有配置的 Telegram 账号"""
    from models.database import get_tg_accounts
    
    accounts = get_tg_accounts()
    for account in accounts:
        if account.get("status") == "active":
            client = TelegramClient(account["id"])
            success = await client.start()
            if success:
                _clients[account["id"]] = client

async def stop_all_clients():
    """停止所有客户端"""
    for client in _clients.values():
        await client.stop()
    _clients.clear()

def get_client(account_id: int) -> Optional[TelegramClient]:
    return _clients.get(account_id)

def set_client(account_id: int, client: TelegramClient):
    _clients[account_id] = client
