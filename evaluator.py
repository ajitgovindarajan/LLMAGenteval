"""
evaluator.py - Core Evaluation Engine for Android World LLM Agents

This file implements the evaluation logic that compares LLM agent performance
against ground-truth actions in Android World episodes. It provides comprehensive
metrics calculation, failure analysis, and result aggregation.

Key Components:
- EvaluationResult: Data class storing detailed evaluation outcomes for single episodes
- Evaluator: Main evaluation engine that runs agents through episodes and calculates metrics
- Action matching: Logic to compare agent actions with ground-truth actions
- Metrics calculation: Step accuracy, episode success rate, and aggregate statistics
- Failure analysis: Identification and categorization of common failure patterns

Features:
- Step-by-step action comparison with exact and fuzzy matching
- Episode-level success determination
- Comprehensive failure point tracking
- Aggregate metrics across multiple episodes
- Detailed logging of agent behavior vs. expected behavior
- Results serialization for analysis and reporting

Evaluation Process:
1. Reset agent history for clean episode start
2. Step through episode observations sequentially
3. Generate agent actions and compare to ground truth
4. Track correct steps, failures, and error patterns
5. Calculate episode and aggregate metrics
6. Store detailed results for analysis

Usage:
    evaluator = Evaluator()
    result = evaluator.evaluate_episode(agent, episode)
    metrics = evaluator.calculate_aggregate_metrics()
    evaluator.save_results("results.json")
"""
import json
from typing import List, Dict, Tuple
from dataclasses import dataclass

from agent import AndroidAgent
from agent import Episode

# this class is denoted as the data class which will be the precursor for the types of variables that are needed
@dataclass
class EvaluationResult:
    episode_id: str
    goal: str
    step_accuracy: float
    episode_success: bool
    total_steps: int
    correct_steps: int
    agent_actions: List[str]
    ground_truth_actions: List[str]
    failure_points: List[int]

# we also need a class that will be the placeholder for the evaluator
class Evaluator:
    def __init__(self):
        self.results = []
    
    # this function will evaluate the perfromance of each agent on a single episode
    def evaluate_episode(self, agent: AndroidAgent, episode: Episode) -> EvaluationResult:
        agent.reset_history()
        agent_actions = []
        correct_steps = 0
        failure_points = []
        
        # Run agent through episode with the exception of the final observation
        for i, observation in enumerate(episode.observations[:-1]):
            try:
                action = agent.generate_action(episode.goal, observation)
                agent_actions.append(action)
                
                # Check if action matches ground truth
                if i < len(episode.actions):
                    ground_truth = episode.actions[i]
                    if self._actions_match(action, ground_truth):
                        correct_steps += 1
                    else:
                        failure_points.append(i)
            # we need the error handling to make sure the program still runs    
            except Exception as e:
                print(f"Error generating action for step {i}: {e}")
                agent_actions.append("ERROR")
                failure_points.append(i)
        
        # Calculate metrics
        total_steps = len(episode.actions)
        step_accuracy = correct_steps / total_steps if total_steps > 0 else 0
        episode_success = len(failure_points) == 0
        
        # this variable is the comphensive stroage of each of the results that is quanitfied for the 
        result = EvaluationResult(
            episode_id=episode.episode_id,
            goal=episode.goal,
            step_accuracy=step_accuracy,
            episode_success=episode_success,
            total_steps=total_steps,
            correct_steps=correct_steps,
            agent_actions=agent_actions,
            ground_truth_actions=episode.actions,
            failure_points=failure_points
        )
        
        self.results.append(result)
        return result
    
    def _actions_match(self, agent_action: str, ground_truth: str) -> bool:
        """Check if agent action matches ground truth"""
        # Exact match
        if agent_action.strip() == ground_truth.strip():
            return True
        
        # Fuzzy match (could be improved)
        # Remove quotes and spaces for comparison
        agent_clean = re.sub(r'["\s]', '', agent_action.lower())
        truth_clean = re.sub(r'["\s]', '', ground_truth.lower())
        
        return agent_clean == truth_clean
    
    def calculate_aggregate_metrics(self) -> Dict:
        """Calculate aggregate metrics across all episodes"""
        if not self.results:
            return {}
        
        total_episodes = len(self.results)
        successful_episodes = sum(1 for r in self.results if r.episode_success)
        avg_step_accuracy = sum(r.step_accuracy for r in self.results) / total_episodes
        
        return {
            'total_episodes': total_episodes,
            'episode_success_rate': successful_episodes / total_episodes,
            'average_step_accuracy': avg_step_accuracy,
            'total_steps': sum(r.total_steps for r in self.results),
            'total_correct_steps': sum(r.correct_steps for r in self.results)
        }
    
    def generate_failure_analysis(self) -> Dict:
        """Analyze common failure patterns"""
        failure_types = {}
        
        for result in self.results:
            if not result.episode_success:
                # Analyze failure points
                for fp in result.failure_points:
                    if fp < len(result.agent_actions):
                        agent_action = result.agent_actions[fp]
                        if "ERROR" in agent_action:
                            failure_types["llm_error"] = failure_types.get("llm_error", 0) + 1
                        elif "CLICK" in agent_action:
                            failure_types["wrong_click"] = failure_types.get("wrong_click", 0) + 1
                        # Add more failure type analysis
        
        return failure_types
    
    def save_results(self, filepath: str):
        """Save evaluation results to file"""
        results_dict = {
            'aggregate_metrics': self.calculate_aggregate_metrics(),
            'failure_analysis': self.generate_failure_analysis(),
            'episode_results': [
                {
                    'episode_id': r.episode_id,
                    'goal': r.goal,
                    'step_accuracy': r.step_accuracy,
                    'episode_success': r.episode_success,
                    'total_steps': r.total_steps,
                    'correct_steps': r.correct_steps,
                    'failure_points': r.failure_points
                }
                for r in self.results
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(results_dict, f, indent=2)