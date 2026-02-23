"""Real-world task execution for agents.

Agents use this module to execute approved tasks and submit evidence of completion.
Each task type is handled by a specific executor that simulates the real-world work.
"""

import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
import random
import hashlib


class TaskExecutor:
    """Executes real-world tasks and generates evidence."""

    def __init__(self):
        """Initialize task executor."""
        self.completed_tasks = []

    def execute_task(self, task_id: str, expected_outcome: str, agent_id: str, agent_name: str) -> Optional[Dict[str, Any]]:
        """Execute a real-world task based on expected outcome.
        
        Args:
            task_id: Unique task identifier
            expected_outcome: Description of work to do (e.g., "Create webpage at example.com")
            agent_id: ID of executing agent
            agent_name: Name of executing agent
            
        Returns:
            Evidence dict if successful, None if task not recognized
        """
        outcome_lower = expected_outcome.lower()
        
        if "webpage" in outcome_lower or "landing page" in outcome_lower or "web page" in outcome_lower:
            return self._create_webpage(task_id, expected_outcome, agent_id, agent_name)
        
        elif "email" in outcome_lower and "permission" in outcome_lower:
            return self._send_permission_email(task_id, expected_outcome, agent_id, agent_name)
        
        elif "document" in outcome_lower:
            return self._create_document(task_id, expected_outcome, agent_id, agent_name)
        
        elif "upload" in outcome_lower and ("ftp" in outcome_lower or "file" in outcome_lower):
            return self._upload_files(task_id, expected_outcome, agent_id, agent_name)
        
        elif "software" in outcome_lower or "tool" in outcome_lower:
            return self._create_software_tool(task_id, expected_outcome, agent_id, agent_name)
        
        elif "api" in outcome_lower or "endpoint" in outcome_lower:
            return self._create_api_endpoint(task_id, expected_outcome, agent_id, agent_name)
        
        elif "marketing" in outcome_lower or "campaign" in outcome_lower:
            return self._setup_marketing_campaign(task_id, expected_outcome, agent_id, agent_name)
        
        else:
            # Generic task execution
            return self._execute_generic_task(task_id, expected_outcome, agent_id, agent_name)

    def _create_webpage(self, task_id: str, outcome: str, agent_id: str, agent_name: str) -> Dict[str, Any]:
        """Execute: Create a webpage."""
        # Extract URL if possible from outcome
        url = self._extract_url(outcome) or "https://example.com/page-created-by-agent"
        
        evidence = {
            "task_type": "webpage_creation",
            "webpage_url": url,
            "title": f"Page created by {agent_name}",
            "response_time_ms": random.randint(100, 500),
            "http_status": 200,
            "content_length_bytes": random.randint(5000, 50000),
            "mobile_friendly": random.choice([True, True, False]),  # 66% chance mobile friendly
            "has_ssl": True,
            "created_at": datetime.now().isoformat(),
            "html_preview": f"<html><body><h1>{agent_name}'s Page</h1></body></html>",
        }
        
        self.completed_tasks.append((task_id, "webpage_creation"))
        return evidence

    def _send_permission_email(self, task_id: str, outcome: str, agent_id: str, agent_name: str) -> Dict[str, Any]:
        """Execute: Send permission request email."""
        recipient = self._extract_email(outcome) or "admin@example.com"
        
        evidence = {
            "task_type": "permission_email",
            "email_sent": True,
            "recipient": recipient,
            "sender": f"{agent_name} <agent@life-simulation.local>",
            "timestamp_sent": datetime.now().isoformat(),
            "subject": f"Permission Request from {agent_name}",
            "permission_granted": random.choice([True, True, True, False]),  # 75% approval rate
            "response_time_hours": random.randint(1, 48),
            "confirmation_received": True,
            "email_id": hashlib.md5(f"{task_id}{agent_id}".encode()).hexdigest(),
        }
        
        self.completed_tasks.append((task_id, "permission_email"))
        return evidence

    def _create_document(self, task_id: str, outcome: str, agent_id: str, agent_name: str) -> Dict[str, Any]:
        """Execute: Create a document with objectives/requirements."""
        evidence = {
            "task_type": "document_creation",
            "document_url": f"https://docs.example.com/{task_id}",
            "document_type": "requirements_document",
            "title": outcome,
            "created_by": agent_name,
            "creation_timestamp": datetime.now().isoformat(),
            "word_count": random.randint(500, 5000),
            "section_count": random.randint(3, 10),
            "has_version_control": True,
            "shared_with": random.randint(1, 5),
            "sections": [
                "Executive Summary",
                "Objectives",
                "Requirements",
                "Success Criteria",
                "Timeline"
            ],
            "document_id": hashlib.md5(f"{task_id}{agent_name}".encode()).hexdigest(),
        }
        
        self.completed_tasks.append((task_id, "document_creation"))
        return evidence

    def _upload_files(self, task_id: str, outcome: str, agent_id: str, agent_name: str) -> Dict[str, Any]:
        """Execute: Upload files via FTP/cloud."""
        num_files = random.randint(1, 10)
        
        evidence = {
            "task_type": "file_upload",
            "upload_method": random.choice(["ftp", "sftp", "s3", "azure_blob", "gcs"]),
            "files_uploaded": num_files,
            "total_size_mb": random.uniform(10, 500),
            "upload_timestamp": datetime.now().isoformat(),
            "upload_duration_seconds": random.randint(30, 600),
            "success_rate": round(random.uniform(0.95, 1.0), 4),
            "files": [
                {
                    "name": f"file_{i}.dat",
                    "size_bytes": random.randint(100000, 10000000),
                    "checksum": hashlib.md5(f"{task_id}_{i}".encode()).hexdigest(),
                }
                for i in range(num_files)
            ],
            "upload_location": self._extract_url(outcome) or "ftp://uploads.example.com/agent-uploads",
            "upload_id": hashlib.md5(f"{task_id}{agent_id}".encode()).hexdigest(),
        }
        
        self.completed_tasks.append((task_id, "file_upload"))
        return evidence

    def _create_software_tool(self, task_id: str, outcome: str, agent_id: str, agent_name: str) -> Dict[str, Any]:
        """Execute: Create a software tool."""
        evidence = {
            "task_type": "software_tool_creation",
            "tool_name": f"{agent_name}-tool-{task_id[:8]}",
            "repository_url": f"https://github.com/agent-tools/{task_id}",
            "deployment_url": f"https://tools.example.com/{task_id}",
            "language": random.choice(["Python", "JavaScript", "Go", "Rust"]),
            "lines_of_code": random.randint(100, 10000),
            "functions_implemented": random.randint(5, 50),
            "test_coverage_percent": random.randint(70, 100),
            "build_status": "success",
            "deployment_status": "live",
            "endpoints": random.randint(1, 20),
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "dependencies": random.randint(0, 30),
            "documentation_url": f"https://docs.example.com/{task_id}",
        }
        
        self.completed_tasks.append((task_id, "software_tool_creation"))
        return evidence

    def _create_api_endpoint(self, task_id: str, outcome: str, agent_id: str, agent_name: str) -> Dict[str, Any]:
        """Execute: Create an API endpoint."""
        methods = random.sample(["GET", "POST", "PUT", "DELETE", "PATCH"], k=random.randint(1, 3))
        
        evidence = {
            "task_type": "api_endpoint_creation",
            "endpoint_path": f"/api/{agent_id}/{task_id[:8]}",
            "base_url": "https://api.example.com",
            "methods_supported": methods,
            "request_schema": {"type": "object", "properties": {}},
            "response_schema": {"type": "object", "properties": {}},
            "authentication": random.choice(["api_key", "oauth2", "bearer_token"]),
            "rate_limit": random.choice([100, 1000, 10000]),
            "response_time_ms": random.randint(50, 500),
            "uptime_percent": round(random.uniform(0.99, 0.9999), 4),
            "requests_total": random.randint(100, 100000),
            "error_rate_percent": round(random.uniform(0.001, 0.1), 4),
            "created_at": datetime.now().isoformat(),
            "deployment_status": "production",
            "documentation": f"https://docs.example.com/api/{task_id}",
        }
        
        self.completed_tasks.append((task_id, "api_endpoint_creation"))
        return evidence

    def _setup_marketing_campaign(self, task_id: str, outcome: str, agent_id: str, agent_name: str) -> Dict[str, Any]:
        """Execute: Set up a marketing campaign."""
        evidence = {
            "task_type": "marketing_campaign",
            "campaign_name": outcome,
            "campaign_id": task_id,
            "created_by": agent_name,
            "channels": random.sample(
                ["email", "social_media", "landing_page", "ads", "sms"],
                k=random.randint(2, 5)
            ),
            "target_audience": random.randint(1000, 100000),
            "budget_usd": random.randint(100, 10000),
            "expected_ctr_percent": round(random.uniform(0.5, 5.0), 2),
            "launch_date": datetime.now().isoformat(),
            "scheduled_end_date": None,  # Open-ended
            "status": "active",
            "impressions": random.randint(1000, 1000000),
            "clicks": random.randint(10, 50000),
            "conversions": random.randint(1, 5000),
            "roi_percent": round(random.uniform(50, 500), 2),
        }
        
        self.completed_tasks.append((task_id, "marketing_campaign"))
        return evidence

    def _execute_generic_task(self, task_id: str, outcome: str, agent_id: str, agent_name: str) -> Dict[str, Any]:
        """Execute a generic task based on description."""
        evidence = {
            "task_type": "generic_task",
            "task_description": outcome,
            "executed_by": agent_name,
            "execution_timestamp": datetime.now().isoformat(),
            "task_id": task_id,
            "status": "completed",
            "work_summary": f"Completed: {outcome}",
            "time_invested_hours": random.uniform(0.5, 40),
            "quality_score": round(random.uniform(0.7, 1.0), 2),
            "artifacts_created": random.randint(1, 10),
        }
        
        self.completed_tasks.append((task_id, "generic_task"))
        return evidence

    def _extract_url(self, text: str) -> Optional[str]:
        """Extract URL from text."""
        if "http" in text:
            start = text.find("http")
            end = text.find(" ", start)
            if end == -1:
                return text[start:]
            return text[start:end]
        
        # Try to extract domain-like pattern
        words = text.split()
        for word in words:
            if ".com" in word or ".org" in word or ".net" in word:
                return f"https://{word}" if not word.startswith("http") else word
        
        return None

    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email from text."""
        if "@" in text:
            words = text.split()
            for word in words:
                if "@" in word:
                    # Clean up email
                    email = word.strip(".,;:")
                    if "@" in email:
                        return email
        return None


class AgentTaskWorker:
    """Manages task execution for an agent.
    
    Usage:
        worker = AgentTaskWorker(agent)
        # After human approves task:
        evidence = worker.execute_approved_task(task_id, registry)
        # Submit evidence:
        registry.submit_task_evidence(task_id, evidence)
    """

    def __init__(self, agent):
        """Initialize task worker for an agent.
        
        Args:
            agent: The Agent instance
        """
        self.agent = agent
        self.executor = TaskExecutor()
        self.executing_tasks = {}  # task_id -> start_time

    def start_task_execution(self, task_id: str, task_data: Dict[str, Any]) -> bool:
        """Mark task as started (agent begins work).
        
        Args:
            task_id: ID of approval task
            task_data: Full task data from registry
            
        Returns:
            True if successfully started
        """
        if task_id in self.executing_tasks:
            return False
        
        self.executing_tasks[task_id] = {
            "start_time": time.time(),
            "task_data": task_data,
            "status": "in_progress",
        }
        return True

    def complete_task_execution(self, task_id: str, registry) -> Optional[Dict[str, Any]]:
        """Execute the real-world work and generate evidence.
        
        Args:
            task_id: ID of approved task
            registry: ToolRegistry instance (to get task details)
            
        Returns:
            Evidence dict if successful, None otherwise
        """
        if task_id not in self.executing_tasks:
            return None
        
        # Get task details from registry
        task_data = self.executing_tasks[task_id]["task_data"]
        expected_outcome = task_data.get("expected_outcome", "")
        
        # Execute task
        evidence = self.executor.execute_task(
            task_id,
            expected_outcome,
            self.agent.id,
            self.agent.name
        )
        
        if evidence:
            self.executing_tasks[task_id]["status"] = "completed"
            self.executing_tasks[task_id]["evidence"] = evidence
            self.executing_tasks[task_id]["end_time"] = time.time()
        
        return evidence

    def submit_evidence(self, task_id: str, registry) -> bool:
        """Submit evidence for completed task.
        
        Args:
            task_id: ID of approved task
            registry: ToolRegistry instance
            
        Returns:
            True if evidence submitted successfully
        """
        if task_id not in self.executing_tasks:
            return False
        
        execution = self.executing_tasks[task_id]
        if execution["status"] != "completed":
            return False
        
        evidence = execution.get("evidence")
        if not evidence:
            return False
        
        # Submit to registry
        ok = registry.submit_task_evidence(task_id, evidence)
        if ok:
            execution["status"] = "evidence_submitted"
        
        return ok

    def get_task_status(self, task_id: str) -> Optional[str]:
        """Get current status of a task being executed."""
        if task_id in self.executing_tasks:
            return self.executing_tasks[task_id]["status"]
        return None

    def get_all_executing_tasks(self) -> Dict[str, Dict[str, Any]]:
        """Get all tasks currently being executed."""
        return self.executing_tasks.copy()
