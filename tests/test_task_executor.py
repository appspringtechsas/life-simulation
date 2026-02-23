"""Tests for task executor and agent task execution."""

import pytest
import json
from src.agents import Agent
from src.agents.task_executor import TaskExecutor, AgentTaskWorker


class TestTaskExecutor:
    """Test task execution and evidence generation."""
    
    @pytest.fixture
    def executor(self):
        """Create executor instance."""
        return TaskExecutor()
    
    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        return Agent(name="TestAgent")
    
    def test_execute_webpage_task(self, executor, agent):
        """Test webpage creation task execution."""
        task_id = "webpage-001"
        outcome = "Create a marketing landing page at campaign.example.com"
        
        evidence = executor.execute_task(task_id, outcome, agent.id, agent.name)
        
        assert evidence is not None
        assert isinstance(evidence, dict)
        assert "webpage_url" in evidence
        assert "http_status" in evidence
        assert "response_time_ms" in evidence
        assert "mobile_friendly" in evidence
        assert evidence["http_status"] in [200, 201]
        assert evidence["response_time_ms"] > 0
        assert "task_type" in evidence
        assert evidence["task_type"] == "webpage_creation"
    
    def test_execute_email_task(self, executor, agent):
        """Test permission email task execution."""
        task_id = "email-001"
        outcome = "Send an email requesting database access permissions"
        
        evidence = executor.execute_task(task_id, outcome, agent.id, agent.name)
        
        assert evidence is not None
        assert "recipient" in evidence
        assert "subject" in evidence
        assert "permission_granted" in evidence
        assert "response_time_hours" in evidence
        assert evidence["permission_granted"] in [True, False]
        assert "task_type" in evidence
        assert evidence["task_type"] == "permission_email"
    
    def test_execute_document_task(self, executor, agent):
        """Test document creation task execution."""
        task_id = "doc-001"
        outcome = "Create a document with project specifications"
        
        evidence = executor.execute_task(task_id, outcome, agent.id, agent.name)
        
        assert evidence is not None
        assert "document_url" in evidence
        assert "word_count" in evidence
        assert "sections" in evidence
        assert isinstance(evidence["sections"], list)
        assert len(evidence["sections"]) > 0
    
    def test_execute_upload_task(self, executor, agent):
        """Test file upload task execution."""
        task_id = "upload-001"
        outcome = "Upload project files to cloud storage"
        
        evidence = executor.execute_task(task_id, outcome, agent.id, agent.name)
        
        assert evidence is not None
        assert "files_uploaded" in evidence
        assert "total_size_mb" in evidence
        assert isinstance(evidence["files"], list)
        assert len(evidence["files"]) > 0
        assert all("filename" in f or "name" in f for f in evidence["files"])
        assert "task_type" in evidence
        assert evidence["task_type"] == "file_upload"
    
    def test_execute_software_task(self, executor, agent):
        """Test software tool creation task execution."""
        task_id = "software-001"
        outcome = "Create a Python tool for data processing"
        
        evidence = executor.execute_task(task_id, outcome, agent.id, agent.name)
        
        assert evidence is not None
        assert "repository_url" in evidence
        assert "lines_of_code" in evidence
        assert "test_coverage_percent" in evidence
        assert "deployment_status" in evidence
        assert evidence["deployment_status"] in ["live", "staging", "failed"]
        assert "task_type" in evidence
        assert evidence["task_type"] == "software_tool_creation"
    
    def test_execute_api_task(self, executor, agent):
        """Test API endpoint creation task execution."""
        task_id = "api-001"
        outcome = "Create a REST API endpoint for user management"
        
        evidence = executor.execute_task(task_id, outcome, agent.id, agent.name)
        
        assert evidence is not None
        assert "endpoint_path" in evidence
        assert "methods_supported" in evidence
        assert "rate_limit" in evidence
        assert "uptime_percent" in evidence
        assert isinstance(evidence["methods_supported"], list)
        assert len(evidence["methods_supported"]) > 0
        assert "task_type" in evidence
        assert evidence["task_type"] == "api_endpoint_creation"
    
    def test_execute_marketing_task(self, executor, agent):
        """Test marketing campaign setup task execution."""
        task_id = "marketing-001"
        outcome = "Setup and launch email marketing campaign"
        
        evidence = executor.execute_task(task_id, outcome, agent.id, agent.name)
        
        assert evidence is not None
        assert "channels" in evidence
        assert "impressions" in evidence
        assert "clicks" in evidence
        assert "roi_percent" in evidence
        assert isinstance(evidence["channels"], list)
        assert evidence["impressions"] > 0
        assert "task_type" in evidence
        assert evidence["task_type"] == "marketing_campaign"
    
    def test_execute_generic_task(self, executor, agent):
        """Test generic task with unrecognized outcome."""
        task_id = "generic-001"
        outcome = "Do some random work that doesn't match known patterns"
        
        evidence = executor.execute_task(task_id, outcome, agent.id, agent.name)
        
        assert evidence is not None
        assert "status" in evidence
        assert "quality_score" in evidence
        assert "time_invested_hours" in evidence
        assert evidence["status"] == "completed"
        assert 0 <= evidence["quality_score"] <= 1
        assert "task_type" in evidence
        assert evidence["task_type"] == "generic_task"
    
    def test_evidence_is_json_serializable(self, executor, agent):
        """Test that evidence can be serialized to JSON."""
        task_id = "json-001"
        outcome = "Create a marketing landing page"
        
        evidence = executor.execute_task(task_id, outcome, agent.id, agent.name)
        
        # Should not raise
        json_str = json.dumps(evidence)
        restored = json.loads(json_str)
        
        assert restored is not None
        assert len(restored) > 0
    
    def test_multiple_task_executions(self, executor, agent):
        """Test multiple task executions in sequence."""
        outcomes = [
            "Create a webpage",
            "Send an email",
            "Create a document",
            "Upload files"
        ]
        
        results = []
        for i, outcome in enumerate(outcomes):
            evidence = executor.execute_task(f"task-{i}", outcome, agent.id, agent.name)
            results.append(evidence)
        
        assert len(results) == len(outcomes)
        assert all(r is not None for r in results)


