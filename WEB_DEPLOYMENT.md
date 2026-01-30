# Web 聊天界面部署指南

## 概述

本文档提供中国年俗知识问答系统 Web 聊天界面的部署说明。

## 前置条件

### 软件要求
- Python 3.7+
- pip（Python 包管理器）
- Web 浏览器（Chrome、Firefox、Safari、Edge）

### 依赖安装
安装所需依赖：
```bash
pip install -r requirements.txt
```

所需包：
- **openai** - OpenAI API 客户端
- **flask** - Web 框架
- **flask-socketio** - Flask 的 WebSocket 支持
- **eventlet** - 异步网络库

## 配置

### 1. 环境变量（推荐）
设置以下环境变量：

**Windows（PowerShell）：**
```powershell
$env:OPENAI_API_KEY="your-api-key-here"
$env:OPENAI_API_BASE="http://localhost:8000/v1"
$env:HOST="0.0.0.0"
$env:PORT="5000"
$env:DEBUG="false"
```

**Linux/Mac：**
```bash
export OPENAI_API_KEY=your-api-key-here
export OPENAI_API_BASE=http://localhost:8000/v1
export HOST=0.0.0.0
export PORT=5000
export DEBUG=false
```

### 2. 配置文件
编辑 `config.json` 文件：
```json
{
  "api_key": "your-api-key-here",
  "api_base": "http://localhost:8000/v1",
  "model": "gpt-3.5-turbo",
  "temperature": 0.7,
  "max_tokens": 150
}
```

## 部署步骤

### 1. 启动 Web 服务器
运行 Web 服务器：
```bash
python web_server.py
```

预期输出：
```
Starting Chinese New Year Customs QA Chat Server...
Server running at http://0.0.0.0:5000
Web interface: http://0.0.0.0:5000/
```

### 2. 访问 Web 界面
打开 Web 浏览器，访问：
```
http://localhost:5000/
```

或在服务器上运行时：
```
http://<server-ip>:5000/
```

## 使用方法

### 基本用法
1. 打开网页
2. 在输入框中输入问题
3. 点击发送按钮或按 Enter 键
4. 等待机器人回复

### 功能特性

#### 快捷话题
点击左侧边栏的快捷话题按钮，可快速提问关于中国年俗的常见问题。

#### 多轮对话
系统保持对话上下文，可以进行追问，例如：
- "为啥要倒贴福？"
- "那福字什么时候贴？"

#### 会话管理
- 系统自动为每个用户创建会话 ID
- 对话历史在会话期间保留
- 点击"清除历史"开始新对话

#### 连接状态
- 连接状态指示器显示 WebSocket 连接是否活跃
- 如果连接丢失，系统会自动尝试重连

## API 接口

### REST API
- `GET /api/health` - 健康检查
- `POST /api/chat` - 通过 HTTP 发送消息
- `GET /api/history/<session_id>` - 获取对话历史
- `GET /api/sessions` - 列出所有活跃会话

### WebSocket 事件
- `connect` - 连接建立
- `user_message` - 发送用户消息
- `bot_message` - 接收机器人回复
- `typing` - 打字指示器
- `disconnect` - 连接关闭
- `clear_history` - 清除对话历史

## 故障排除

### 1. 连接失败
如果看到"未连接"状态：
- 检查 Web 服务器是否运行
- 检查浏览器控制台错误
- 刷新页面重新连接

### 2. 无响应
如果机器人无响应：
- 检查终端错误消息
- 验证 LLM 后端配置正确
- 尝试刷新页面

### 3. CORS 错误
如果遇到 CORS 错误：
- 服务器已配置允许所有来源
- 如问题持续，请联系管理员

### 4. 性能问题
如果界面响应慢：
- 检查网络连接
- 减小 config 中的 `max_tokens` 设置
- 考虑使用更强大的 LLM 模型

## 生产环境部署

### 使用生产服务器
生产环境部署建议使用：
- **Gunicorn** 配合 **eventlet** 工作进程：
  ```bash
  gunicorn -k eventlet -w 1 web_server:app
  ```

### Docker 部署
创建 Dockerfile：
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "web_server.py"]
```

构建并运行：
```bash
docker build -t chinese-new-year-qa .
docker run -p 5000:5000 -e OPENAI_API_KEY=your-key chinese-new-year-qa
```

### Nginx 反向代理
配置 Nginx 作为反向代理：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 安全注意事项

### API Key 安全
- 切勿将 API Key 提交到版本控制
- 对敏感信息使用环境变量
- 定期轮换 API Key

### 网络安全
- 生产环境使用 HTTPS
- 实施限流
- 监控 API 使用

### 输入验证
- 服务器验证所有输入
- 可疑输入会被记录并拒绝

## 总结

Web 聊天界面提供了与中国年俗知识问答系统交互的友好方式。按照本部署指南操作，你可以成功部署和使用 Web 界面。

如有问题或疑问，请参阅故障排除部分或联系系统管理员。