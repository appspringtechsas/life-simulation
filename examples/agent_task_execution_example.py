"""Complete example: Agents executing real-world tasks.

This example shows the full workflow:
1. Agents propose tasks with costs
2. Humans approve proposals
3. Agents execute approved tasks
4. Agents submit evidence
5. Humans approve evidence
6. Agents receive resource rewards

Run this example:
    python examples/agent_task_execution_example.py
"""

import os
import sys
import time
from threading import Thread

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.simulation import Simulator
from src.agents import Agent
from src.agents.task_executor import AgentTaskWorker, TaskExecutor
from src.mcp.slack_approval import SlackApprovalServer


def execute_approved_tasks_example():
    """Demonstrate task execution workflow without simulator."""
    
    print("=" * 70)
    print("AGENT TASK EXECUTION EXAMPLE")
    print("=" * 70)
    
    # Create agent and task executor
    agent = Agent(name="Agent-Emma")
    worker = AgentTaskWorker(agent)
    
    print(f"\n1. Created agent: {agent.name} (ID: {agent.id[:8]})")
    
    # Simulate task data
    task_id = "task-abc123"
    task_data = {
        "id": task_id,
        "agent_id": agent.id,
        "proposed_cost": 40.0,
        "expected_outcome": "Create a marketing landing page at campaign.example.com",
        "status": "executing"
    }
    
    print(f"\n2. Approved task data:")
    print(f"   Task ID: {task_id}")
    print(f"   Expected: {task_data['expected_outcome']}")
    print(f"   Reward: {task_data['proposed_cost']} resources")
    
    # Start execution
    print(f"\n3. Agent begins work...")
    worker.start_task_execution(task_id, task_data)
    
    # Simulate work taking time
    time.sleep(1)
    
    # Complete execution and get evidence
    print(f"\n4. Agent completes work and generates evidence...")
    evidence = worker.complete_task_execution(task_id, None)
    
    if evidence:
        print(f"\n5. Evidence generated:")
        for key, value in evidence.items():
            if key not in ["html_preview", "sections"]:
                print(f"   {key}: {value}")
    
    print("\n" + "=" * 70)
    print("Task execution example complete!")
    print("=" * 70)


