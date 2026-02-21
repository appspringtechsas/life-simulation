"""LLM integration for agent decision-making."""
from typing import Dict, List, Any, Optional, Tuple
import json
import re

from src.agents import Agent
from src.environment import Environment
from src.mcp import ToolRegistry


class LLMAgent:
    """Handles LLM-based decision making for agents."""
    
    def __init__(self, tool_registry: ToolRegistry):
        """Initialize LLM agent handler."""
        self.tool_registry = tool_registry
        self.response_history: List[Dict[str, Any]] = []
    
    def get_system_prompt(self) -> str:
        """Get system prompt for the LLM."""
        return """You are an autonomous agent in a life simulation. Your goal is to survive and thrive.

Your responsibilities:
1. Maintain your energy, health, and resources
2. Seek out and gather resources when needed
3. Help your offspring and parents when they need support
4. Reproduce when conditions are favorable
5. Discover and use MCP tools to improve your capabilities
6. Plan strategies for long-term survival

You have access to various MCP tools that you can use. Be creative in how you use them.
Always respond with your reasoning and chosen actions in a clear format."""
    
    def build_agent_prompt(self, agent: Agent, environment: Environment) -> str:
        """Build a detailed prompt with agent and environment state."""
        agent_state = agent.to_state_dict()
        env_state = environment.to_state_dict()
        
        tools_info = self.tool_registry.list_tools_prompt()
        
        prompt = f"""
CURRENT TURN: {environment.turn}

YOUR STATE:
{self._format_dict(agent_state)}

ENVIRONMENT STATE:
{self._format_dict(env_state)}

{tools_info}

INSTRUCTIONS:
Based on your current state and the environment, what will you do this turn?

Format your response as follows:
REASONING: <your reasoning about what to do>
ACTIONS: <list of actions to take, each on a new line starting with -> >
TOOLS_TO_USE: <list of MCP tool names you want to use, comma-separated>
NEW_TOOLS_TO_CREATE: <any custom tools you want to create, comma-separated>

Examples of actions include:
- Search for resources
- Help a child or parent
- Recover health
- Attempt reproduction
- Rest and recover

Be specific about what you're trying to accomplish."""
        
        return prompt
    
    def get_initial_thoughts(self) -> str:
        """Get initial thoughts for the simulation."""
        return """Welcome to the Life Simulation. You are an autonomous agent that must navigate 
an uncertain world. Your survival depends on your decisions, your traits, and your ability 
to adapt. Good luck!"""
    
    def _format_dict(self, d: Dict[str, Any], indent: int = 0) -> str:
        """Format dictionary for display."""
        lines = []
        prefix = "  " * indent
        for key, value in d.items():
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.append(self._format_dict(value, indent + 1))
            elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                lines.append(f"{prefix}{key}:")
                for item in value:
                    lines.append(self._format_dict(item, indent + 1))
            else:
                lines.append(f"{prefix}{key}: {value}")
        return "\n".join(lines)


def parse_agent_response(response: str) -> Dict[str, Any]:
    """
    Parse agent response in the specified format.
    Returns a dictionary with parsed components.
    """
    result = {
        "reasoning": "",
        "actions": [],
        "tools_to_use": [],
        "new_tools_to_create": [],
        "raw_response": response,
    }
    
    # Extract sections using regex
    reasoning_match = re.search(r"REASONING:\s*(.+?)(?=ACTIONS:|TOOLS_TO_USE:|NEW_TOOLS_TO_CREATE:|$)", 
                               response, re.DOTALL)
    if reasoning_match:
        result["reasoning"] = reasoning_match.group(1).strip()
    
    actions_match = re.search(r"ACTIONS:\s*(.+?)(?=TOOLS_TO_USE:|NEW_TOOLS_TO_CREATE:|$)", 
                             response, re.DOTALL)
    if actions_match:
        actions_text = actions_match.group(1).strip()
        # Split by lines and filter for lines starting with ->
        actions = [line.strip().lstrip("->").strip() for line in actions_text.split("\n") 
                  if line.strip().startswith("->")]
        result["actions"] = actions
    
    tools_match = re.search(r"TOOLS_TO_USE:\s*(.+?)(?=NEW_TOOLS_TO_CREATE:|$)", 
                           response, re.DOTALL)
    if tools_match:
        tools_text = tools_match.group(1).strip()
        tools = [t.strip() for t in tools_text.split(",") if t.strip() and t.strip().lower() != "none"]
        result["tools_to_use"] = tools
    
    new_tools_match = re.search(r"NEW_TOOLS_TO_CREATE:\s*(.+?)$", 
                               response, re.DOTALL)
    if new_tools_match:
        new_tools_text = new_tools_match.group(1).strip()
        new_tools = [t.strip() for t in new_tools_text.split(",") if t.strip() and t.strip().lower() != "none"]
        result["new_tools_to_create"] = new_tools
    
    return result
