"""
config.py - Configuration Management for Android World LLM Agent Evaluation

This file centralizes all configuration settings, constants, and parameters used
throughout the Android World evaluation framework. It provides a single source
of truth for model specifications, evaluation parameters, and system settings.

Key Components:
- SUPPORTED_MODELS: Dictionary of available LLM models with their configurations
- PROMPT_TEMPLATES: Available prompting strategies for agent behavior
- File path configurations: Directory structures for results, logs, and prompts
- Action parsing patterns: Regular expressions for extracting actions from LLM responses
- Evaluation metrics: List of performance metrics to calculate and track

Features:
- Model-agnostic configuration (supports OpenAI and Anthropic models)
- Extensible prompt template system
- Configurable evaluation parameters
- Standardized action parsing patterns
- Centralized directory management
"""
import os
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Config:
    # First we have highlight the model configurations
    SUPPORTED_MODELS = {
        "gpt-4": {"provider": "openai", "max_tokens": 150},
        "gpt-3.5-turbo": {"provider": "openai", "max_tokens": 150},
        "claude-3-opus": {"provider": "anthropic", "max_tokens": 150},
        "claude-3-sonnet": {"provider": "anthropic", "max_tokens": 150}
    }
    
    # This element will be the templates possible for the prompts
    PROMPT_TEMPLATES = ["base", "few_shot", "self_reflection"]
    
    # This will set the episode benchmarks
    DEFAULT_NUM_EPISODES = 10
    MIN_EPISODES_FOR_BENCHMARK = 10
    
    # FThis will confuguate the paths for the these need to be fied as a result of the file directory that will need to be developed
    RESULTS_DIR = "results"
    LOGS_DIR = "results/logs"
    PROMPTS_DIR = "prompts"
    
    # Action patterns for parsing
    ACTION_PATTERNS = [
        r'CLICK\(["\']([^"\']*)["\']\)',
        r'SCROLL\(["\']([^"\']*)["\']\)',
        r'TYPE\(["\']([^"\']*)["\']\)',
        r'SWIPE\(["\']([^"\']*)["\']\)',
        r'LONG_PRESS\(["\']([^"\']*)["\']\)'
    ]
    
    # These is where the main results will be highlighted through the main ML/AI evalation metrics
    METRICS = [
        "step_accuracy",
        "episode_success_rate",
        "exact_match_rate",
        "partial_match_rate"
    ]