"""LLM integration for agent decision-making."""
from typing import Dict, List, Any, Optional, Tuple
import json
import re
import os
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

from src.agents import Agent
from src.environment import Environment
from src.mcp import ToolRegistry

# Load environment variables from .env file
load_dotenv()


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

    def get_response(self, agent: Agent, environment: Environment, model: str = "gpt-3.5-turbo") -> str:
        """
        Build a prompt for an agent and call an external LLM (OpenAI by default).
        Raises a RuntimeError when the OpenAI package or API is not available so callers
        can fall back to the internal simulator.
        """
        prompt = self.build_agent_prompt(agent, environment)
        system_prompt = self.get_system_prompt()

        # Helper to attempt many common response shapes (OpenAI, Gemini, genai, etc.)
        def _extract_text(resp_obj) -> str:
            # handle new openai response format first
            try:
                if hasattr(resp_obj, "choices") and hasattr(resp_obj.choices[0], "message"):
                    return resp_obj.choices[0].message.content
            except Exception:
                pass

            # dict-like access
            try:
                if isinstance(resp_obj, dict):
                    # OpenAI ChatCompletion
                    if "choices" in resp_obj:
                        try:
                            return resp_obj["choices"][0]["message"]["content"]
                        except Exception:
                            pass
                    # Gemini / genai -> candidates
                    if "candidates" in resp_obj:
                        cand = resp_obj["candidates"][0]
                        if isinstance(cand, dict) and "content" in cand:
                            return cand["content"]
                        # some responses embed output
                    if "output" in resp_obj:
                        out = resp_obj["output"]
                        if isinstance(out, list) and len(out) > 0:
                            first = out[0]
                            if isinstance(first, dict) and "content" in first:
                                return first["content"]
                    if "message" in resp_obj and isinstance(resp_obj["message"], dict):
                        msg = resp_obj["message"]
                        if "content" in msg:
                            return msg["content"]
                    # direct text
                    if "text" in resp_obj and isinstance(resp_obj["text"], str):
                        return resp_obj["text"]
                # attribute access
                if hasattr(resp_obj, "text"):
                    return getattr(resp_obj, "text")
                if hasattr(resp_obj, "choices"):
                    try:
                        ch = getattr(resp_obj, "choices")
                        return ch[0].message.content
                    except Exception:
                        pass
                if hasattr(resp_obj, "candidates"):
                    cand = getattr(resp_obj, "candidates")
                    try:
                        first = cand[0]
                        if isinstance(first, dict) and "content" in first:
                            return first["content"]
                        if hasattr(first, "content"):
                            return getattr(first, "content")
                    except Exception:
                        pass
            except Exception:
                pass

            # Fallback to string representation
            return str(resp_obj)

        # If the model looks like Gemini, try Google genai client (successor to google-generativeai)
        if "gemini" in model.lower():
            try:
                import google.genai  # type: ignore
            except Exception as exc:
                raise RuntimeError("google-genai package not installed; install with 'pip install .[gemini]' to use Gemini models") from exc

            # Get API key
            gkey = os.getenv("GOOGLE_API_KEY") or os.getenv("GEN_API_KEY")
            if not gkey:
                raise RuntimeError("GOOGLE_API_KEY or GEN_API_KEY environment variable not set")

            # Use the new google-genai Client API
            try:
                client = google.genai.Client(api_key=gkey)
                resp = client.models.generate_content(
                    model=model,
                    contents=system_prompt + "\n\n" + prompt,
                )
            except Exception as exc:
                raise RuntimeError(f"Gemini API request failed: {exc}") from exc
            
            content = _extract_text(resp).strip()

            # Save to local history for debugging/inspection
            self.response_history.append({"agent_id": agent.id, "prompt": prompt, "response": content})

            return content

        # Default: OpenAI-compatible flow
        try:
            from azure.ai.inference import ChatCompletionsClient
        except Exception as exc:
            raise RuntimeError("openai package not installed; install with 'pip install openai' to use a real LLM") from exc

        # Allow using environment variable for API key
        token = os.getenv("GITHUB_TOKEN")
        # Allow using environment variable for API base URL
        base_url = os.getenv("OPENAI_API_BASE")
        
        if not token:
            raise RuntimeError("OPENAI_API_KEY environment variable not set")

        endpoint = base_url
        model_name = model


        client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(token),
        )

        try:
            response = client.complete(
                messages=[
                    SystemMessage(content=system_prompt),
                    UserMessage(prompt),
                ],
                temperature=1.0,
                top_p=1.0,
                max_tokens=1000,
                model=model_name
            )
            
        except Exception as exc:
            # Surface a helpful error for the simulator to catch and fallback
            raise RuntimeError(f"LLM request failed: {exc}") from exc

        content = _extract_text(response).strip()

        # Save to local history for debugging/inspection
        self.response_history.append({"agent_id": agent.id, "prompt": prompt, "response": content})

        return content


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
