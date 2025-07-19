"""
main.py - Command-Line Interface for Android World LLM Agent Evaluation

This file provides the main entry point for running individual LLM agent evaluations
on the Android World benchmark. It offers a simple command-line interface for testing
single model-prompt combinations with configurable parameters.

Key Features:
- Command-line argument parsing for evaluation parameters
- Single-run evaluation mode (vs. comparative benchmarking)
- Configurable model selection (GPT-4, Claude, etc.)
- Prompt template selection (base, few-shot, self-reflection)
- Customizable episode sampling size
- Real-time progress tracking and results summary
- Automatic results saving in JSON format

Arguments:
- --data_path: Path to Android World dataset directory (required)
- --model: LLM model to use (default: gpt-4)
- --prompt_template: Prompting strategy to use (base/few_shot/self_reflection)
- --num_episodes: Number of episodes to evaluate (default: 10)
- --api_key: API key for the selected LLM service (required)
- --output_dir: Directory for saving results (default: results/)

Usage Examples:
    # Basic GPT-4 evaluation
    python main.py --data_path android_world_data/ --api_key sk-...
    
    # Claude with few-shot prompting
    python main.py --data_path android_world_data/ --model claude-3-sonnet 
                   --prompt_template few_shot --api_key your_anthropic_key
    
    # Extended evaluation with 25 episodes
    python main.py --data_path android_world_data/ --num_episodes 25 --api_key sk-...
"""
import argparse
import os
from agent import AndroidAgent
from environment import AndroidWorldEnvironment
from evaluator import Evaluator

def main():
    parser = argparse.ArgumentParser(description="Evaluate LLM agents on Android World")
    parser.add_argument("--data_path", required=True, help="Path to android_world dataset")
    parser.add_argument("--model", default="gpt-4", help="Model to use (gpt-4, claude-3)")
    parser.add_argument("--prompt_template", default="base", choices=["base", "few_shot", "self_reflection"])
    parser.add_argument("--num_episodes", type=int, default=10, help="Number of episodes to evaluate")
    parser.add_argument("--api_key", required=True, help="API key for LLM")
    parser.add_argument("--output_dir", default="results", help="Output directory for results")
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize components
    env = AndroidWorldEnvironment(args.data_path)
    agent = AndroidAgent(args.model, args.prompt_template, args.api_key)
    evaluator = Evaluator()
    
    # Get episodes to evaluate
    episodes = env.get_random_episodes(args.num_episodes)
    
    print(f"Evaluating {len(episodes)} episodes with {args.model} using {args.prompt_template} prompting...")
    
    # Run evaluation
    for i, episode in enumerate(episodes):
        print(f"Episode {i+1}/{len(episodes)}: {episode.goal}")
        result = evaluator.evaluate_episode(agent, episode)
        print(f"  Step accuracy: {result.step_accuracy:.2f}, Success: {result.episode_success}")
    
    # Save results
    # have to fix the directory
    results_file = os.path.join(args.output_dir, f"results_{args.model}_{args.prompt_template}.json")
    evaluator.save_results(results_file)
    
    # Print summary
    metrics = evaluator.calculate_aggregate_metrics()
    print("\nSummary:")
    print(f"Episode success rate: {metrics['episode_success_rate']:.2f}")
    print(f"Average step accuracy: {metrics['average_step_accuracy']:.2f}")
    print(f"Results saved to: {results_file}")

if __name__ == "__main__":
    main()