#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Answer Generation Module
Generates colloquial answers based on retrieved knowledge entries.
"""

from typing import Dict, List
import re

class AnswerGenerator:
    """Generates colloquial answers based on retrieved knowledge entries."""

    def __init__(self):
        """Initialize the answer generator."""
        # Intent-specific templates
        self.intent_templates = {
            'why': '因为{reason}，所以{action}。',
            'what': '{description}。',
            'when': '{action}通常在{time}。',
            'how': '{action}的方法是{method}。',
            'where': '{action}通常在{place}。'
        }

    def generate_answer(self, retrieved_entries: List[Dict], query: Dict, context: List[Dict] = None) -> str:
        """
        Generate a colloquial answer based on retrieved knowledge entries.

        Args:
            retrieved_entries: List of retrieved knowledge entries
            query: Processed query dictionary
            context: Dialogue history for context-aware generation

        Returns:
            Colloquial answer as a string
        """
        if not retrieved_entries:
            return "抱歉，我暂时没有关于这个问题的信息。"

        # Get the most relevant entry
        top_entry = retrieved_entries[0]

        # Extract information from the top entry
        title = top_entry.get('title', '')
        description = top_entry.get('description', '')
        scenarios = top_entry.get('scenarios', [])

        # Get intent from query
        intent = query.get('intent', 'what')

        # Generate answer based on intent
        if intent in self.intent_templates:
            answer = self._generate_intent_based_answer(top_entry, intent, query)
        else:
            answer = self._generate_generic_answer(top_entry, query)

        # Make answer more colloquial
        colloquial_answer = self._make_colloquial(answer)

        # Add context if available
        if context and query.get('context_aware', False):
            colloquial_answer = self._add_context(colloquial_answer, context)

        return colloquial_answer

    def _generate_intent_based_answer(self, entry: Dict, intent: str, query: Dict) -> str:
        """
        Generate an answer based on the specific intent.

        Args:
            entry: Top retrieved knowledge entry
            intent: Intent type from the query
            query: Processed query dictionary

        Returns:
            Answer string tailored to the intent
        """
        title = entry.get('title', '')
        description = entry.get('description', '')

        if intent == 'why':
            # Extract reason from description
            reason = self._extract_reason(description, title)
            action = title
            return self.intent_templates['why'].format(reason=reason, action=action)

        elif intent == 'what':
            return self.intent_templates['what'].format(description=description)

        elif intent == 'when':
            # Extract time information from description
            time_info = self._extract_time(description)
            action = title
            if time_info:
                return self.intent_templates['when'].format(action=action, time=time_info)
            else:
                return f"关于{title}的时间，{description}"

        elif intent == 'how':
            # Extract method information from description
            method = self._extract_method(description)
            action = title
            if method:
                return self.intent_templates['how'].format(action=action, method=method)
            else:
                return f"关于{title}的方法，{description}"

        elif intent == 'where':
            # Extract place information from description
            place = self._extract_place(description)
            action = title
            if place:
                return self.intent_templates['where'].format(action=action, place=place)
            else:
                return f"关于{title}的地点，{description}"

        else:
            return description

    def _generate_generic_answer(self, entry: Dict, query: Dict) -> str:
        """
        Generate a generic answer when no specific intent template matches.

        Args:
            entry: Top retrieved knowledge entry
            query: Processed query dictionary

        Returns:
            Generic answer string
        """
        title = entry.get('title', '')
        description = entry.get('description', '')
        return f"{title}：{description}"

    def _extract_reason(self, description: str, title: str) -> str:
        """
        Extract reason information from the description.

        Args:
            description: Knowledge entry description
            title: Knowledge entry title

        Returns:
            Reason string
        """
        # Look for reason indicators
        reason_indicators = ['因为', '由于', '是因为', '源于', '起因']
        for indicator in reason_indicators:
            if indicator in description:
                reason_part = description.split(indicator)[1]
                # Clean up the reason part
                reason_part = reason_part.split('。')[0].strip()
                return reason_part

        # If no reason indicator found, use the first part of the description
        reason = description.split('。')[0].strip()
        return reason

    def _extract_time(self, description: str) -> str:
        """
        Extract time information from the description.

        Args:
            description: Knowledge entry description

        Returns:
            Time information string
        """
        # Look for time indicators
        time_indicators = ['在', '于', '通常', '一般', '时候', '时间', '日期']
        for indicator in time_indicators:
            if indicator in description:
                # Extract time-related part
                parts = description.split(indicator)
                if len(parts) > 1:
                    time_part = parts[1].split('，')[0].split('。')[0].strip()
                    if any(time_word in time_part for time_word in ['春节', '除夕', '正月', '腊月', '时候', '时间', '日期']):
                        return time_part

        return ''

    def _extract_method(self, description: str) -> str:
        """
        Extract method information from the description.

        Args:
            description: Knowledge entry description

        Returns:
            Method information string
        """
        # Look for method indicators
        method_indicators = ['通过', '使用', '采用', '做法', '方法', '步骤', '如何']
        for indicator in method_indicators:
            if indicator in description:
                # Extract method-related part
                parts = description.split(indicator)
                if len(parts) > 1:
                    method_part = parts[1].split('，')[0].split('。')[0].strip()
                    return method_part

        return ''

    def _extract_place(self, description: str) -> str:
        """
        Extract place information from the description.

        Args:
            description: Knowledge entry description

        Returns:
            Place information string
        """
        # Look for place indicators
        place_indicators = ['在', '于', '地方', '位置', '地点']
        for indicator in place_indicators:
            if indicator in description:
                # Extract place-related part
                parts = description.split(indicator)
                if len(parts) > 1:
                    place_part = parts[1].split('，')[0].split('。')[0].strip()
                    if any(place_word in place_part for place_word in ['门', '墙', '窗户', '房间', '院子', '广场', '寺庙', '公园']):
                        return place_part

        return ''

    def _make_colloquial(self, answer: str) -> str:
        """
        Make the answer more colloquial and natural.

        Args:
            answer: Generated answer string

        Returns:
            Colloquial answer string
        """
        # Replace formal expressions with colloquial ones
        colloquial_replacements = {
            '是因为': '因为',
            '因此': '所以',
            '例如': '比如',
            '也就是说': '就是说',
            '此外': '另外',
            '综上所述': '总之',
            '需要注意的是': '要注意的是',
            '可以': '可以啊',
            '应该': '应该吧',
            '必须': '一定要'
        }

        colloquial_answer = answer
        for formal, colloquial in colloquial_replacements.items():
            colloquial_answer = colloquial_answer.replace(formal, colloquial)

        # Add some colloquial particles
        if not any(particle in colloquial_answer for particle in ['啊', '呀', '呢', '吧', '嘛']):
            if colloquial_answer.endswith('。'):
                colloquial_answer = colloquial_answer[:-1] + '呢。'
            else:
                colloquial_answer += '呢'

        # Remove duplicate punctuation
        colloquial_answer = re.sub(r'。+', '。', colloquial_answer)

        return colloquial_answer

    def _add_context(self, answer: str, context: List[Dict]) -> str:
        """
        Add context from previous dialogue to the answer.

        Args:
            answer: Generated answer string
            context: Dialogue history

        Returns:
            Answer string with added context
        """
        # Get the most recent user question
        recent_user_question = None
        for turn in reversed(context):
            if turn['role'] == 'user':
                recent_user_question = turn['content']
                break

        if recent_user_question:
            # Add a reference to the previous question
            if '那' in recent_user_question or '那么' in recent_user_question:
                answer = f"你问的关于{recent_user_question.split('那')[1].strip()}的问题，{answer}"

        return answer
