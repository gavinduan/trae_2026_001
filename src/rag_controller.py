#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAG Controller Module
Orchestrates the RAG workflow using the various modules.
"""

from typing import Dict, List
from question_processor import QuestionProcessor
from knowledge_retriever import KnowledgeRetriever
from answer_generator import AnswerGenerator
from dialogue_manager import DialogueManager
from llm_backend import LLMBackend

class RAGController:
    """Orchestrates the RAG workflow for Chinese New Year customs QA."""

    def __init__(self, knowledge_base_path: str):
        """
        Initialize the RAG controller.

        Args:
            knowledge_base_path: Path to the knowledge base JSON file
        """
        # Initialize modules
        self.question_processor = QuestionProcessor()
        self.knowledge_retriever = KnowledgeRetriever(knowledge_base_path)
        self.answer_generator = AnswerGenerator()
        self.dialogue_manager = DialogueManager()
        
        # Initialize LLM backend
        try:
            self.llm_backend = LLMBackend()
            self.llm_enabled = True
        except ValueError as e:
            print(f"LLM backend initialization failed: {e}")
            print("LLM backend will be disabled. System will only use knowledge base.")
            self.llm_backend = None
            self.llm_enabled = False

    def process_query(self, question: str) -> str:
        """
        Process a user query through the RAG workflow.

        Args:
            question: User question as a string

        Returns:
            Colloquial answer as a string
        """
        # Check if it's a follow-up question
        is_follow_up = self.dialogue_manager.is_follow_up_question(question)

        # Get recent context if it's a follow-up
        if is_follow_up:
            context = self.dialogue_manager.get_recent_context()
        else:
            context = None

        # Process the question
        query = self.question_processor.process_question(question, context)

        # Retrieve relevant knowledge
        retrieved_entries = self.knowledge_retriever.retrieve(query)

        # Generate answer
        if retrieved_entries:
            # Use knowledge base answer
            answer = self.answer_generator.generate_answer(retrieved_entries, query, context)
            source = 'knowledge_base'
        elif self.llm_enabled:
            # Fallback to LLM if knowledge base returns no results
            print("Knowledge base returned no results. Using LLM fallback.")
            answer = self.llm_backend.generate_answer(question, context)
            source = 'llm'
        else:
            # No results and LLM disabled
            answer = "抱歉，我暂时没有关于这个问题的信息。"
            source = 'fallback'

        # Add to dialogue history
        self.dialogue_manager.add_turn('user', question)
        self.dialogue_manager.add_turn('system', answer)

        return answer, source

    def get_dialogue_history(self) -> List[Dict]:
        """
        Get the dialogue history.

        Returns:
            List of dialogue turns
        """
        return self.dialogue_manager.get_history()

    def clear_dialogue_history(self):
        """
        Clear the dialogue history.
        """
        self.dialogue_manager.clear_history()

    def reload_knowledge_base(self):
        """
        Reload the knowledge base from the JSON file.
        """
        self.knowledge_retriever.reload_knowledge_base()

    def set_max_history_length(self, max_length: int):
        """
        Set the maximum dialogue history length.

        Args:
            max_length: Maximum number of dialogue turns to keep
        """
        # Reinitialize dialogue manager with new max length
        self.dialogue_manager = DialogueManager(max_history_length=max_length)
