## Why

当前年俗知识问答系统仅支持命令行交互模式，用户体验有限。将系统改造为Web页面对话模式，可以提供更友好的用户界面，支持更自然的对话交互，提升用户体验和系统可访问性。

## What Changes

- 新增Web前端界面，包含聊天窗口、输入框、发送按钮等组件
- 新增后端API服务，处理Web前端的请求
- 新增会话管理功能，支持多用户并发访问
- 新增WebSocket支持，实现实时对话
- 保持原有命令行模式作为备选

## Capabilities

### New Capabilities
- `web-chat-interface`: 提供Web页面对话功能，支持实时聊天和多轮对话
- `rest-api`: 提供RESTful API接口，供Web前端调用
- `session-management`: 管理用户会话，支持多用户并发访问

### Modified Capabilities
- `chinese-new-year-customs-qa`: 扩展问答功能，支持通过API调用

## Impact

- 受影响的代码：新增`web/`目录包含前端代码，新增`api/`目录包含后端API
- 新增依赖：Flask/FastAPI（后端）、HTML/CSS/JavaScript（前端）
- 需要配置Web服务器部署
- 性能影响：Web模式需要处理HTTP请求和WebSocket连接