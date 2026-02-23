"""Tests for real-world task approval workflow."""

import pytest
import time
from src.mcp import ToolRegistry, MCPTool


class TestRealWorldTasks:
    """Test suite for real-world task workflow."""

    def test_create_real_world_task(self):
        """Test creating a real-world task."""
        registry = ToolRegistry()
        
        task_id = registry.create_real_world_task(
            "search_resources",
            "agent-1",
            {
                "proposed_cost": 30.0,
                "expected_outcome": "Create a webpage to gather resources",
                "description": "Setting up landing page"
            }
        )
        
        assert task_id is not None
        assert len(task_id) > 0
        
        # Check task is in pending_approval
        pending = registry.get_pending_real_world_tasks()
        assert len(pending) == 1
        assert pending[0]["id"] == task_id
        assert pending[0]["status"] == "pending_approval"
        assert pending[0]["proposed_cost"] == 30.0

    def test_approve_real_world_task(self):
        """Test approving a task moves it to executing."""
        registry = ToolRegistry()
        
        task_id = registry.create_real_world_task(
            "search_resources",
            "agent-1",
            {
                "proposed_cost": 35.0,
                "expected_outcome": "Upload files via FTP",
            }
        )
        
        # Approve task
        ok = registry.approve_real_world_task(task_id)
        assert ok is True
        
        # Check task moved to executing
        pending = registry.get_pending_real_world_tasks()
        assert len(pending) == 0
        
        executing = registry.get_executing_real_world_tasks()
        assert len(executing) == 1
        assert executing[0]["status"] == "executing"

    def test_reject_real_world_task(self):
        """Test rejecting a task."""
        registry = ToolRegistry()
        
        task_id = registry.create_real_world_task(
            "search_resources",
            "agent-1",
            {
                "proposed_cost": 25.0,
                "expected_outcome": "Create document with requirements",
            }
        )
        
        # Reject task
        ok = registry.reject_real_world_task(task_id, "Insufficient details")
        assert ok is True
        
        # Check task is rejected
        pending = registry.get_pending_real_world_tasks()
        assert len(pending) == 0
        
        # Check in history
        history = registry.get_history()
        reject_entries = [h for h in history if h["action"] == "real_world_task_rejected"]
        assert len(reject_entries) > 0

    def test_submit_task_evidence(self):
        """Test agent submitting evidence after completion."""
        registry = ToolRegistry()
        
        task_id = registry.create_real_world_task(
            "search_resources",
            "agent-1",
            {
                "proposed_cost": 40.0,
                "expected_outcome": "Email permissions request and get approval",
            }
        )
        
        # Approve task
        registry.approve_real_world_task(task_id)
        
        # Submit evidence
        evidence = {
            "email_sent": True,
            "response_received": True,
            "permission_granted": True,
            "confirmation_screenshot": "data:image/png;base64,..."
        }
        ok = registry.submit_task_evidence(task_id, evidence)
        assert ok is True
        
        # Check task moved to awaiting_evidence_approval
        executing = registry.get_executing_real_world_tasks()
        assert len(executing) == 0
        
        awaiting = registry.get_awaiting_evidence_tasks()
        assert len(awaiting) == 1
        assert awaiting[0]["status"] == "awaiting_evidence_approval"
        assert awaiting[0]["deliverables"] == evidence

    def test_approve_task_evidence(self):
        """Test human approving submitted evidence."""
        registry = ToolRegistry()
        
        task_id = registry.create_real_world_task(
            "search_resources",
            "agent-1",
            {
                "proposed_cost": 45.0,
                "expected_outcome": "Create software tool",
            }
        )
        
        # Approve and submit
        registry.approve_real_world_task(task_id)
        registry.submit_task_evidence(task_id, {"tool_output": "success"})
        
        # Approve evidence
        ok = registry.approve_task_evidence(task_id)
        assert ok is True
        
        # Check task moved to approved
        awaiting = registry.get_awaiting_evidence_tasks()
        assert len(awaiting) == 0
        
        # Check can retrieve and clear
        approved = registry.get_and_clear_approved_tasks()
        assert len(approved) == 1
        assert approved[0]["status"] == "approved"
        assert approved[0]["proposed_cost"] == 45.0

    def test_reject_task_evidence(self):
        """Test human rejecting evidence, task returns to executing."""
        registry = ToolRegistry()
        
        task_id = registry.create_real_world_task(
            "search_resources",
            "agent-1",
            {
                "proposed_cost": 25.0,
                "expected_outcome": "Create webpage",
            }
        )
        
        # Approve and submit
        registry.approve_real_world_task(task_id)
        registry.submit_task_evidence(task_id, {"webpage_url": "example.com"})
        
        # Reject evidence
        ok = registry.reject_task_evidence(task_id, "Webpage does not meet requirements")
        assert ok is True
        
        # Check task back to executing
        awaiting = registry.get_awaiting_evidence_tasks()
        assert len(awaiting) == 0
        
        executing = registry.get_executing_real_world_tasks()
        assert len(executing) == 1

    def test_task_state_machine(self):
        """Test full workflow: pending → executing → evidence → approved."""
        registry = ToolRegistry()
        
        # Create task
        task_id = registry.create_real_world_task(
            "search_resources",
            "agent-1",
            {
                "proposed_cost": 50.0,
                "expected_outcome": "Complete real-world work",
            }
        )
        
        # Check pending
        assert len(registry.get_pending_real_world_tasks()) == 1
        assert len(registry.get_executing_real_world_tasks()) == 0
        
        # Step 1: Approve proposal
        registry.approve_real_world_task(task_id)
        assert len(registry.get_pending_real_world_tasks()) == 0
        assert len(registry.get_executing_real_world_tasks()) == 1
        
        # Step 2: Submit evidence
        registry.submit_task_evidence(task_id, {"completed": True})
        assert len(registry.get_executing_real_world_tasks()) == 0
        assert len(registry.get_awaiting_evidence_tasks()) == 1
        
        # Step 3: Approve evidence
        registry.approve_task_evidence(task_id)
        assert len(registry.get_awaiting_evidence_tasks()) == 0
        
        # Step 4: Retrieve approved
        approved = registry.get_and_clear_approved_tasks()
        assert len(approved) == 1
        assert approved[0]["proposed_cost"] == 50.0

    def test_multiple_tasks(self):
        """Test managing multiple tasks simultaneously."""
        registry = ToolRegistry()
        
        # Create multiple tasks
        task_ids = []
        for i in range(3):
            task_id = registry.create_real_world_task(
                "search_resources",
                f"agent-{i}",
                {
                    "proposed_cost": 30.0 + i*10,
                    "expected_outcome": f"Task {i} outcome",
                }
            )
            task_ids.append(task_id)
        
        # Check all pending
        pending = registry.get_pending_real_world_tasks()
        assert len(pending) == 3
        
        # Approve first two
        registry.approve_real_world_task(task_ids[0])
        registry.approve_real_world_task(task_ids[1])
        
        # Check states
        assert len(registry.get_pending_real_world_tasks()) == 1
        assert len(registry.get_executing_real_world_tasks()) == 2
        
        # Complete first task
        registry.submit_task_evidence(task_ids[0], {"done": True})
        registry.approve_task_evidence(task_ids[0])
        
        # Get approved (should be one)
        approved = registry.get_and_clear_approved_tasks()
        assert len(approved) == 1
        assert approved[0]["agent_id"] == "agent-0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
