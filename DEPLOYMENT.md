# LLM 后端部署指南

## 概述

本文档提供中国年俗知识问答系统 LLM 后端集成的部署说明。当知识库检索无法回答问题时，LLM 后端会使用 OpenAI API 生成答案。

## 前置条件

### 软件要求
- Python 3.7+
- pip（Python 包管理器）

### 依赖安装
- OpenAI Python SDK
  ```bash
  pip install openai
  ```
  或
  ```bash
  pip install -r requirements.txt
  ```

## 配置

### 1. API Key 配置

#### 方式一：环境变量（推荐）
设置 OpenAI API Key 为环境变量：

**Windows（命令提示符）：**
```cmd
set OPENAI_API_KEY=your-api-key-here
```

**Windows（PowerShell）：**
```powershell
$env:OPENAI_API_KEY="your-api-key-here"
```

**Linux/Mac：**
```bash
export OPENAI_API_KEY=your-api-key-here
```

#### 方式二：配置文件
不推荐用于生产环境，但可用于开发：

编辑 `config.json` 文件，添加 API Key：
```json
{
  "api_key": "your-api-key-here",
  "model": "gpt-3.5-turbo",
  "temperature": 0.7,
  "max_tokens": 150,
  "top_p": 1.0,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0
}
```

**注意：** 如果环境变量和配置文件都包含 API Key，环境变量优先。

### 2. 自定义 LLM API 端点配置

如果你使用自托管 LLM（如 llama.cpp、vLLM 或其他 OpenAI 兼容 API），需要配置 API 基础 URL：

#### 方式一：环境变量
```cmd
# Windows（命令提示符）
set OPENAI_API_BASE=http://localhost:8000/v1

# Windows（PowerShell）
$env:OPENAI_API_BASE="http://localhost:8000/v1"

# Linux/Mac
export OPENAI_API_BASE=http://localhost:8000/v1
```

#### 方式二：配置文件
在 `config.json` 中添加 `api_base` 字段：
```json
{
  "api_key": "your-api-key-here",
  "api_base": "http://localhost:8000/v1",
  "model": "gpt-3.5-turbo",
  "temperature": 0.7,
  "max_tokens": 150,
  "top_p": 1.0,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0
}
```

**常见的自托管 LLM API 端点：**
- **llama.cpp（OpenAI 兼容模式）：** `http://localhost:8000/v1`
- **vLLM：** `http://localhost:8000/v1`
- **text-generation-inference：** `http://localhost:8080/v1`
- **LocalAI：** `http://localhost:8080/v1`

**注意：** 确保你的自托管 LLM API 正在运行且可在指定端点访问。有些自托管 LLM 可能不需要 API Key，此时可将 `api_key` 设置为任意非空字符串。

### 3. 模型配置

编辑 `config.json` 文件自定义 LLM 参数：

- **model**：要使用的 OpenAI 模型（如 "gpt-3.5-turbo"、"gpt-4"）
- **temperature**：控制随机性（0.0-2.0，数值越高越随机）
- **max_tokens**：生成的最大 token 数
- **top_p**：控制多样性（0.0-1.0，数值越低越专注）
- **frequency_penalty**：惩罚高频 token
- **presence_penalty**：惩罚新 token

## 部署步骤

1. **克隆仓库**：
   ```bash
   git clone <repository-url>
   cd chinese-new-year-customs-qa
   ```

2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

3. **配置 API Key**：
   按照上述 API Key 配置说明进行操作。

4. **测试集成**：
   ```bash
   python test_llm_integration.py
   ```

5. **运行系统**：
   ```bash
   python src/main.py
   ```

## 使用方法

### 基本用法
1. 启动系统：
   ```bash
   python src/main.py
   ```

2. 输入关于中国年俗的问题：
   ```
   你问：为啥要倒贴福？
   我答：倒贴福字是因为'倒'和'到'谐音，寓意着福到了，是一种吉祥的象征呢。

   你问：圣诞节在中国有什么习俗？
   我答：在中国，圣诞节虽然不是传统节日，但现在很多年轻人也会庆祝。常见的习俗包括：装饰圣诞树、互赠礼物、吃圣诞大餐、参加派对等。一些商场和餐厅也会推出圣诞主题的活动和装饰，营造节日氛围呢。
   ```

### 多轮对话
系统支持追问：
```
你问：为啥要倒贴福？
我答：倒贴福字是因为'倒'和'到'谐音，寓意着福到了，是一种吉祥的象征呢。

你问：那福字什么时候贴？
我答：福字通常在春节前贴，一般是腊月二十八或二十九，象征着迎接新年的福气呢。
```

## 监控与维护

### 监控
LLM 后端内置以下监控功能：
- API 调用次数
- 使用的总 token 数
- 预估成本
- 平均响应时间

查看监控统计：
```python
from src.rag_controller import RAGController

rag = RAGController("openspec/knowledge-base.json")
if rag.llm_enabled:
    stats = rag.llm_backend.get_monitoring_stats()
    print(stats)
```

### 成本控制
控制 API 成本的方法：
1. 使用 `gpt-3.5-turbo` 而非 `gpt-4` 以降低成本
2. 减小 `max_tokens` 以限制响应长度
3. 在公开部署环境中实施限流

### 故障排除

#### 常见问题

1. **API Key 错误**：
   ```
   ValueError: OPENAI_API_KEY environment variable is not set
   ```
   **解决方案：** 设置 OPENAI_API_KEY 环境变量。

2. **API 连接错误**：
   ```
   openai.error.APIConnectionError: Error communicating with OpenAI
   ```
   **解决方案：** 检查网络连接，确保 API Key 有效。

3. **API 速率限制错误**：
   ```
   openai.error.RateLimitError: You exceeded your current quota
   ```
   **解决方案：** 检查 OpenAI 账户配额和账单设置。

4. **LLM 后端禁用**：
   ```
   LLM backend initialization failed: OPENAI_API_KEY environment variable is not set
   ```
   **解决方案：** 设置 OPENAI_API_KEY 环境变量。系统将继续仅使用知识库。

## 安全注意事项

### 最佳实践
- 切勿在代码中硬编码 API Key
- 对敏感信息使用环境变量
- 实施限流以防止滥用
- 监控 API 使用情况以检测异常活动
- 定期轮换 API Key

### 生产环境部署
生产环境部署建议：
1. 使用密钥管理服务而非环境变量
2. 为问答系统实施身份验证
3. 设置 API 使用监控和告警
4. 考虑使用代理服务器增加安全层

## 性能优化

### 响应时间
提升响应时间的方法：
1. 使用 `gpt-3.5-turbo` 以获得更快响应
2. 减小 `max_tokens` 以限制生成时间
3. 为常见问题实施缓存

### 准确度
提升答案准确度的方法：
1. 使用 `gpt-4` 以获得更准确响应（成本更高）
2. 在 `llm_backend.py` 中微调提示词
3. 在系统消息中添加更具体的说明

## 总结

LLM 后端集成通过回答知识库未涵盖的问题，增强了中国年俗知识问答系统的功能。按照本部署指南操作，你可以成功配置和部署具有 LLM 能力的系统。

如有问题或疑问，请参阅 OpenAI 文档或联系系统管理员。