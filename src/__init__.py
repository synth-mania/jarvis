"""
Personal Assistant package integrating calendar, tasks, and email data with LLM interface.
"""

__version__ = '0.1.0'

from .core import Agent, Conversation
from .llm_interface import LLMInterface

__all__ = [
    'Agent',
    'Conversation',
    'LLMInterface'
]