def execute_with_simulator():
    """Demonstrate task execution integrated with simulator and approvals."""
    
    print("\n" + "=" * 70)
    print("FULL WORKFLOW: Agents, Tasks, Approvals, and Execution")
    print("=" * 70)
    
    sim = Simulator(max_turns=5, max_agents=2)
    server = SlackApprovalServer(host='0.0.0.0', port=5000)
    
    # Start approval server
    t = Thread(target=server.start, args=(sim.tool_registry,), daemon=True)
    t.start()
    time.sleep(1)
    
    print("\n✓ Approval server started at http://localhost:5000")
    print("\nWorkflow:")
    print("  1. Agents use search_resources during simulation")
    print("  2. Tasks created as pending_approval")
    print("  3. Open http://localhost:5000 to approve proposals")
    print("  4. After approving, use execute_agents_tasks() to simulate work")
    print("  5. Return to http://localhost:5000 to approve evidence")
    print("  6. Resources granted to agents on next simulator turn")
    
    # Run simulation for a few turns
    print("\n" + "-" * 70)
    print("Running simulation (agents requesting tasks)...")
    print("-" * 70)
    
    initial_agents = 2
    for i in range(initial_agents):
        sim.add_agent()
    
    # Run a couple turns
    for turn in range(2):
        print(f"\nTurn {turn}:")
        sim.current_turn = turn
        sim.environment.turn = turn
        sim.environment.update()
        
        living = sim.get_living_agents().copy()
        for agent in living:
            sim.process_agent_turn(agent)
        
        # Check for pending tasks
        pending = sim.tool_registry.get_pending_real_world_tasks()
        if pending:
            print(f"\n  Pending tasks waiting for approval ({len(pending)}):")
            for p in pending:
                print(f"    - {p['id'][:8]}: {p['agent_id'][:8]} proposes {p['proposed_cost']} resources")
    
    print("\n" + "-" * 70)
    print("MANUAL STEP: Approve tasks at http://localhost:5000")
    print("-" * 70)
    
    # Prompt user to approve
    print("\nOpen http://localhost:5000 in browser and:")
    print("  1. Click 'Approve task' on pending proposals")
    print("  2. Return here after approving")
    print("\nPress Enter to continue (after approving tasks)...")
    input()
    
    # Execute approved tasks
    print("\n" + "-" * 70)
    print("Executing approved tasks and collecting evidence...")
    print("-" * 70)
    
    executing = sim.tool_registry.get_executing_real_world_tasks()
    executor = TaskExecutor()
    
    for task in executing:
        agent_id = task["agent_id"]
        task_id = task["id"]
        expected_outcome = task["expected_outcome"]
        
        print(f"\n  Executing: {agent_id[:8]} - {expected_outcome}")
        
        # Generate evidence
        evidence = executor.execute_task(
            task_id,
            expected_outcome,
            agent_id,
            f"Agent-{agent_id[:4]}"
        )
        
        if evidence:
            # Submit evidence
            ok = sim.tool_registry.submit_task_evidence(task_id, evidence)
            if ok:
                print(f"    ✓ Evidence submitted")
                print(f"    Evidence keys: {list(evidence.keys())[:5]}...")
    
    print("\n" + "-" * 70)
    print("MANUAL STEP: Approve evidence")
    print("-" * 70)
    
    awaiting = sim.tool_registry.get_awaiting_evidence_tasks()
    if awaiting:
        print(f"\nOpen http://localhost:5000 and approve {len(awaiting)} evidence submissions:")
        for a in awaiting:
            print(f"  - {a['id'][:8]}: {a['expected_outcome']}")
        
        print("\nPress Enter to continue (after approving evidence)...")
        input()
        
        # Run one more turn to grant resources
        print("\n" + "-" * 70)
        print("Granting resources from approved evidence...")
        print("-" * 70)
        
        approved = sim.tool_registry.get_and_clear_approved_tasks()
        for task in approved:
            agent_id = task["agent_id"]
            agent = sim.get_agent(agent_id)
            cost = task["proposed_cost"]
            
            if agent:
                old_resources = agent.resources
                agent.gain_resources(cost)
                print(f"  ✓ {agent.name}: {old_resources:.1f} → {agent.resources:.1f} resources")
    
    print("\n" + "=" * 70)
    print("Full workflow complete!")
    print("=" * 70)


def show_task_types():
    """Show all supported task types and example evidence."""
    
    print("\n" + "=" * 70)
    print("SUPPORTED TASK TYPES")
    print("=" * 70)
    
    executor = TaskExecutor()
    agent = Agent(name="TaskDemonstrator")
    
    task_types = [
        ("Webpage Creation", "Create a landing page at marketing.example.com"),
        ("Permission Email", "Send an email asking for data access permissions"),
        ("Document Creation", "Create a document with Q1 project requirements"),
        ("File Upload", "Upload files via FTP to backup.example.com"),
        ("Software Tool", "Create a Python tool for data processing"),
        ("API Endpoint", "Create a REST API endpoint for user management"),
        ("Marketing Campaign", "Setup an email marketing campaign"),
    ]
    
    for i, (name, outcome) in enumerate(task_types, 1):
        print(f"\n{i}. {name}")
        print(f"   Example: {outcome}")
        
        evidence = executor.execute_task(
            f"task-{i:03d}",
            outcome,
            agent.id,
            agent.name
        )
        
        if evidence:
            print(f"   Evidence keys:")
            for key in list(evidence.keys())[:5]:
                print(f"     - {key}")


def main():
    """Run examples."""
    
    print("\n" + "=" * 70)
    print("AGENT TASK EXECUTION - COMPLETE EXAMPLES")
    print("=" * 70)
    
    print("\nAvailable examples:")
    print("  1. Simple task execution (no simulator)")
    print("  2. Full workflow with simulator and manual approvals")
    print("  3. Show all supported task types")
    print("  4. Exit")
    
    choice = input("\nSelect example (1-4): ").strip()
    
    if choice == "1":
        execute_approved_tasks_example()
    elif choice == "2":
        execute_with_simulator()
    elif choice == "3":
        show_task_types()
    else:
        print("Exiting...")


if __name__ == "__main__":
    main()
