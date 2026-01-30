#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Question Processing Module
Processes user questions to extract key information and identify intent.
"""

import re
from typing import Dict, List, Tuple

class QuestionProcessor:
    """Processes user questions to extract key information."""

    def __init__(self):
        """Initialize the question processor."""
        # Common question patterns
        self.question_patterns = {
            'why': [r'为什么', r'为啥', r'何故', r'何以'],
            'what': [r'什么', r'啥', r'何谓', r'是什么'],
            'when': [r'什么时候', r'何时', r'几时', r'什么时候'],
            'how': [r'怎么', r'如何', r'怎样', r'如何做'],
            'where': [r'哪里', r'哪儿', r'在什么地方', r'位置']
        }

    def process_question(self, question: str, context: List[Dict] = None) -> Dict:
        """
        Process a user question to extract key information.

        Args:
            question: User question as a string
            context: Dialogue history for context-aware processing

        Returns:
            Dict containing processed query information
        """
        # Clean the question
        cleaned_question = self._clean_question(question)

        # Extract intent
        intent = self._extract_intent(cleaned_question)

        # Extract keywords
        keywords = self._extract_keywords(cleaned_question)

        # Process with context if available
        if context:
            processed_query = self._process_with_context(cleaned_question, context, intent, keywords)
        else:
            processed_query = {
                'original_question': question,
                'cleaned_question': cleaned_question,
                'intent': intent,
                'keywords': keywords,
                'context_aware': False
            }

        return processed_query

    def _clean_question(self, question: str) -> str:
        """
        Clean the question by removing punctuation and unnecessary whitespace.

        Args:
            question: User question as a string

        Returns:
            Cleaned question string
        """
        # Remove punctuation
        cleaned = re.sub(r'[，。！？；："\'（）]', ' ', question)
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def _extract_intent(self, question: str) -> str:
        """
        Extract the intent from the question.

        Args:
            question: Cleaned question string

        Returns:
            Intent type as a string
        """
        for intent, patterns in self.question_patterns.items():
            for pattern in patterns:
                if pattern in question:
                    return intent
        return 'what'  # Default intent

    def _extract_keywords(self, question: str) -> List[str]:
        """
        Extract keywords from the question.

        Args:
            question: Cleaned question string

        Returns:
            List of extracted keywords
        """
        # Remove question words
        keyword_question = question
        for patterns in self.question_patterns.values():
            for pattern in patterns:
                keyword_question = keyword_question.replace(pattern, '')

        # Split into words and filter out stop words
        words = keyword_question.split()
        stop_words = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '那么', '然后', '接着', '还有', '另外', '再问', '再', '又', '还', '也', '更'}
        keywords = [word for word in words if word not in stop_words and len(word) > 1]

        # Add common year-related keywords
        year_related_words = {'新年', '春节', '除夕', '元宵', '清明', '端午', '七夕', '中秋', '重阳'}
        for word in year_related_words:
            if word in question and word not in keywords:
                keywords.append(word)

        return keywords

    def _process_with_context(self, question: str, context: List[Dict], intent: str, keywords: List[str]) -> Dict:
        """
        Process the question with dialogue context.

        Args:
            question: Cleaned question string
            context: Dialogue history
            intent: Extracted intent
            keywords: Extracted keywords

        Returns:
            Context-aware processed query
        """
        # Get the most recent system response
        recent_system_response = None
        for turn in reversed(context):
            if turn['role'] == 'system':
                recent_system_response = turn['content']
                break

        # Get the most recent user question
        recent_user_question = None
        for turn in reversed(context):
            if turn['role'] == 'user':
                recent_user_question = turn['content']
                break

        # Process context to enhance keywords
        enhanced_keywords = keywords.copy()

        # If the question contains pronouns or references, resolve them using context
        if any(pronoun in question for pronoun in ['这', '那', '它', '他', '她', '他们', '她们', '它们']):
            if recent_system_response:
                # Extract keywords from recent system response
                system_keywords = self._extract_keywords(recent_system_response)
                enhanced_keywords.extend(system_keywords)
            elif recent_user_question:
                # Extract keywords from recent user question
                user_keywords = self._extract_keywords(recent_user_question)
                enhanced_keywords.extend(user_keywords)

        # Remove duplicates
        enhanced_keywords = list(set(enhanced_keywords))

        return {
            'original_question': question,
            'cleaned_question': question,
            'intent': intent,
            'keywords': enhanced_keywords,
            'context_aware': True,
            'recent_context': {
                'system_response': recent_system_response,
                'user_question': recent_user_question
            }
        }