class TestAgentTaskWorker:
    """Test agent task worker lifecycle management."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        return Agent(name="WorkerAgent")
    
    @pytest.fixture
    def worker(self, agent):
        """Create worker instance."""
        return AgentTaskWorker(agent)
    
    def test_start_task_execution(self, worker):
        """Test starting task execution."""
        task_id = "task-start-001"
        task_data = {
            "id": task_id,
            "expected_outcome": "Create a webpage",
            "proposed_cost": 30.0
        }
        
        worker.start_task_execution(task_id, task_data)
        
        status = worker.get_task_status(task_id)
        assert status in ["started", "in_progress"]
    
    def test_complete_task_execution(self, worker):
        """Test completing task execution and getting evidence."""
        task_id = "task-complete-001"
        task_data = {
            "id": task_id,
            "expected_outcome": "Create a webpage",
            "agent_id": worker.agent.id,
            "proposed_cost": 30.0
        }
        
        worker.start_task_execution(task_id, task_data)
        evidence = worker.complete_task_execution(task_id, None)
        
        assert evidence is not None
        assert isinstance(evidence, dict)
        assert len(evidence) > 0
    
    def test_submit_evidence(self, worker):
        """Test submitting evidence directly without registry."""
        task_id = "task-evidence-001"
        task_data = {
            "id": task_id,
            "expected_outcome": "Create a webpage",
            "agent_id": worker.agent.id,
            "proposed_cost": 30.0
        }
        
        worker.start_task_execution(task_id, task_data)
        evidence = worker.complete_task_execution(task_id, None)
        
        # Verify evidence was generated
        assert evidence is not None
        assert isinstance(evidence, dict)
        assert len(evidence) > 0
    
    def test_get_task_status(self, worker):
        """Test getting task execution status."""
        task_id = "task-status-001"
        
        # Task not started
        status = worker.get_task_status(task_id)
        assert status is None or status == "not_started"
        
        # Start task
        task_data = {
            "id": task_id,
            "expected_outcome": "Create a webpage",
            "proposed_cost": 30.0
        }
        worker.start_task_execution(task_id, task_data)
        
        status = worker.get_task_status(task_id)
        assert status in ["started", "in_progress"]
    
    def test_multiple_concurrent_tasks(self, agent):
        """Test managing multiple concurrent tasks."""
        worker = AgentTaskWorker(agent)
        
        task_ids = ["task-concurrent-001", "task-concurrent-002", "task-concurrent-003"]
        
        # Start all tasks
        for task_id in task_ids:
            task_data = {
                "id": task_id,
                "expected_outcome": f"Task for {task_id}",
                "agent_id": agent.id,
                "proposed_cost": 30.0
            }
            worker.start_task_execution(task_id, task_data)
        
        # Complete all tasks
        evidence_list = []
        for task_id in task_ids:
            evidence = worker.complete_task_execution(task_id, None)
            assert evidence is not None
            evidence_list.append(evidence)
        
        # Verify all tasks are completed
        assert len(worker.executing_tasks) == len(task_ids)
        assert len(evidence_list) == len(task_ids)
    
    def test_task_worker_isolation(self):
        """Test that different workers don't share task data."""
        agent1 = Agent(name="Agent1")
        agent2 = Agent(name="Agent2")
        
        worker1 = AgentTaskWorker(agent1)
        worker2 = AgentTaskWorker(agent2)
        
        task_id = "task-isolation-001"
        
        # Start task in worker1
        task_data = {
            "id": task_id,
            "expected_outcome": "Create a webpage",
            "proposed_cost": 30.0
        }
        worker1.start_task_execution(task_id, task_data)
        
        # Worker2 should not know about it
        status1 = worker1.get_task_status(task_id)
        status2 = worker2.get_task_status(task_id)
        
        assert status1 is not None
        assert status2 is None
