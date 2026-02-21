"""MCP Tools system for dynamic tool management."""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Callable, Optional
import json


@dataclass
class MCPTool:
    """Represents a MCP Tool that agents can use."""
    
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    creator_id: Optional[str] = None  # Agent ID that created this tool
    enabled: bool = True
    execution_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "creator_id": self.creator_id,
            "enabled": self.enabled,
            "execution_count": self.execution_count,
        }


class ToolRegistry:
    """Registry for managing MCP tools."""
    
    def __init__(self):
        """Initialize tool registry."""
        self._tools: Dict[str, MCPTool] = {}
        self._history: List[Dict[str, Any]] = []
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tools available to agents."""
        default_tools = [
            MCPTool(
                name="search_resources",
                description="Search for resources in the environment",
                parameters={
                    "search_radius": {"type": "float", "description": "Search radius"},
                    "intensity": {"type": "float", "description": "Search intensity (0-1)"}
                }
            ),
            MCPTool(
                name="consume_energy",
                description="Consume energy for actions",
                parameters={
                    "amount": {"type": "float", "description": "Energy amount to consume"}
                }
            ),
            MCPTool(
                name="recover_health",
                description="Recover health using resources",
                parameters={
                    "resource_amount": {"type": "float", "description": "Resources to spend"}
                }
            ),
            MCPTool(
                name="help_offspring",
                description="Help offspring with resources or health",
                parameters={
                    "offspring_id": {"type": "str", "description": "ID of offspring"},
                    "resource_transfer": {"type": "float", "description": "Resources to transfer"},
                    "health_boost": {"type": "float", "description": "Health boost to give"}
                }
            ),
            MCPTool(
                name="help_parent",
                description="Help parent with resources or health",
                parameters={
                    "parent_id": {"type": "str", "description": "ID of parent"},
                    "resource_transfer": {"type": "float", "description": "Resources to transfer"}
                }
            ),
            MCPTool(
                name="explore_new_tools",
                description="Discover and learn new MCP tools",
                parameters={
                    "exploration_effort": {"type": "float", "description": "Effort to explore (0-100)"}
                }
            ),
            MCPTool(
                name="get_agent_state",
                description="Get current state of the agent",
                parameters={}
            ),
            MCPTool(
                name="get_environment_state",
                description="Get current state of the environment",
                parameters={}
            ),
        ]
        
        for tool in default_tools:
            self._tools[tool.name] = tool
            self._record_action("register", tool.name, None, "Default tool registered")
    
    def register_tool(self, tool: MCPTool) -> bool:
        """Register a new tool. Returns True if successful."""
        if tool.name in self._tools:
            return False
        self._tools[tool.name] = tool
        self._record_action("register", tool.name, tool.creator_id, f"Custom tool created")
        return True
    
    def unregister_tool(self, tool_name: str, requester_id: Optional[str] = None) -> bool:
        """Unregister a tool. Returns True if successful."""
        if tool_name not in self._tools:
            return False
        tool = self._tools[tool_name]
        del self._tools[tool_name]
        self._record_action("unregister", tool_name, requester_id, f"Tool removed")
        return True
    
    def enable_tool(self, tool_name: str) -> bool:
        """Enable a tool. Returns True if successful."""
        if tool_name not in self._tools:
            return False
        self._tools[tool_name].enabled = True
        self._record_action("modify", tool_name, None, "Tool enabled")
        return True
    
    def disable_tool(self, tool_name: str) -> bool:
        """Disable a tool. Returns True if successful."""
        if tool_name not in self._tools:
            return False
        self._tools[tool_name].enabled = False
        self._record_action("modify", tool_name, None, "Tool disabled")
        return True
    
    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """Get a tool by name."""
        return self._tools.get(tool_name)
    
    def get_enabled_tools(self) -> List[MCPTool]:
        """Get all enabled tools."""
        return [t for t in self._tools.values() if t.enabled]
    
    def get_all_tools(self) -> List[MCPTool]:
        """Get all tools (enabled and disabled)."""
        return list(self._tools.values())
    
    def execute_tool(self, tool_name: str) -> bool:
        """Execute a tool. Returns True if successful."""
        tool = self.get_tool(tool_name)
        if not tool or not tool.enabled:
            return False
        tool.execution_count += 1
        self._record_action("execute", tool_name, None, f"Execution count: {tool.execution_count}")
        return True
    
    def list_tools_prompt(self) -> str:
        """Get a formatted list of available tools for the LLM."""
        enabled = self.get_enabled_tools()
        if not enabled:
            return "No tools currently available."
        
        tools_info = []
        for tool in enabled:
            info = f"- {tool.name}: {tool.description}"
            if tool.parameters:
                params = ", ".join(f"{k} ({v.get('type', 'unknown')})" 
                                  for k, v in tool.parameters.items())
                info += f" [Parameters: {params}]"
            tools_info.append(info)
        
        return "Available MCP Tools:\n" + "\n".join(tools_info)
    
    def _record_action(self, action: str, tool_name: str, agent_id: Optional[str], details: str):
        """Record action in history."""
        self._history.append({
            "action": action,
            "tool_name": tool_name,
            "agent_id": agent_id,
            "details": details,
        })
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get tool registry history."""
        return self._history.copy()
