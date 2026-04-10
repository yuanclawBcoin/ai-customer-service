# AI 客服系统

Telegram 个人号 AI 客服，支持人设配置、情绪系统、记忆管理。

## 功能特性

- **Telegram 个人号对接** - 使用 Pyrogram 连接真实用户账号
- **人设配置** - 自定义 AI 名称、性格、说话风格
- **情绪引擎** - 动态情绪反应，影响回复语气
- **记忆系统** - 记住用户重要信息，长期上下文
- **防检测** - 模拟打字节奏、随机表情、偶尔忽略
- **管理后台** - Web 界面配置所有设置

## 快速开始

### 1. 安装依赖

```bash
cd ai-customer-service
pip install -r requirements.txt
```

### 2. 配置系统

在管理后台（启动后访问 http://localhost:8000）配置：

- MiniMax API Key
- Telegram API ID 和 Hash（从 my.telegram.org 获取）

### 3. 启动服务

```bash
cd backend
python main.py
```

访问 http://localhost:8000 进入管理后台

## 配置说明

### MiniMax API

1. 注册 MiniMax 账号
2. 获取 API Key
3. 在管理后台的"系统设置"中填入

### Telegram API

1. 访问 https://my.telegram.org
2. 登录后进入 "API development tools"
3. 创建应用，获取 App api_id 和 api_hash
4. 在管理后台填入

### 首次使用

1. 进入"系统设置"，配置 API Key
2. 进入"人设配置"，创建 AI 人设
3. 进入"Telegram"，添加账号并连接
4. 开始聊天测试

## 项目结构

```
ai-customer-service/
├── backend/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置
│   ├── tg_client.py         # Telegram 客户端
│   ├── ai_engine/           # AI 引擎
│   │   ├── persona.py       # 人设系统
│   │   ├── memory.py         # 记忆系统
│   │   ├── emotion.py        # 情绪引擎
│   │   └── generator.py      # 回复生成
│   ├── models/              # 数据模型
│   │   └── database.py       # SQLite 操作
│   └── data/                 # 数据库文件
├── frontend/                 # Vue3 管理后台
├── nginx/                    # Nginx 配置
├── docker-compose.yml        # Docker 部署
└── README.md
```

## 使用 Docker 部署

```bash
docker-compose up -d
```

## 技术栈

- **后端**: FastAPI + Pyrogram
- **前端**: Vue3 + Element Plus
- **数据库**: SQLite
- **AI**: MiniMax API

## 注意事项

1. Telegram 个人号存在封号风险，请谨慎使用
2. 建议使用专用账号，不要使用主号
3. 定期备份会话文件和数据库
