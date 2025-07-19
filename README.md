QualGent Research Coding Challenge: Evaluating LLM
Agents in Android World
Objective
Design a lightweight evaluation framework to test how well LLMs can act as agents in mobile
environments, using the android_world benchmark. You’ll evaluate LLMs' ability to navigate
simulated Android apps by reasoning over observations and generating valid actions to reach
specific goals.
Setup & Agent Framework Scaffold
Goal: Load the environment, inspect episodes, and build a minimal agent loop.
Tasks:
● Clone the android_world repo.
● Explore a few episodes in the dataset:
○ Each episode has a goal, a sequence of observations, and a ground-truth action
trace.
● Build a Python scaffold that:
○ Loads one episode
○ Shows the goal and first observation
○ Lets you prompt an LLM (e.g., GPT-4 or Claude) to generate the next action
Suggested Prompt Format:
None
Goal: Uninstall the Slack app
Observation:
- App: Settings
- UI Elements: ["Apps", "Search", "Battery", ...]
What is the next best action? Respond in the format:
CLICK("Apps")
Deliverables:
● Basic agent loop (input: goal + observation, output: LLM-generated action)
● Configurable prompt template
● Script to run agent on 1 full episode
Prompting & Evaluation Strategy
Goal: Improve prompting and evaluate model behavior over multiple steps.
Tasks:
● Implement one or both:
○ Few-shot prompting: Include examples of good agent steps
○ Self-reflection: Ask the model to explain why it chose an action
● Run your agent on 3+ full episodes
● Compare generated actions to ground-truth using:
○ Exact match on action strings (e.g., CLICK("Apps"))
○ Episode success (did it reach the goal?)
○ Step accuracy (% of correct actions)
Optional:
● Add basic error handling (e.g., if LLM hallucinates UI elements not in observation)
● Use OpenAI's function_calling or Claude’s tool_use for structured output
Deliverables:
● Evaluation loop
● At least two prompt variants tested
● Per-episode logs of predictions vs. ground truth
Benchmarking & Report
Goal: Benchmark performance and reflect on LLM capabilities and limitations.
Tasks:
● Run your evaluation on at least 10 episodes
● Report:
○ Average step accuracy
○ Episode success rate
○ Failure analysis: Where and why do LLMs go wrong?
● Highlight interesting behaviors:
○ Hallucinated actions?
○ Misinterpretation of goals?
○ UI reasoning limitations?
Write a short markdown/PDF report including:
● Your approach to prompting and evaluation
● Summary of performance metrics
● 2–3 illustrative example episodes
● Recommendations for improving agent behavior (e.g., memory, search, retries)
Bonus (Optional):
● Integrate a memory buffer (e.g., full history of actions and observations)
● Compare GPT-4 vs Claude vs Mistral
● Add visualization of episode progress (optional CLI or Streamlit tool)
Expected Deliverables
● src/: Code for agent, prompts, evaluation
● prompts/: Your few-shot examples and templates
● results/: Logs and structured outputs
● report.md: 1–2 page write-up of what you tried and what you learned
Requirements
● Python 3.x
● Any LLM API (OpenAI, Anthropic, HuggingFace)
● Can use libraries: openai, langchain, json, pydantic, fuzzywuzzy, etc.
Evaluation Criteria
● Prompting and reasoning quality
● Correct use of dataset structure (goals, observations, actions)
● Thoughtfulness of evaluation design
● Clarity of code and report
