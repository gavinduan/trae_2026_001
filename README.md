# 中国年俗知识问答系统

一个基于 RAG（检索增强生成）技术的中国年俗知识问答聊天机器人。

## 功能特性

- **智能问答**：回答关于中国春节、元宵节等传统节日的问题
- **流式输出**：支持打字机效果的流式响应
- **多轮对话**：支持上下文理解的连续对话
- **Markdown 渲染**：支持 Markdown 格式输出
- **Thinking 过滤**：自动过滤思维区块内容
- **快捷入口**：左侧边栏提供常见问题快速提问
- **会话管理**：支持会话历史记录和清除

## 技术栈

### 后端
- **Python 3.7+**
- **Flask** - Web 框架
- **Flask-SocketIO** - WebSocket 支持
- **OpenAI API** - LLM 能力集成

### 前端
- **HTML5/CSS3** - 页面结构与样式
- **JavaScript (ES6+)** - 交互逻辑
- **Socket.IO** - 实时通信
- **Marked.js** - Markdown 渲染

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/gavinduan/trae_2026_001.git
cd trae_2026_001
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API Key

复制配置文件模板并编辑：

```bash
cp config.json.example config.json
```

编辑 `config.json`，填入你的 OpenAI API Key：

```json
{
  "api_key": "your-api-key-here",
  "model": "gpt-3.5-turbo",
  "temperature": 0.7,
  "max_tokens": 150
}
```

或者使用环境变量（推荐）：

```bash
# Linux/Mac
export OPENAI_API_KEY=your-api-key-here

# Windows (PowerShell)
$env:OPENAI_API_KEY="your-api-key-here"
```

### 4. 启动服务

```bash
python web_server.py
```

服务启动后，访问 http://localhost:5000/

## 项目结构

```
├── web_server.py          # Web 服务器入口
├── src/
│   ├── llm_backend.py     # OpenAI LLM 后端集成
│   ├── rag_controller.py  # RAG 控制器
│   ├── answer_generator.py
│   ├── knowledge_retriever.py
│   ├── question_processor.py
│   └── dialogue_manager.py
├── web/
│   ├── index.html         # 主页面
│   ├── js/
│   │   └── chat.js        # 前端聊天逻辑
│   └── css/
│       └── style.css      # 样式表
├── openspec/              # OpenSpec 规范文档
├── DEPLOYMENT.md          # LLM 后端部署文档
├── WEB_DEPLOYMENT.md      # Web 界面部署文档
└── config.json.example    # 配置文件模板
```

## 使用示例

### 询问年俗问题

```
用户：为啥要倒贴福？
助手：倒贴福字是因为"倒"和"到"谐音，寓意着福到了，是一种吉祥的象征呢。

用户：那福字什么时候贴？
助手：福字通常在春节前贴，一般是腊月二十八或二十九，象征着迎接新年的福气呢。
```

### 可用快捷话题

- 倒贴福
- 守岁
- 压岁钱
- 放鞭炮
- 年夜饭
- 庙会
- 舞龙舞狮
- 元宵节

## API 接口

### REST API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/chat` | POST | 发送消息（HTTP 方式） |
| `/api/history/<session_id>` | GET | 获取对话历史 |
| `/api/sessions` | GET | 列出所有活跃会话 |

### WebSocket 事件

| 事件 | 方向 | 说明 |
|------|------|------|
| `user_message` | 客户端→服务器 | 发送用户消息 |
| `bot_message` | 服务器→客户端 | 机器人回复（非流式） |
| `bot_stream_chunk` | 服务器→客户端 | 流式输出片段 |
| `typing` | 服务器→客户端 | 打字指示器 |
| `clear_history` | 客户端→服务器 | 清除对话历史 |

## 常见问题

### 1. API Key 错误
```
ValueError: OPENAI_API_KEY environment variable is not set
```
**解决方案**：确保已正确设置 OpenAI API Key。

### 2. 连接失败
如果看到"未连接"状态，检查：
- Web 服务器是否正在运行
- 浏览器控制台是否有错误
- 尝试刷新页面重新连接

### 3. 机器人无响应
- 检查终端错误日志
- 验证 LLM 后端配置
- 尝试刷新页面

## 生产环境部署

### 使用 Gunicorn

```bash
pip install gunicorn eventlet
gunicorn -k eventlet -w 1 web_server:app
```

### Docker 部署

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "web_server.py"]
```

```bash
docker build -t chinese-new-year-qa .
docker run -p 5000:5000 -e OPENAI_API_KEY=your-key chinese-new-year-qa
```

## 监控

LLM 后端内置以下监控功能：
- API 调用次数
- 使用的总 token 数
- 预估成本
- 平均响应时间

## 安全建议

- 切勿将 API Key 提交到版本控制
- 使用环境变量存储敏感信息
- 生产环境使用 HTTPS
- 实施限流防止滥用

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请通过 GitHub Issues 反馈。