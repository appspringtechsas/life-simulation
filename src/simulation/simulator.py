"""Main simulation engine."""
from typing import Dict, List, Optional, Tuple, Any
import json
import random
from datetime import datetime

from src.agents import Agent
from src.environment import Environment
from src.mcp import MCPTool, ToolRegistry
from src.llm import LLMAgent, parse_agent_response
from .event_logger import EventLogger


class Simulator:
    """Main simulation engine."""
    
    def __init__(self, max_turns: int = 100, max_agents: int = 50):
        """Initialize simulator."""
        self.max_turns = max_turns
        self.environment = Environment(max_agents=max_agents)
        self.agents: Dict[str, Agent] = {}
        self.tool_registry = ToolRegistry()
        self.event_logger = EventLogger()
        self.llm_agent = LLMAgent(self.tool_registry)
        self.current_turn = 0
        self.execution_log: List[Dict[str, Any]] = []
    
    def add_agent(self, agent: Optional[Agent] = None, assign_birth_turn: bool = True) -> Agent:
        """Add agent to simulation. Creates new if not provided."""
        if agent is None:
            agent = Agent()
        
        if assign_birth_turn:
            agent.birth_turn = self.current_turn
        
        self.agents[agent.id] = agent
        self.event_logger.log_birth(
            self.current_turn,
            agent.id,
            agent.name,
            agent.parent_ids
        )
        return agent
    
    def remove_agent(self, agent_id: str, cause: str = "unknown"):
        """Remove dead agent from active agents."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            if not agent.is_alive():
                del self.agents[agent_id]
                self.event_logger.log_death(
                    self.current_turn,
                    agent_id,
                    agent.name,
                    cause
                )
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID."""
        return self.agents.get(agent_id)
    
    def get_living_agents(self) -> List[Agent]:
        """Get all living agents."""
        return [a for a in self.agents.values() if a.is_alive()]
    
    def process_agent_turn(self, agent: Agent) -> Dict[str, Any]:
        """
        Process one turn for an agent.
        Simulate LLM interaction and action execution.
        """
        turn_log = {
            "agent_id": agent.id,
            "agent_name": agent.name,
            "reasoning": "",
            "actions": [],
            "results": [],
        }
        
        # Build prompt for agent
        prompt = self.llm_agent.build_agent_prompt(agent, self.environment)
        
        # Simulate LLM response (in real scenario, call actual LLM)
        response = self._simulate_llm_response(agent)
        
        # Parse response
        parsed = parse_agent_response(response)
        turn_log["reasoning"] = parsed["reasoning"]
        turn_log["actions"] = parsed["actions"]
        
        # Execute actions
        for action in parsed["actions"]:
            result = self._execute_action(agent, action)
            turn_log["results"].append(result)
        
        # Use tools
        for tool_name in parsed["tools_to_use"]:
            result = self._use_tool(agent, tool_name)
            turn_log["results"].append(result)
        
        # Create new tools if agent proposes any
        for new_tool_name in parsed["new_tools_to_create"]:
            result = self._create_custom_tool(agent, new_tool_name)
            turn_log["results"].append(result)
        
        # Apply turn-based costs
        agent.lose_energy(1.0)  # Base metabolism
        
        # Check for hazard damage
        hazard = self.environment.get_hazard_damage()
        if hazard > 0:
            agent.take_damage(hazard)
            turn_log["results"].append(f"Took {hazard:.2f} damage from environmental hazard")
        
        # Check if agent dies
        if not agent.is_alive():
            cause = "starvation" if agent.energy <= 0 else "disease" if agent.health <= 0 else "unknown"
            agent.die(self.current_turn)
            self.remove_agent(agent.id, cause)
            turn_log["results"].append(f"Agent died from {cause}")
        
        return turn_log
    
    def _simulate_llm_response(self, agent: Agent) -> str:
        """Simulate an LLM response based on agent state and needs."""
        # This is a deterministic simulation since we don't have access to real LLM
        actions = []
        tools = []
        
        # Decision logic based on agent state
        if agent.energy < 30:
            actions.append("Search for resources to recover energy")
            tools.append("search_resources")
        
        if agent.health < 40:
            actions.append("Use resources to recover health")
            tools.append("recover_health")
        
        if agent.resources < 20:
            actions.append("Focus on resource gathering")
            tools.append("search_resources")
        
        if random.random() < 0.1 and agent.can_reproduce():
            actions.append("Attempt to reproduce")
        
        if random.random() < 0.05:
            actions.append("Explore new tools and capabilities")
            tools.append("explore_new_tools")
        
        if random.random() < 0.08 and agent.children_ids:
            actions.append("Help my offspring")
            tools.append("help_offspring")
        
        if random.random() < 0.05 and agent.parent_ids:
            actions.append("Help my parent")
            tools.append("help_parent")
        
        if not actions:
            actions.append("Rest and recover")
        
        reasoning = f"Based on my state (energy: {agent.energy:.1f}, health: {agent.health:.1f}, resources: {agent.resources:.1f}), I will..."
        
        response = f"""REASONING: {reasoning}
ACTIONS:
"""
        for action in actions:
            response += f"-> {action}\n"
        
        response += f"TOOLS_TO_USE: {', '.join(tools) if tools else 'none'}\n"
        response += "NEW_TOOLS_TO_CREATE: none\n"
        
        return response
    
    def _execute_action(self, agent: Agent, action: str) -> str:
        """Execute an action for the agent."""
        action_lower = action.lower()
        
        # Search for resources
        if "search" in action_lower and "resource" in action_lower:
            amount = self.environment.request_resources(agent.id, 30)
            agent.gain_resources(amount)
            return f"Searched for resources, found {amount:.1f}"
        
        # Recover health
        elif "recover" in action_lower and "health" in action_lower:
            if agent.spend_resources(15):
                agent.health = min(100.0, agent.health + 20)
                return f"Used resources to recover health to {agent.health:.1f}"
            else:
                return "Insufficient resources to recover health"
        
        # Reproduce
        elif "reproduce" in action_lower:
            if agent.can_reproduce():
                offspring = agent.reproduce()
                if offspring:
                    self.add_agent(offspring)
                    self.event_logger.log_reproduction(
                        self.current_turn,
                        agent.id,
                        agent.name,
                        offspring.id,
                        30,
                        40
                    )
                    return f"Successfully reproduced, created offspring {offspring.name}"
            return "Cannot reproduce at this time"
        
        # Help offspring
        elif "help" in action_lower and ("offspring" in action_lower or "child" in action_lower):
            if agent.children_ids:
                child_id = agent.children_ids[0]  # Help first child
                child = self.get_agent(child_id)
                if child and agent.spend_resources(10):
                    child.gain_resources(10)
                    child.health = min(100.0, child.health + 10)
                    return f"Helped offspring {child.name}"
            return "No offspring to help"
        
        # Help parent
        elif "help" in action_lower and "parent" in action_lower:
            if agent.parent_ids:
                parent_id = agent.parent_ids[0]
                parent = self.get_agent(parent_id)
                if parent and agent.spend_resources(5):
                    parent.gain_resources(5)
                    return f"Helped parent {parent.name}"
            return "No parent to help"
        
        # Rest
        elif "rest" in action_lower:
            agent.energy = min(100.0, agent.energy + 15)
            return f"Rested, energy now {agent.energy:.1f}"
        
        else:
            return f"Action '{action}' processed"
    
    def _use_tool(self, agent: Agent, tool_name: str) -> str:
        """Use an MCP tool."""
        if not self.tool_registry.execute_tool(tool_name):
            return f"Tool '{tool_name}' not available or not enabled"
        
        agent.discovered_tools.append(tool_name)
        
        # Simulate tool effects
        if tool_name == "search_resources":
            amount = random.uniform(20, 50)
            agent.gain_resources(amount)
            return f"Used search_resources tool, gained {amount:.1f} resources"
        
        elif tool_name == "recover_health":
            agent.health = min(100.0, agent.health + 25)
            return f"Used recover_health tool, health now {agent.health:.1f}"
        
        elif tool_name == "explore_new_tools":
            new_tool_chance = random.random()
            if new_tool_chance < 0.3:
                new_tool = self._discover_new_tool(agent)
                return f"Discovered new tool: {new_tool}"
            return "Exploration found no new tools this turn"
        
        else:
            return f"Used tool '{tool_name}'"
    
    def _create_custom_tool(self, agent: Agent, tool_name: str) -> str:
        """Create a custom tool."""
        if agent.spend_resources(20):
            new_tool = MCPTool(
                name=f"custom_{tool_name}_{agent.id[:8]}",
                description=f"Custom tool created by {agent.name}",
                creator_id=agent.id,
            )
            if self.tool_registry.register_tool(new_tool):
                self.event_logger.log_tool_creation(
                    self.current_turn,
                    agent.id,
                    agent.name,
                    new_tool.name
                )
                return f"Created custom tool: {new_tool.name}"
        return "Insufficient resources to create tool"
    
    def _discover_new_tool(self, agent: Agent) -> str:
        """Discover a new tool from the environment."""
        possible_tools = ["advanced_search", "resource_conversion", "health_boost", "data_analysis"]
        tool_name = random.choice(possible_tools)
        full_name = f"{tool_name}_{agent.id[:6]}"
        
        new_tool = MCPTool(
            name=full_name,
            description=f"Tool discovered by {agent.name}",
            creator_id=agent.id,
        )
        
        if self.tool_registry.register_tool(new_tool):
            return full_name
        
        return "discovery_failed"
    
    def run_simulation(self, initial_agents: int = 5, verbose: bool = True) -> Dict[str, Any]:
        """Run the complete simulation."""
        # Initialize agents
        for i in range(initial_agents):
            self.add_agent()
        
        if verbose:
            print(f"\n{'='*60}")
            print("LIFE SIMULATION STARTED")
            print(f"{'='*60}")
            print(f"Initial agents: {len(self.agents)}")
            print(f"Max turns: {self.max_turns}")
            print(f"Max agents: {self.environment.max_agents}\n")
        
        # Run simulation loop
        for turn in range(self.max_turns):
            self.current_turn = turn
            self.environment.turn = turn
            self.environment.update()
            
            turn_log = {
                "turn": turn,
                "agents_alive": len(self.get_living_agents()),
                "agent_turns": [],
            }
            
            # Process each living agent
            living_agents = self.get_living_agents().copy()
            for agent in living_agents:
                agent_turn = self.process_agent_turn(agent)
                turn_log["agent_turns"].append(agent_turn)
            
            self.execution_log.append(turn_log)
            
            # Print turn summary
            if verbose and turn % 10 == 0:
                print(f"Turn {turn}: {len(self.get_living_agents())} agents alive, "
                      f"resources: {self.environment.resources_available:.1f}")
            
            # Check if simulation should end
            if len(self.get_living_agents()) == 0:
                if verbose:
                    print(f"\nSimulation ended at turn {turn}: All agents dead")
                break
        
        return self.get_simulation_report()
    
    def get_simulation_report(self) -> Dict[str, Any]:
        """Generate a report of the simulation."""
        event_summary = self.event_logger.get_events_summary()
        
        return {
            "total_turns": self.current_turn,
            "agents_alive": len(self.get_living_agents()),
            "total_agents_created": len(self.agents) + len([e for e in self.event_logger.events if e.event_type == "death"]),
            "events": event_summary,
            "environment_state": self.environment.to_state_dict(),
            "tool_registry_size": len(self.tool_registry.get_all_tools()),
            "simulation_status": "completed",
        }
    
    def save_state(self, filename: str):
        """Save simulation state to JSON."""
        state = {
            "current_turn": self.current_turn,
            "agents": {aid: agent.to_state_dict() for aid, agent in self.agents.items()},
            "environment": self.environment.to_state_dict(),
            "events": json.loads(self.event_logger.to_json()),
            "tools": [tool.to_dict() for tool in self.tool_registry.get_all_tools()],
        }
        
        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self, filename: str):
        """Load simulation state from JSON."""
        with open(filename, 'r') as f:
            state = json.load(f)
        
        self.current_turn = state["current_turn"]
        self.environment.turn = self.current_turn
        
        # Load agents
        self.agents.clear()
        for agent_data in state.get("agents", {}).values():
            agent = Agent.from_state_dict(agent_data)
            self.agents[agent.id] = agent
