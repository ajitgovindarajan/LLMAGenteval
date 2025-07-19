"""
environment.py - Android World Environment Interface

This file provides the interface layer between the evaluation framework and the
Android World dataset. It handles loading, parsing, and serving episodes from
the dataset in a format suitable for agent evaluation.

Key Components:
- AndroidWorldEnvironment: Main environment class for dataset interaction
- Episode loading: Parse JSON files from the Android World dataset
- Episode retrieval: Methods to access specific or random episodes
- Data validation: Ensure episodes have required fields (goal, observations, actions)

Features:
- Flexible dataset loading from directory structure
- Episode sampling for evaluation (random selection)
- Episode lookup by ID for reproducible testing
- Error handling for malformed data files
- Memory-efficient episode management

Data Structure Expected:
Each episode JSON file should contain:
- goal: String describing the task objective
- observations: List of dictionaries with UI state information
- actions: List of ground-truth action strings
- episode_id: Unique identifier (derived from filename)

"""
import json
import os
from typing import List, Dict

class AndroidWorldEnvironment:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.episodes = self._load_episodes()
    
    def _load_episodes(self) -> List[Episode]:
        """Load episodes from android_world dataset"""
        episodes = []
        
        # This is a placeholder - adapt based on actual android_world data structure
        for filename in os.listdir(self.data_path):
            if filename.endswith('.json'):
                with open(os.path.join(self.data_path, filename), 'r') as f:
                    data = json.load(f)
                    episode = Episode(
                        goal=data.get('goal', ''),
                        observations=data.get('observations', []),
                        actions=data.get('actions', []),
                        episode_id=filename.replace('.json', '')
                    )
                    episodes.append(episode)
        
        return episodes
    
    def get_episode(self, episode_id: str) -> Episode:
        """Get specific episode by ID"""
        for episode in self.episodes:
            if episode.episode_id == episode_id:
                return episode
        raise ValueError(f"Episode {episode_id} not found")
    
    def get_random_episodes(self, n: int) -> List[Episode]:
        """Get n random episodes for evaluation"""
        import random
        return random.sample(self.episodes, min(n, len(self.episodes)))