"""
Android World LLM Agent Evaluation Framework - Utilities Module

This module provides comprehensive utilities for evaluating Large Language Model (LLM) 
agents on Android World benchmarks. The framework tests how well LLMs can interact 
with Android applications through UI actions like clicking, scrolling, and typing.

Key Components:
- Logger: Structured logging for episode tracking, action recording, and error handling
- ActionParser: Parses and validates LLM responses into structured Android UI actions
- ResultsAnalyzer: Generates performance visualizations and failure analysis reports

Core Functionality:
1. ACTION PARSING: Converts natural language LLM responses into structured Android 
   actions (CLICK, SCROLL, TYPE, SWIPE, LONG_PRESS) with validation against available UI elements

2. PERFORMANCE TRACKING: Logs each episode's goal, step-by-step actions, ground truth 
   comparisons, and success/failure outcomes with detailed accuracy metrics

3. RESULTS ANALYSIS: Creates comprehensive reports including:
   - Episode success rates and step accuracy distributions
   - Performance correlation with episode length and complexity
   - Failure pattern analysis (early vs late failures)
   - Visual charts and summary statistics

4. BENCHMARK ORCHESTRATION: Supports comparative evaluation across multiple:
   - LLM models (GPT-4, Claude, etc.)
   - Prompt templates and strategies
   - Android World task categories

The framework enables researchers to systematically evaluate and compare LLM agents
for Android automation tasks, identifying strengths, weaknesses, and improvement areas
through detailed performance analytics and failure mode analysis.

Usage: Typically imported by main benchmark runners that coordinate episode execution,
action validation, and result aggregation across multiple evaluation configurations.
"""
"""

import json
import re
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class Logger:
    """Custom logging utility for the evaluation framework"""
    
    def __init__(self, log_dir: str = "results/logs"):
        os.makedirs(log_dir, exist_ok=True)
        self.log_file = os.path.join(log_dir, f"evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def log_episode_start(self, episode_id: str, goal: str):
        self.logger.info(f"Starting episode {episode_id}: {goal}")
    
    def log_action(self, step: int, observation: Dict, action: str, ground_truth: str, match: bool):
        self.logger.info(f"Step {step}: Action='{action}', Truth='{ground_truth}', Match={match}")
    
    def log_episode_end(self, episode_id: str, success: bool, accuracy: float):
        self.logger.info(f"Episode {episode_id} completed: Success={success}, Accuracy={accuracy:.2f}")
    
    def log_error(self, error_msg: str, context: str = ""):
        self.logger.error(f"Error in {context}: {error_msg}")

class ActionParser:
    """Enhanced action parsing with validation"""
    
    ACTION_PATTERNS = {
        'CLICK': r'CLICK\(["\']([^"\']*)["\']\)',
        'SCROLL': r'SCROLL\(["\']([^"\']*)["\']\)',
        'TYPE': r'TYPE\(["\']([^"\']*)["\']\)',
        'SWIPE': r'SWIPE\(["\']([^"\']*)["\']\)',
        'LONG_PRESS': r'LONG_PRESS\(["\']([^"\']*)["\']\)'
    }
    
    @classmethod
    def parse_action(cls, response: str) -> Dict[str, Any]:
        """Parse action from LLM response with validation"""
        response = response.strip()
        
        for action_type, pattern in cls.ACTION_PATTERNS.items():
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                return {
                    'action_type': action_type,
                    'target': match.group(1),
                    'formatted': f'{action_type}("{match.group(1)}")',
                    'valid': True
                }
        
        # If no pattern matched, it's likely an error
        return {
            'action_type': 'UNKNOWN',
            'target': None,
            'formatted': response,
            'valid': False
        }
    
    @classmethod
    def validate_action(cls, action: Dict, available_elements: List[str]) -> bool:
        """Validate if action target exists in available UI elements"""
        if not action['valid']:
            return False
        
        target = action['target']
        if not target:
            return False
        
        # Exact match
        if target in available_elements:
            return True
        
        # Fuzzy match (case-insensitive)
        for element in available_elements:
            if target.lower() == element.lower():
                return True
        
        return False

class ResultsAnalyzer:
    """Comprehensive analysis of evaluation results"""
    
    def __init__(self, results_file: str):
        with open(results_file, 'r') as f:
            self.data = json.load(f)
        self.episode_results = self.data.get('episode_results', [])
        self.aggregate_metrics = self.data.get('aggregate_metrics', {})
    
    def generate_performance_plots(self, output_dir: str = "results"):
        """Generate visualization plots for performance analysis"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert to DataFrame for easier plotting
        df = pd.DataFrame(self.episode_results)
        
        # Plot 1: Episode Success Rate
        plt.figure(figsize=(10, 6))
        success_rate = df['episode_success'].mean()
        plt.bar(['Success', 'Failure'], [success_rate, 1 - success_rate])
        plt.title('Episode Success Rate')
        plt.ylabel('Proportion')
        plt.savefig(os.path.join(output_dir, 'episode_success_rate.png'))
        plt.close()
        
        # Plot 2: Step Accuracy Distribution
        plt.figure(figsize=(10, 6))
        plt.hist(df['step_accuracy'], bins=20, alpha=0.7, edgecolor='black')
        plt.title('Distribution of Step Accuracy')
        plt.xlabel('Step Accuracy')
        plt.ylabel('Frequency')
        plt.axvline(df['step_accuracy'].mean(), color='red', linestyle='--', label=f'Mean: {df["step_accuracy"].mean():.2f}')
        plt.legend()
        plt.savefig(os.path.join(output_dir, 'step_accuracy_distribution.png'))
        plt.close()
        
        # Plot 3: Performance by Episode Length
        df['episode_length'] = df['total_steps']
        length_performance = df.groupby('episode_length')['episode_success'].mean()
        
        plt.figure(figsize=(12, 6))
        length_performance.plot(kind='bar')
        plt.title('Success Rate by Episode Length')
        plt.xlabel('Episode Length (steps)')
        plt.ylabel('Success Rate')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'performance_by_length.png'))
        plt.close()
        
        # Plot 4: Accuracy vs Success
        plt.figure(figsize=(10, 6))
        colors = ['red' if not success else 'green' for success in df['episode_success']]
        plt.scatter(df['step_accuracy'], df['total_steps'], c=colors, alpha=0.6)
        plt.xlabel('Step Accuracy')
        plt.ylabel('Total Steps')
        plt.title('Step Accuracy vs Episode Length (Red=Failed, Green=Success)')
        plt.savefig(os.path.join(output_dir, 'accuracy_vs_length.png'))
        plt.close()
    
    def generate_failure_analysis(self) -> Dict:
        """Analyze failure patterns in detail"""
        failures = [r for r in self.episode_results if not r['episode_success']]
        
        analysis = {
            'total_failures': len(failures),
            'failure_rate': len(failures) / len(self.episode_results) if self.episode_results else 0,
            'avg_failure_step': sum(len(f['failure_points']) for f in failures) / len(failures) if failures else 0,
            'failure_patterns': {}
        }
        
        # Analyze where failures occur
        failure_steps = []
        for failure in failures:
            failure_steps.extend(failure['failure_points'])
        
        if failure_steps:
            analysis['failure_patterns'] = {
                'early_failures': sum(1 for step in failure_steps if step < 2),
                'mid_failures': sum(1 for step in failure_steps if 2 <= step < 5),
                'late_failures': sum(1 for step in failure_steps if step >= 5)
            }
        
        return analysis
    
    def generate_summary_report(self, output_file: str = "results/summary_report.txt"):
        """Generate a text summary of results"""
        failure_analysis = self.generate_failure_analysis()
        
        with open(output_file, 'w') as f:
            f.write("ANDROID WORLD LLM AGENT EVALUATION SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("OVERALL PERFORMANCE:\n")
            f.write(f"Total Episodes: {self.aggregate_metrics.get('total_episodes', 0)}\n")
            f.write(f"Episode Success Rate: {self.aggregate_metrics.get('episode_success_rate', 0):.2%}\n")
            f.write(f"Average Step Accuracy: {self.aggregate_metrics.get('average_step_accuracy', 0):.2%}\n")
            f.write(f"Total Steps: {self.aggregate_metrics.get('total_steps', 0)}\n")
            f.write(f"Correct Steps: {self.aggregate_metrics.get('total_correct_steps', 0)}\n\n")
            
            f.write("FAILURE ANALYSIS:\n")
            f.write(f"Total Failures: {failure_analysis['total_failures']}\n")
            f.write(f"Failure Rate: {failure_analysis['failure_rate']:.2%}\n")
            f.write(f"Average Failure Step: {failure_analysis['avg_failure_step']:.1f}\n")
            
            if failure_analysis['failure_patterns']:
                f.write("\nFAILURE TIMING:\n")
                for pattern, count in failure_analysis['failure_patterns'].items():
                    f.write(f"{pattern}: {count}\n")
            
            f.write("\nTOP PERFORMING EPISODES:\n")
            top_episodes = sorted(self.episode_results, key=lambda x: x['step_accuracy'], reverse=True)[:5]
            for i, episode in enumerate(top_episodes, 1):
                f.write(f"{i}. {episode['episode_id']}: {episode['step_accuracy']:.2%} accuracy\n")
            
            f.write("\nLOWEST PERFORMING EPISODES:\n")
            bottom_episodes = sorted(self.episode_results, key=lambda x: x['step_accuracy'])[:5]
            for i, episode in enumerate(bottom_episodes, 1):
                f.write(f"{i}. {episode['episode_id']}: {episode['step_accuracy']:.2%} accuracy\n")


def main():
    parser = argparse.ArgumentParser(description="Run comprehensive Android World benchmarks")
    parser.add_argument("--data_path", required=True, help="Path to android_world dataset")
    parser.add_argument("--config_file", help="JSON file with benchmark configurations")
    parser.add_argument("--output_dir", default="results", help="Output directory")
    parser.add_argument("--num_episodes", type=int, default=10, help="Episodes per benchmark")
    parser.add_argument("--models", nargs="+", default=["gpt-4"], help="Models to test")
    parser.add_argument("--prompts", nargs="+", default=["base"], help="Prompt templates to test")
    parser.add_argument("--openai_key", help="OpenAI API key")
    parser.add_argument("--anthropic_key", help="Anthropic API key")
    
    args = parser.parse_args()
    
    # Initialize benchmark runner
    runner = BenchmarkRunner(args.data_path, args.output_dir)
    
    # Prepare configurations
    configs = []
    if args.config_file:
        with open(args.config_file, 'r') as f:
            configs = json.load(f)
    else:
        # Generate configs from command line args
        for model in args.models:
            for prompt in args.prompts:
                api_key = args.openai_key if "gpt" in model else args.anthropic_key
                configs.append({
                    'model': model,
                    'prompt_template': prompt,
                    'api_key': api_key
                })
    
    # Run benchmarks
    results = runner.run_comparative_benchmark(configs, args.num_episodes)
    
    # Generate final report
    runner.generate_final_report(results)
    
    print(f"\nBenchmark completed! Results saved to: {args.output_dir}")
    print(f"View final report: {os.path.join(args.output_dir, 'final_report.md')}")

if __name__ == "__main__":
    main()
