## 为什么

当前年俗知识问答系统在知识库中找不到答案时，只能返回固定的"抱歉，我暂时没有关于这个问题的信息。"，用户体验较差。通过集成LLM后端，可以在知识库中找不到答案时，调用LLM生成回答，提高系统的覆盖范围和用户体验。

## 变更内容

- 添加LLM后端集成模块，支持调用OpenAI API
- 修改RAG流程，当知识库检索结果为空时，调用LLM生成回答
- 实现LLM回答的质量控制和过滤
- 添加LLM配置管理，支持API密钥和模型参数配置

## 功能 (Capabilities)

### 新增功能
- `llm-backend`: 提供LLM后端集成功能，支持调用OpenAI API生成回答

### 修改功能
- `chinese-new-year-customs-qa`: 修改年俗知识问答功能，添加LLM后端回退机制

## 影响

- 受影响的代码：`src/rag_controller.py`、`src/answer_generator.py`
- 新增依赖：OpenAI Python SDK
- 系统配置：需要添加OpenAI API密钥配置
- 性能影响：调用LLM可能会增加响应时间