#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for LLM backend integration
"""

import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rag_controller import RAGController

class TestLLMIntegration:
    """
    Test class for LLM backend integration
    """

    def __init__(self):
        """
        Initialize test class
        """
        # Path to knowledge base
        self.knowledge_base_path = os.path.join(os.path.dirname(__file__), 'openspec', 'knowledge-base.json')

        # Initialize RAG controller
        self.rag_controller = RAGController(self.knowledge_base_path)

        # Test questions
        self.test_questions = [
            "为啥要倒贴福？",  # Should be in knowledge base
            "守岁是干啥的？",  # Should be in knowledge base
            "年兽是什么？",    # Should be in knowledge base
            "春节为什么要放鞭炮？",  # Should be in knowledge base
            "那福字什么时候贴？",    # Follow-up question
            "圣诞节在中国有什么习俗？",  # Not in knowledge base, should use LLM
            "万圣节为什么要讨糖？",     # Not in knowledge base, should use LLM
            "你好",                  # Greeting, should use LLM
            "再见"                   # Farewell, should use LLM
        ]

    def run_tests(self):
        """
        Run integration tests
        """
        print("===========================================")
        print("LLM Backend Integration Test")
        print("===========================================")
        print(f"Knowledge base path: {self.knowledge_base_path}")
        print(f"LLM backend enabled: {self.rag_controller.llm_enabled}")
        print("===========================================")

        for i, question in enumerate(self.test_questions, 1):
            print(f"\nTest {i}: {question}")
            print("-" * 50)
            
            try:
                answer = self.rag_controller.process_query(question)
                print(f"Answer: {answer}")
                print("Status: PASS")
            except Exception as e:
                print(f"Error: {e}")
                print("Status: FAIL")

        print("\n" + "=" * 50)
        print("Test Summary")
        print("=" * 50)
        print(f"Total tests: {len(self.test_questions)}")
        print(f"LLM backend enabled: {self.rag_controller.llm_enabled}")
        if self.rag_controller.llm_enabled and hasattr(self.rag_controller, 'llm_backend'):
            monitoring_stats = self.rag_controller.llm_backend.get_monitoring_stats()
            print(f"LLM API calls: {monitoring_stats['total_calls']}")
            print(f"Total tokens: {monitoring_stats['total_tokens']}")
            print(f"Estimated cost: ${monitoring_stats['total_cost']:.4f}")
            print(f"Avg response time: {monitoring_stats['avg_response_time']:.2f}s")

if __name__ == "__main__":
    test = TestLLMIntegration()
    test.run_tests()
