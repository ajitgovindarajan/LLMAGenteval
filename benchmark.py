"""
benchmark.py

this benchmark file will privde the evalation bechmarks that re denoted by the project guidelines.
benchmark.py - Comprehensive Benchmarking System for Android World LLM Agents

This file provides the core benchmarking infrastructure for evaluating LLM agents
across multiple models, prompt templates, and episodes in the Android World environment.

Key Components:
- BenchmarkRunner: Main orchestration class for running evaluations
- Single benchmark execution: Test one model-prompt combination
- Comparative benchmarking: Test multiple configurations simultaneously
- Results aggregation: Collect and analyze performance metrics
- Report generation: Create markdown reports with performance summaries

Features:
- Multi-model support (GPT-4, Claude, etc.)
- Multiple prompt strategies (base, few-shot, self-reflection)
- Configurable episode sampling
- Automated results saving and analysis
- Performance visualization integration
- Error handling and logging

Workflow:
1. Initialize environment and load episodes
2. Configure model-prompt combinations to test
3. Run agents through selected episodes
4. Collect step-by-step and episode-level metrics
5. Generate comparative analysis and final reports

Usage:
    runner = BenchmarkRunner(data_path="android_world_data/")
    configs = [{"model": "gpt-4", "prompt_template": "few_shot", "api_key": "..."}]
    results = runner.run_comparative_benchmark(configs, num_episodes=15)

"""

import argparse
import json
import os
import time
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

from agent import AndroidAgent
from environment import AndroidWorldEnvironment
from evaluator import Evaluator
from utils import Logger, ResultsAnalyzer

# Comprehensive benchmarking system for multiple models and prompts
class BenchmarkRunner:
    
    def __init__(self, data_path: str, output_dir: str = "results"):
        self.data_path = data_path
        self.output_dir = output_dir
        self.logger = Logger()
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize environment
        self.env = AndroidWorldEnvironment(data_path)
    
    # this function will define the single benchmark model
    def run_single_benchmark(self, model: str, prompt_template: str, api_key: str, 
                           num_episodes: int = 10) -> Dict:
        # this will run for a single model prompt combination
        self.logger.logger.info(f"Starting benchmark: {model} with {prompt_template}")
        
        # Initialize agent and evaluator from the agent.py file
        agent = AndroidAgent(model, prompt_template, api_key)
        evaluator = Evaluator()
        
        # from the environment we can obtain the episodes 
        episodes = self.env.get_random_episodes(num_episodes)
        
        # Run the evaluation
        start_time = time.time()
        # loop through the episode from the evaluator as then log the end of the episode to show the results
        for episode in episodes:
            try:
                result = evaluator.evaluate_episode(agent, episode)
                self.logger.log_episode_end(episode.episode_id, result.episode_success, result.step_accuracy)
            except Exception as e:
                self.logger.log_error(str(e), f"Episode {episode.episode_id}")
        
        duration = time.time() - start_time
        
        # Save results ot the results directory
        results_file = os.path.join(self.output_dir, f"benchmark_{model}_{prompt_template}.json")
        evaluator.save_results(results_file)
        
        # Generate analysis that will be sent to the results file
        analyzer = ResultsAnalyzer(results_file)
        analyzer.generate_performance_plots(self.output_dir)
        
        return {
            'model': model,
            'prompt_template': prompt_template,
            'results_file': results_file,
            'duration': duration,
            'metrics': evaluator.calculate_aggregate_metrics()
        }
    
    # the comparative benchmark function will run the comparison over multiple configurations
    def run_comparative_benchmark(self, configs: List[Dict], num_episodes: int = 10) -> Dict:
        # start the empty directory to store the results
        all_results = []
        
        # then loop through all configurations which then the results will be appeneded to the result dictionary
        for config in configs:
            result = self.run_single_benchmark(
                config['model'],
                config['prompt_template'],
                config['api_key'],
                num_episodes
            )
            all_results.append(result)
        
        # Generate comparative analysis into a file in the results directory
        comparison_file = os.path.join(self.output_dir, "comparative_analysis.json")
        # write into the generatve analysis file
        with open(comparison_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        return {
            'results': all_results,
            'comparison_file': comparison_file
        }
    
    # this next function will generate a full comprehensive report by making a file in the results folder and altering as the program is run
    def generate_final_report(self, benchmark_results: Dict):
        # this line will generate the final report file as a markdown source file
        report_file = os.path.join(self.output_dir, "final_report.md")
        
        # as a loop, wirte down the certain title and headers that make the readibility of the report better
        with open(report_file, 'w') as f:
            f.write("# Android World LLM Agent Benchmark Results\n\n")
            # this line will denote he time of the program results
            f.write(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # this is where the complete table of data will be placed with the proper metrics
            f.write("## Configuration Summary\n\n")
            f.write("| Model | Prompt Template | Success Rate | Step Accuracy | Duration |\n")
            f.write("|-------|----------------|--------------|---------------|----------|\n")
            
            # loop through the benchmark results along with the model and API that is used
            for result in benchmark_results['results']:
                metrics = result['metrics']
                f.write(f"| {result['model']} | {result['prompt_template']} | "
                       f"{metrics.get('episode_success_rate', 0):.2%} | "
                       f"{metrics.get('average_step_accuracy', 0):.2%} | "
                       f"{result['duration']:.1f}s |\n")
            
            # this snppet of code will highlight the best performing configuration with the written declaration in the final report
            f.write("\n## Best Performing Configuration\n\n")
            best_config = max(benchmark_results['results'], 
                            key=lambda x: x['metrics'].get('episode_success_rate', 0))
            f.write(f"**Model**: {best_config['model']}\n")
            f.write(f"**Prompt Template**: {best_config['prompt_template']}\n")
            f.write(f"**Success Rate**: {best_config['metrics'].get('episode_success_rate', 0):.2%}\n")
            f.write(f"**Step Accuracy**: {best_config['metrics'].get('average_step_accuracy', 0):.2%}\n")