
"""
agent.py - Core LLM Agent Implementation for Android World Evaluation

This file implements the AndroidAgent class, which serves as the primary interface
for Large Language Model agents operating in the Android World environment.

Key Components:
- Episode: Data class representing a single evaluation episode with goal, observations, and actions
- AndroidAgent: Main agent class that generates actions based on observations and goals
- Multiple prompt templates: base, few-shot, and self-reflection prompting strategies
- LLM integration: Support for both OpenAI (GPT) and Anthropic (Claude) models
- Action parsing: Robust parsing of LLM responses into structured actions

The agent follows a simple loop:
1. Receive goal and current observation
2. Generate contextual prompt based on template
3. Query LLM for next action
4. Parse and validate the response
5. Return structured action for environment

Usage:
    agent = AndroidAgent(model_name="gpt-4", prompt_template="few_shot", api_key="...")
    action = agent.generate_action(goal="Uninstall app", observation=obs_dict)
"""

# src/agent.py
import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import openai
from anthropic import Anthropic

 # this class will be based on the the data class
@dataclass
class Episode:
    goal: str
    observations: List[Dict]
    actions: List[str]
    episode_id: str


# this will identify the android agent 
class AndroidAgent:
    def __init__(self, model_name: str = "gpt-4", prompt_template: str = "base", api_key: str = None):
        self.model_name = model_name
        self.prompt_template = prompt_template
        self.action_history = []
        
        # This next part of the code will initialize the evaluator based on the andrioid agent
        if "gpt" in model_name.lower():
            self.client = openai.OpenAI(api_key=api_key)
            self.provider = "openai"
        elif "claude" in model_name.lower():
            self.client = Anthropic(api_key=api_key)
            self.provider = "anthropic"
        else:
            raise ValueError(f"Unsupported model: {model_name}")
    
    """Generate next action given goal and current observation"""
    def generate_action(self, goal: str, observation: Dict, history: Optional[List] = None) -> str:
        prompt = self._format_prompt(goal, observation, history)
        response = self._call_llm(prompt)
        action = self._parse_action(response)
        
        # then we need to store the data in the storage database
        self.action_history.append({
            'observation': observation,
            'action': action,
            'response': response
        })
        
        return action
    
    #this method will determine the format prompt based on the template that is chosen to give a the best final determination
    def _format_prompt(self, goal: str, observation: Dict, history: Optional[List] = None) -> str:
        if self.prompt_template == "base":
            return self._base_prompt(goal, observation)
        elif self.prompt_template == "few_shot":
            return self._few_shot_prompt(goal, observation, history)
        elif self.prompt_template == "self_reflection":
            return self._self_reflection_prompt(goal, observation, history)
        else:
            raise ValueError(f"Unknown prompt template: {self.prompt_template}")
    
    # this function will yield the base prompt 
    def _base_prompt(self, goal: str, observation: Dict) -> str:
        """Basic prompt template"""
        ui_elements = observation.get('ui_elements', [])
        app_name = observation.get('app', 'Unknown')
        
        return f"""Goal: {goal}
        Observation:
        - App: {app_name}
        - UI Elements: {ui_elements}
        What is the next best action to achieve the goal? Respond in the format:
        CLICK("element_name") or SCROLL("direction") or TYPE("text")
        Action:"""
    
    # this function will output the prmots based on the input prompts
    def _few_shot_prompt(self, goal: str, observation: Dict, history: Optional[List] = None) -> str:
        """Few-shot prompt with examples"""
        examples = """Examples:
Goal: Open calculator app
Observation: App: Home, UI Elements: ["Calculator", "Settings", "Chrome"]
Action: CLICK("Calculator")

Goal: Uninstall app
Observation: App: Settings, UI Elements: ["Apps", "Display", "Sound"]
Action: CLICK("Apps")

Goal: Send message "Hello"
Observation: App: Messages, UI Elements: ["Compose", "Search", "Settings"]
Action: CLICK("Compose")
"""
        
        base_prompt = self._base_prompt(goal, observation)
        return examples + "\n" + base_prompt
    
    def _self_reflection_prompt(self, goal: str, observation: Dict, history: Optional[List] = None) -> str:
        """Self-reflection prompt"""
        base_prompt = self._base_prompt(goal, observation)
        
        reflection_prompt = """
Before choosing an action, consider:
1. What is the current state of the app?
2. What UI elements are available?
3. Which action will move me closer to the goal?
4. Are there any intermediate steps needed?

Reasoning: [Explain your thought process]
Action: [Your chosen action]
"""
        
        return base_prompt + reflection_prompt
     
    # The function will call the appropriate LLm API
    def _call_llm(self, prompt: str) -> str:
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=150
                )
                return response.choices[0].message.content
            
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=150,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
       # need to handle any potental errors 
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return "ERROR"
        
    # this function will extract action from the response of the large language model
    def _parse_action(self, response: str) -> str:
        # Look for action patterns
        action_patterns = [
            r'CLICK\(["\']([^"\']*)["\']\)',
            r'SCROLL\(["\']([^"\']*)["\']\)',
            r'TYPE\(["\']([^"\']*)["\']\)',
            r'SWIPE\(["\']([^"\']*)["\']\)'
        ]
        
        # look through the patternes to see if there is a match and if there is match classify and add to the match group
        for pattern in action_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                action_type = pattern.split('\\(')[0].replace('r\'', '')
                return f'{action_type}("{match.group(1)}")'
        
        # If no pattern matched, return the response as-is
        return response.strip()
    
    # All the agents need a reset for the new episode so the history will be set to 
    def reset_history(self):
        self.action_history = []