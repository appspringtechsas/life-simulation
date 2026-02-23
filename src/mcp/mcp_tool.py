"""MCP Tools system for dynamic tool management."""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Callable, Optional
import json
import time
import uuid
import os
try:
    # use stdlib to avoid new dependency; optional webhook support
    from urllib import request as _urlrequest, error as _urlerror
except Exception:
    _urlrequest = None
    _urlerror = None


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
        # Structure for real-world tasks that require human approval
        # Each task: {id, tool_name, agent_id, details, status, created_at, approved_at, outcome}
        self._real_world_tasks: List[Dict[str, Any]] = []
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

    # --- Real world task workflow ---
    def create_real_world_task(self, tool_name: str, agent_id: str, details: Dict[str, Any]) -> str:
        """Create a real-world task that requires human approval.

        Args:
            tool_name: Name of the tool/action
            agent_id: ID of requesting agent
            details: Must include 'proposed_cost' (resources agent will gain),
                     'expected_outcome' (what the agent will do), and optional
                     'description' for human clarity.
        Returns: task id
        """
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "tool_name": tool_name,
            "agent_id": agent_id,
            "details": details,
            "status": "pending_approval",  # pending_approval -> executing -> awaiting_evidence_approval -> approved/rejected
            "created_at": time.time(),
            "approved_at": None,
            "execution_started_at": None,
            "evidence_submitted_at": None,
            "evidence_approved_at": None,
            "outcome": None,
            "proposed_cost": details.get("proposed_cost", 0),
            "expected_outcome": details.get("expected_outcome", ""),
            "deliverables": None,  # Agent submits evidence here
        }
        self._real_world_tasks.append(task)
        self._record_action("real_world_task_created", tool_name, agent_id, f"Task {task_id} created")
        # Notify humans (optional Slack webhook)
        self._notify_human_channel(task)
        return task_id

    def get_pending_real_world_tasks(self) -> List[Dict[str, Any]]:
        """Return list of pending real-world tasks."""
        return [t for t in self._real_world_tasks if t["status"] == "pending_approval"]

    def get_executing_real_world_tasks(self) -> List[Dict[str, Any]]:
        """Return tasks currently being executed by agents."""
        return [t for t in self._real_world_tasks if t["status"] == "executing"]

    def get_awaiting_evidence_tasks(self) -> List[Dict[str, Any]]:
        """Return tasks awaiting human review of submitted deliverables/evidence."""
        return [t for t in self._real_world_tasks if t["status"] == "awaiting_evidence_approval"]

    def approve_real_world_task(self, task_id: str, outcome: Optional[Dict[str, Any]] = None) -> bool:
        """Approve a pending_approval real-world task and move it to executing status.
        
        The agent can now proceed with the task execution."""
        for t in self._real_world_tasks:
            if t["id"] == task_id and t["status"] == "pending_approval":
                t["status"] = "approved"
                t["approved_at"] = time.time()
                t["execution_started_at"] = time.time()
                t["status"] = "executing"  # move directly to executing
                t["outcome"] = outcome or {}
                self._record_action("real_world_task_approved", t["tool_name"], t["agent_id"], f"Task {task_id} approved, agent can begin execution")
                return True
        return False

    def reject_real_world_task(self, task_id: str, reason: Optional[str] = None) -> bool:
        """Reject a pending_approval task."""
        for t in self._real_world_tasks:
            if t["id"] == task_id and t["status"] == "pending_approval":
                t["status"] = "rejected"
                t["approved_at"] = time.time()
                t["outcome"] = {"rejected_reason": reason}
                self._record_action("real_world_task_rejected", t["tool_name"], t["agent_id"], f"Task {task_id} rejected: {reason}")
                return True
        return False

    def submit_task_evidence(self, task_id: str, deliverables: Dict[str, Any]) -> bool:
        """Agent submits evidence/deliverables that the task is complete.
        
        Moves task to awaiting_evidence_approval status so human can review."""
        for t in self._real_world_tasks:
            if t["id"] == task_id and t["status"] == "executing":
                t["status"] = "awaiting_evidence_approval"
                t["evidence_submitted_at"] = time.time()
                t["deliverables"] = deliverables
                self._record_action("task_evidence_submitted", t["tool_name"], t["agent_id"], f"Task {task_id} evidence submitted, awaiting human review")
                self._notify_evidence_review_channel(t)
                return True
        return False

    def approve_task_evidence(self, task_id: str) -> bool:
        """Human approves the submitted evidence/deliverables.
        
        Agent receives the full proposed_cost on next turn."""
        for t in self._real_world_tasks:
            if t["id"] == task_id and t["status"] == "awaiting_evidence_approval":
                t["status"] = "approved"
                t["evidence_approved_at"] = time.time()
                self._record_action("task_evidence_approved", t["tool_name"], t["agent_id"], f"Task {task_id} evidence approved, agent will receive {t['proposed_cost']} resources")
                return True
        return False

    def reject_task_evidence(self, task_id: str, reason: Optional[str] = None) -> bool:
        """Human rejects the evidence; task goes back to executing for retry."""
        for t in self._real_world_tasks:
            if t["id"] == task_id and t["status"] == "awaiting_evidence_approval":
                t["status"] = "executing"
                t["outcome"] = {"evidence_rejected_reason": reason}
                self._record_action("task_evidence_rejected", t["tool_name"], t["agent_id"], f"Task {task_id} evidence rejected: {reason}")
                return True
        return False

    def get_and_clear_approved_tasks(self) -> List[Dict[str, Any]]:
        """Return approved (evidence accepted) tasks and remove them from the task pool."""
        approved = [t for t in self._real_world_tasks if t["status"] == "approved"]
        # keep rejected/pending in the list, remove approved
        self._real_world_tasks = [t for t in self._real_world_tasks if t["status"] != "approved"]
        return approved

    def _notify_human_channel(self, task: Dict[str, Any]):
        """Notify human to review and approve task proposal + proposed cost and expected outcome."""
        webhook = os.environ.get("SLACK_WEBHOOK_URL")
        proposed_cost = task.get("proposed_cost", 0)
        expected_outcome = task.get("expected_outcome", "")
        base_approval = os.environ.get("APPROVAL_BASE_URL") or os.environ.get("APPROVAL_HOST")
        token = os.environ.get("APPROVAL_TOKEN")
        details_json = json.dumps(task["details"])
        text = f"""Real-world task created: {task['id']}
Tool: {task['tool_name']}
Agent: {task['agent_id']}
Proposed Cost (resources agent will gain if approved): {proposed_cost}
Expected Outcome: {expected_outcome}
Details: {details_json}"""
        # If an approval server base URL is provided, include approve/reject links
        if base_approval:
            # ensure no trailing slash
            base = base_approval.rstrip("/")
            approve_url = f"{base}/approve/{task['id']}"
            reject_url = f"{base}/reject/{task['id']}"
            if token:
                approve_url += f"?token={token}"
                reject_url += f"?token={token}"
            text += f"\n\nApprove task: {approve_url}\nReject task: {reject_url}"

        self._record_action("notify_human", task["tool_name"], task["agent_id"], text)
        if webhook and _urlrequest is not None:
            payload = json.dumps({"text": text}).encode("utf-8")
            req = _urlrequest.Request(webhook, data=payload, headers={"Content-Type": "application/json"})
            try:
                resp = _urlrequest.urlopen(req, timeout=5)
                self._record_action("notify_human_result", task["tool_name"], task["agent_id"], f"Slack response: {getattr(resp, 'status', 'ok')}")
            except Exception as e:
                self._record_action("notify_human_error", task["tool_name"], task["agent_id"], f"Slack notify failed: {e}")

    def _notify_evidence_review_channel(self, task: Dict[str, Any]):
        """Notify human to review submitted evidence/deliverables."""
        webhook = os.environ.get("SLACK_WEBHOOK_URL")
        base_approval = os.environ.get("APPROVAL_BASE_URL") or os.environ.get("APPROVAL_HOST")
        token = os.environ.get("APPROVAL_TOKEN")
        deliverables_json = json.dumps(task.get("deliverables") or {})
        text = f"""Task evidence submitted: {task['id']}
Agent: {task['agent_id']}
Tool: {task['tool_name']}
Expected Outcome: {task.get('expected_outcome', '')}
Deliverables/Evidence: {deliverables_json}
Proposed Cost: {task.get('proposed_cost', 0)} resources (if approved)"""
        if base_approval:
            base = base_approval.rstrip("/")
            approve_url = f"{base}/approve_evidence/{task['id']}"
            reject_url = f"{base}/reject_evidence/{task['id']}"
            if token:
                approve_url += f"?token={token}"
                reject_url += f"?token={token}"
            text += f"\n\nApprove evidence: {approve_url}\nReject evidence: {reject_url}"

        self._record_action("notify_evidence_review", task["tool_name"], task["agent_id"], text)
        if webhook and _urlrequest is not None:
            payload = json.dumps({"text": text}).encode("utf-8")
            req = _urlrequest.Request(webhook, data=payload, headers={"Content-Type": "application/json"})
            try:
                resp = _urlrequest.urlopen(req, timeout=5)
                self._record_action("notify_evidence_result", task["tool_name"], task["agent_id"], f"Slack response: {getattr(resp, 'status', 'ok')}")
            except Exception as e:
                self._record_action("notify_evidence_error", task["tool_name"], task["agent_id"], f"Slack evidence notify failed: {e}")
    
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
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all real-world tasks (in any status)."""
        return [t.copy() for t in self._real_world_tasks]