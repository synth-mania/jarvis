"""
Personal Assistant package integrating calendar, tasks, and email data with LLM interface.
"""

__version__ = '0.1.0'

from .core import MainProgram, DataSourceManager, ConversationHistory
from .llm_interface import LLMInterface

__all__ = [
    'MainProgram',
    'DataSourceManager',
    'ConversationHistory',
    'LLMInterface'
]
