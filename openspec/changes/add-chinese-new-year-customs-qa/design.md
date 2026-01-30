# Chinese New Year Customs QA System Design

## Context
This system is designed to answer questions about Chinese New Year customs and traditions in an accurate and engaging way. It uses a RAG (Retrieval-Augmented Generation) approach to retrieve relevant information from a knowledge base and generate colloquial answers.

## Goals / Non-Goals
### Goals
- Provide accurate answers to questions about Chinese New Year customs
- Generate colloquial, easy-to-understand answers
- Support multi-turn dialogues for follow-up questions
- Be responsive and efficient

### Non-Goals
- Replace human experts on Chinese culture
- Handle questions outside the scope of Chinese New Year customs
- Provide real-time updates to the knowledge base

## System Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  User Interface │────▶│  RAG Workflow   │────▶│  Knowledge Base │
│                 │◀────│                 │◀────│                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        ▲                      │
        │                      │
        └──────────────────────┘
              Dialogue History
```

## Modules

### 1. Question Processing Module
- **Function**: Process user questions to extract key information
- **Input**: User question (text)
- **Output**: Processed query with keywords
- **Implementation**: Use natural language processing to identify important terms and intent

### 2. Knowledge Retrieval Module
- **Function**: Retrieve relevant information from the knowledge base
- **Input**: Processed query
- **Output**: Top N most relevant knowledge entries
- **Implementation**: Use keyword matching and semantic similarity to rank knowledge entries

### 3. Answer Generation Module
- **Function**: Generate colloquial answers based on retrieved information
- **Input**: Retrieved knowledge entries + Dialogue history (for multi-turn)
- **Output**: Colloquial answer
- **Implementation**: Use language model to generate natural-sounding answers

### 4. Dialogue Management Module
- **Function**: Manage dialogue history and context
- **Input**: User questions and system answers
- **Output**: Updated dialogue history
- **Implementation**: Store dialogue history in memory and use it to contextualize follow-up questions

## Data Flow

1. **User asks a question**: "为啥要倒贴福？"
2. **Question processing**: Extract keywords "倒贴福" and intent to understand the reason
3. **Knowledge retrieval**: Find relevant entries about "贴福字" from the knowledge base
4. **Answer generation**: Generate a colloquial answer explaining the reason for inverted fu characters
5. **System responds**: "倒贴福字是因为'倒'和'到'谐音，寓意着福到了，是一种吉祥的象征。"
6. **User asks a follow-up**: "那福字什么时候贴？"
7. **Question processing with context**: Understand this is about the timing of贴福字
8. **Knowledge retrieval**: Find relevant information about the timing of贴福字
9. **Answer generation with context**: Generate an answer about when to贴福字
10. **System responds**: "福字通常在春节前贴，一般是腊月二十八或二十九，象征着迎接新年的福气。"

## Knowledge Base Structure

The knowledge base is stored in JSON format with the following structure:

```json
{
  "version": "1.0",
  "data": [
    {
      "id": "fu-character",
      "title": "贴福字",
      "description": "贴福字是中国春节的传统习俗之一...",
      "keywords": ["福字", "贴福", "倒贴福", "福气", "好运"],
      "scenarios": ["春节前贴福字", "倒贴福字寓意", "福字的位置选择"],
      "related": ["spring-festival", "couplets", "door-gods"]
    },
    // More entries...
  ]
}
```

## Retrieval Strategy

1. **Keyword matching**: Match keywords from the user's question with keywords in the knowledge base
2. **Semantic similarity**: Calculate semantic similarity between the user's question and knowledge entries
3. **Ranking**: Rank knowledge entries based on combined score of keyword matching and semantic similarity
4. **Top N selection**: Select top N most relevant entries for answer generation

## Answer Generation Strategy

1. **Context gathering**: Collect information from top N knowledge entries
2. **Query understanding**: Understand the user's intent and what information is needed
3. **Colloquialization**: Generate answers in natural, conversational language
4. **Conciseness**: Keep answers brief and to the point
5. **Accuracy**: Ensure answers are accurate based on the knowledge base

## Multi-turn Dialogue Strategy

1. **History storage**: Store the last N turns of dialogue history
2. **Context integration**: Integrate dialogue history into question processing
3. **Reference resolution**: Resolve pronouns and references in follow-up questions
4. **Topic continuity**: Maintain topic continuity across multiple turns

## Testing Scenarios

### Basic QA
- **Scenario 1**: "为啥要倒贴福？"
- **Scenario 2**: "守岁是干啥的？"
- **Scenario 3**: "压岁钱是怎么来的？"

### Multi-turn Dialogue
- **Scenario 1**: "为啥要倒贴福？" → "那福字什么时候贴？"
- **Scenario 2**: "守岁是干啥的？" → "守岁的时候一般做什么？"
- **Scenario 3**: "压岁钱是怎么来的？" → "压岁钱一般给多少合适？"

## Deployment Considerations

- **Scalability**: The system should be able to handle multiple concurrent users
- **Performance**: Response time should be under 2 seconds for most queries
- **Maintainability**: The knowledge base should be easy to update and expand
- **Reliability**: The system should handle unexpected inputs gracefully

## Open Questions

- **Knowledge base expansion**: How to efficiently add new entries to the knowledge base?
- **Multilingual support**: Should the system support English questions about Chinese New Year customs?
- **User feedback**: How to collect and incorporate user feedback to improve the system?