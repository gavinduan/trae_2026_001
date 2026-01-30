#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dialogue Management Module
Manages dialogue history and context for multi-turn conversations.
"""

from typing import Dict, List

class DialogueManager:
    """Manages dialogue history and context for multi-turn conversations."""

    def __init__(self, max_history_length: int = 5):
        """
        Initialize the dialogue manager.

        Args:
            max_history_length: Maximum number of dialogue turns to keep
        """
        self.max_history_length = max_history_length
        self.dialogue_history = []

    def add_turn(self, role: str, content: str):
        """
        Add a turn to the dialogue history.

        Args:
            role: Role of the speaker ('user' or 'system')
            content: Content of the message
        """
        turn = {
            'role': role,
            'content': content,
            'timestamp': self._get_timestamp()
        }

        # Add to history
        self.dialogue_history.append(turn)

        # Truncate history if it exceeds max length
        if len(self.dialogue_history) > self.max_history_length:
            self.dialogue_history = self.dialogue_history[-self.max_history_length:]

    def get_history(self) -> List[Dict]:
        """
        Get the dialogue history.

        Returns:
            List of dialogue turns
        """
        return self.dialogue_history

    def clear_history(self):
        """
        Clear the dialogue history.
        """
        self.dialogue_history = []

    def get_recent_context(self, num_turns: int = 3) -> List[Dict]:
        """
        Get the most recent context from the dialogue history.

        Args:
            num_turns: Number of recent turns to include

        Returns:
            List of recent dialogue turns
        """
        return self.dialogue_history[-num_turns:]

    def is_follow_up_question(self, question: str) -> bool:
        """
        Determine if a question is a follow-up question.

        Args:
            question: User question as a string

        Returns:
            True if it's a follow-up question, False otherwise
        """
        # Check for follow-up indicators
        follow_up_indicators = [
            '那', '那么', '那如果', '那要是', '那假如',
            '然后', '接着', '还有', '另外', '再问',
            '再', '又', '还', '也', '更'
        ]

        for indicator in follow_up_indicators:
            if question.startswith(indicator):
                return True

        return False

    def _get_timestamp(self) -> str:
        """
        Get the current timestamp.

        Returns:
            Timestamp as a string
        """
        import datetime
        return datetime.datetime.now().isoformat()
