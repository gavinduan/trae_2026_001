#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Knowledge Retrieval Module
Retrieves relevant information from the knowledge base based on processed queries.
"""

import json
from typing import Dict, List, Tuple

class KnowledgeRetriever:
    """Retrieves relevant information from the knowledge base."""

    def __init__(self, knowledge_base_path: str):
        """
        Initialize the knowledge retriever.

        Args:
            knowledge_base_path: Path to the knowledge base JSON file
        """
        self.knowledge_base_path = knowledge_base_path
        self.knowledge_base = self._load_knowledge_base()

    def _load_knowledge_base(self) -> Dict:
        """
        Load the knowledge base from the JSON file.

        Returns:
            Knowledge base as a dictionary
        """
        with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
            knowledge_base = json.load(f)
        return knowledge_base

    def retrieve(self, query: Dict, top_n: int = 3) -> List[Dict]:
        """
        Retrieve relevant knowledge entries based on the processed query.

        Args:
            query: Processed query dictionary
            top_n: Number of top relevant entries to return

        Returns:
            List of top N relevant knowledge entries
        """
        # Extract keywords from the query
        keywords = query.get('keywords', [])

        # Calculate relevance scores for each entry
        scored_entries = []
        for entry in self.knowledge_base['data']:
            score = self._calculate_relevance(entry, keywords, query)
            if score > 0:
                scored_entries.append((score, entry))

        # Sort by relevance score (descending)
        scored_entries.sort(key=lambda x: x[0], reverse=True)

        # Return top N entries
        top_entries = [entry for _, entry in scored_entries[:top_n]]
        return top_entries

    def _calculate_relevance(self, entry: Dict, keywords: List[str], query: Dict) -> float:
        """
        Calculate the relevance score of a knowledge entry to the query.

        Args:
            entry: Knowledge entry dictionary
            keywords: List of keywords from the query
            query: Processed query dictionary

        Returns:
            Relevance score as a float
        """
        score = 0.0

        # Get original question for better matching
        original_question = query.get('original_question', '')
        cleaned_question = query.get('cleaned_question', '')

        # Match keywords in title
        title = entry.get('title', '')
        for keyword in keywords:
            if keyword in title:
                score += 3.0  # Higher weight for title matches
                # Extra weight for exact matches
                if keyword == title:
                    score += 2.0

        # Match keywords in description
        description = entry.get('description', '')
        for keyword in keywords:
            if keyword in description:
                score += 2.0  # Medium weight for description matches

        # Match keywords in keywords field
        entry_keywords = entry.get('keywords', [])
        for keyword in keywords:
            if keyword in entry_keywords:
                score += 2.5  # Slightly higher weight for explicit keywords

        # Match keywords in scenarios
        scenarios = entry.get('scenarios', [])
        for scenario in scenarios:
            for keyword in keywords:
                if keyword in scenario:
                    score += 1.5  # Lower weight for scenario matches

        # Adjust score based on intent
        intent = query.get('intent', '')
        if intent == 'why' and any(reason_word in description for reason_word in ['因为', '由于', '是因为', '源于', '起因']):
            score += 1.5
        elif intent == 'when' and any(time_word in description for time_word in ['时间', '时候', '何时', '什么时候', '通常', '一般']):
            score += 1.5
        elif intent == 'how' and any(method_word in description for method_word in ['如何', '怎么', '怎样', '方法', '步骤']):
            score += 1.5
        elif intent == 'where' and any(place_word in description for place_word in ['地方', '位置', '地点', '在', '于']):
            score += 1.5

        # Handle common questions
        common_questions = {
            '过年': 'spring-festival',
            '春节': 'spring-festival',
            '除夕': 'new-years-eve',
            '守岁': 'shou-sui',
            '压岁钱': 'lucky-money',
            '红包': 'red-packets',
            '春联': 'couplets',
            '福字': 'fu-character',
            '倒贴福': 'fu-character',
            '年糕': 'rice-cake',
            '饺子': 'dumplings',
            '放鞭炮': 'firecrackers',
            '烟花': 'firecrackers',
            '庙会': 'temple-fair',
            '舞龙': 'dragon-lion-dance',
            '舞狮': 'dragon-lion-dance',
            '元宵节': 'lantern-festival',
            '灯会': 'lanterns',
            '猜灯谜': 'lantern-riddles',
            '清明': 'qingming-festival',
            '端午节': 'dragon-boat-festival',
            '粽子': 'dragon-boat-festival',
            '七夕': 'qixi-festival',
            '中秋': 'mid-autumn-festival',
            '月饼': 'mid-autumn-festival',
            '重阳': 'double-ninth-festival'
        }

        # Check for common questions
        for question, entry_id in common_questions.items():
            if question in original_question or question in cleaned_question:
                if entry.get('id') == entry_id:
                    score += 5.0  # High weight for common question matches

        return score

    def get_related_entries(self, entry_id: str, top_n: int = 2) -> List[Dict]:
        """
        Get related knowledge entries based on the entry ID.

        Args:
            entry_id: ID of the knowledge entry
            top_n: Number of top related entries to return

        Returns:
            List of top N related knowledge entries
        """
        # Find the entry with the given ID
        target_entry = None
        for entry in self.knowledge_base['data']:
            if entry.get('id') == entry_id:
                target_entry = entry
                break

        if not target_entry:
            return []

        # Get related entry IDs
        related_ids = target_entry.get('related', [])

        # Find and return related entries
        related_entries = []
        for entry in self.knowledge_base['data']:
            if entry.get('id') in related_ids:
                related_entries.append(entry)

        # Return top N related entries
        return related_entries[:top_n]

    def reload_knowledge_base(self):
        """
        Reload the knowledge base from the JSON file.
        """
        self.knowledge_base = self._load_knowledge_base()
