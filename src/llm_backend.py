#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LLM Backend Module
Integrates with OpenAI API to generate answers when knowledge base retrieval fails.
"""

import os
import json
import time
from typing import Dict, List, Optional
from openai import OpenAI

class LLMBackend:
    """
    LLM Backend for generating answers using OpenAI API.
    """

    def __init__(self):
        """
        Initialize the LLM backend with configuration.
        """
        # Read configuration from file if exists
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        config = {
            'model': 'gpt-3.5-turbo',
            'temperature': 0.7,
            'max_tokens': 150,
            'top_p': 1.0,
            'frequency_penalty': 0.0,
            'presence_penalty': 0.0
        }
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config.update(json.load(f))

        # Read API key from environment variable or config
        self.api_key = os.getenv('OPENAI_API_KEY') or config.get('api_key')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable or api_key in config.json is not set")

        # Read API base URL from environment variable or config
        self.api_base = os.getenv('OPENAI_API_BASE') or config.get('api_base')

        # Initialize OpenAI client
        if self.api_base:
            self.client = OpenAI(api_key=self.api_key, base_url=self.api_base)
        else:
            self.client = OpenAI(api_key=self.api_key)

        # Update configuration
        self.config = config

        # Initialize monitoring
        self.monitoring = {
            'total_calls': 0,
            'total_tokens': 0,
            'total_cost': 0.0,
            'avg_response_time': 0.0
        }

        # Inappropriate content patterns
        self.inappropriate_patterns = [
            '色情', '赌博', '毒品', '暴力', '恐怖',
            '政治敏感', '歧视', '侮辱', '诈骗'
        ]

    def generate_answer(self, question: str, context: Optional[List[Dict]] = None, stream: bool = False):
        """
        Generate an answer using OpenAI API.

        Args:
            question: User question as a string
            context: Dialogue history for context-aware generation
            stream: Whether to use streaming output

        Returns:
            Generated answer as a string (non-stream) or generator (stream)
        """
        start_time = time.time()

        try:
            # Build prompt
            prompt = self._build_prompt(question, context)

            # Build conversation messages with full context
            conversation_messages = self._build_conversation_messages(context)

            # Add current question to context
            if context:
                # Create a copy of context and add current question
                full_context = context + [{'role': 'user', 'content': question}]
                conversation_messages = self._build_conversation_messages(full_context)
            else:
                conversation_messages = []

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.config['model'],
                messages=[
                    {
                        'role': 'system',
                        'content': '你是一个中国年俗知识专家，负责回答用户关于中国传统节日和习俗的问题。请使用口语化的语言，确保回答准确、有趣。请直接回答问题，不要输出思考过程或分析内容。'
                    }
                ] + conversation_messages if conversation_messages else [
                    {
                        'role': 'system',
                        'content': '你是一个中国年俗知识专家，负责回答用户关于中国传统节日和习俗的问题。请使用口语化的语言，确保回答准确、有趣。请直接回答问题，不要输出思考过程或分析内容。'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=self.config['temperature'],
                max_tokens=self.config['max_tokens'],
                top_p=self.config['top_p'],
                frequency_penalty=self.config['frequency_penalty'],
                presence_penalty=self.config['presence_penalty'],
                stream=stream
            )

            if stream:
                # Return streaming response with thinking block filtering
                def generate_stream():
                    buffer = ""
                    in_thinking_block = False

                    # All possible start tags (full-width and half-width)
                    start_tags = ['＜thought>', '<thought>', '＜think>', '<think>', '＜THINK>', '＜Think>']
                    # All possible end tags
                    end_tags = ['＜/thought>', '</thought>', '＜/think>', '</think>', '＜/THINK>', '＜/Think>']

                    for chunk in response:
                        if chunk.choices and chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            if content:
                                # Update monitoring
                                self.monitoring['total_calls'] += 1

                                buffer += content

                                # Keep processing until buffer has no complete thinking blocks
                                while True:
                                    if in_thinking_block:
                                        # Looking for end tag
                                        end_pos = -1
                                        found_end_tag = None
                                        for tag in end_tags:
                                            pos = buffer.find(tag)
                                            if pos != -1 and (end_pos == -1 or pos < end_pos):
                                                end_pos = pos
                                                found_end_tag = tag

                                        if end_pos != -1:
                                            # Found end tag, remove everything up to and including it
                                            buffer = buffer[end_pos + len(found_end_tag):]
                                            in_thinking_block = False
                                        else:
                                            # Still inside thinking block, no complete end tag yet
                                            break
                                    else:
                                        # Looking for start tag
                                        start_pos = -1
                                        found_start_tag = None
                                        for tag in start_tags:
                                            pos = buffer.find(tag)
                                            if pos != -1 and (start_pos == -1 or pos < start_pos):
                                                start_pos = pos
                                                found_start_tag = tag

                                        if start_pos != -1:
                                            # Found start tag, check if there's a matching end tag
                                            remaining_after_start = buffer[start_pos + len(found_start_tag):]

                                            end_pos = -1
                                            found_end_tag = None
                                            for tag in end_tags:
                                                pos = remaining_after_start.find(tag)
                                                if pos != -1 and (end_pos == -1 or pos < end_pos):
                                                    end_pos = pos
                                                    found_end_tag = tag

                                            if end_pos != -1:
                                                # Found complete thinking block, remove it
                                                buffer = buffer[:start_pos] + remaining_after_start[end_pos + len(found_end_tag):]
                                                # Continue loop to check for more thinking blocks
                                            else:
                                                # Start tag found but no end tag yet, enter thinking block mode
                                                buffer = buffer[:start_pos]
                                                in_thinking_block = True
                                                break
                                        else:
                                            # No start tag, yield all content and clear buffer
                                            if buffer:
                                                yield buffer
                                                buffer = ""
                                            break

                    # Handle any remaining content after stream ends
                    if buffer and not in_thinking_block:
                        yield buffer

                    # Finalize monitoring
                    self.monitoring['avg_response_time'] = (
                        (self.monitoring['avg_response_time'] * (self.monitoring['total_calls'] - 1) + (time.time() - start_time)) /
                        self.monitoring['total_calls']
                    )

                return generate_stream()
            else:
                # Extract answer
                answer = response.choices[0].message.content.strip()

                # Update monitoring
                self._update_monitoring(response, time.time() - start_time)

                # Quality control
                if self._contains_inappropriate_content(answer):
                    return "抱歉，我无法回答这个问题。"

                # Post-process answer
                processed_answer = self._post_process_answer(answer)

                return processed_answer

        except Exception as e:
            print(f"LLM API call failed: {e}")
            return "抱歉，我暂时无法回答这个问题。"

    def post_process_response(self, response: str) -> str:
        """
        Post-process a complete response to remove thinking blocks and clean up.

        Args:
            response: Raw response string

        Returns:
            Post-processed response
        """
        return self._post_process_answer(response)

    def _build_prompt(self, question: str, context: Optional[List[Dict]] = None) -> str:
        """
        Build a prompt for OpenAI API based on the question and context.

        Args:
            question: User question as a string
            context: Dialogue history for context-aware generation

        Returns:
            Built prompt as a string
        """
        prompt = f"请回答以下关于中国年俗的问题：{question}"

        if context:
            # Add recent context to prompt
            recent_context = context[-2:]  # Get last 2 turns
            context_str = "\n最近的对话：\n"
            for turn in recent_context:
                role = "用户" if turn['role'] == 'user' else "助手"
                context_str += f"{role}：{turn['content']}\n"
            prompt += context_str

        prompt += "\n请使用口语化的语言回答，确保回答准确、有趣。"
        return prompt

    def _build_conversation_messages(self, context: Optional[List[Dict]] = None) -> List[Dict]:
        """
        Build conversation messages for LLM API from dialogue history.

        Args:
            context: Dialogue history

        Returns:
            List of conversation messages in OpenAI format
        """
        if not context:
            return []

        messages = []
        for turn in context:
            role = turn['role']
            if role == 'user':
                messages.append({'role': 'user', 'content': turn['content']})
            elif role == 'system':
                messages.append({'role': 'assistant', 'content': turn['content']})

        return messages

    def _post_process_answer(self, answer: str) -> str:
        """
        Post-process the LLM-generated answer.

        Args:
            answer: Raw answer from LLM

        Returns:
            Post-processed answer
        """
        # Remove think/思考/分析部分
        import re
        
        # Remove content between <think> tags
        answer = re.sub(r'<think>.*?</think>', '', answer, flags=re.DOTALL)
        
        # Remove content between 思考 tags
        answer = re.sub(r'思考[:：].*?(\n|$)', '', answer)
        answer = re.sub(r'分析[:：].*?(\n|$)', '', answer)
        answer = re.sub(r'推理[:：].*?(\n|$)', '', answer)
        
        # Remove content after "让我思考" or similar phrases
        answer = re.sub(r'让我[思考分析想一想推理].*?(\n|$)', '', answer)
        
        # Remove "思考过程：" or similar prefixes
        answer = re.sub(r'思考过程[:：].*?(\n|$)', '', answer)
        answer = re.sub(r'分析过程[:：].*?(\n|$)', '', answer)
        
        # Clean up extra whitespace and newlines
        answer = re.sub(r'\n+', '\n', answer)
        answer = re.sub(r' +', ' ', answer)
        
        # Strip leading/trailing whitespace
        answer = answer.strip()
        
        # Remove unnecessary prefixes
        prefixes = ["回答：", "答：", "我来回答："]
        for prefix in prefixes:
            if answer.startswith(prefix):
                answer = answer[len(prefix):].strip()

        # Add colloquial particles if needed
        if not any(particle in answer for particle in ['啊', '呀', '呢', '吧', '嘛']):
            if answer.endswith('。'):
                answer = answer[:-1] + '呢。'

        return answer

    def _contains_inappropriate_content(self, text: str) -> bool:
        """
        Check if text contains inappropriate content.

        Args:
            text: Text to check

        Returns:
            True if text contains inappropriate content, False otherwise
        """
        for pattern in self.inappropriate_patterns:
            if pattern in text:
                return True
        return False

    def _update_monitoring(self, response, response_time: float, tokens: int = 0):
        """
        Update monitoring statistics.

        Args:
            response: OpenAI API response
            response_time: Response time in seconds
            tokens: Number of tokens in the response (for streaming)
        """
        # Update call count
        self.monitoring['total_calls'] += 1

        # Update token count
        if tokens > 0:
            self.monitoring['total_tokens'] += tokens

            # Calculate cost (approximate)
            model = self.config['model']
            if model == 'gpt-3.5-turbo':
                cost_per_token = 0.0000015  # $0.0015 per 1k tokens
            elif model == 'gpt-4':
                cost_per_token = 0.00003  # $0.03 per 1k tokens
            else:
                cost_per_token = 0.0000015

            cost = tokens * cost_per_token
            self.monitoring['total_cost'] += cost
        else:
            # Update token count from response usage
            usage = response.usage
            if usage:
                total_tokens = usage.total_tokens
                self.monitoring['total_tokens'] += total_tokens

                # Calculate cost (approximate)
                model = self.config['model']
                if model == 'gpt-3.5-turbo':
                    cost_per_token = 0.0000015  # $0.0015 per 1k tokens
                elif model == 'gpt-4':
                    cost_per_token = 0.00003  # $0.03 per 1k tokens
                else:
                    cost_per_token = 0.0000015

                cost = total_tokens * cost_per_token
                self.monitoring['total_cost'] += cost

        # Update average response time
        self.monitoring['avg_response_time'] = (
            (self.monitoring['avg_response_time'] * (self.monitoring['total_calls'] - 1) + response_time) /
            self.monitoring['total_calls']
        )

    def get_monitoring_stats(self) -> Dict:
        """
        Get monitoring statistics.

        Returns:
            Monitoring statistics as a dictionary
        """
        return self.monitoring

    def reset_monitoring(self):
        """
        Reset monitoring statistics.
        """
        self.monitoring = {
            'total_calls': 0,
            'total_tokens': 0,
            'total_cost': 0.0,
            'avg_response_time': 0.0
        }

    def update_config(self, new_config: Dict):
        """
        Update configuration.

        Args:
            new_config: New configuration dictionary
        """
        self.config.update(new_config)

        # Save to file
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
