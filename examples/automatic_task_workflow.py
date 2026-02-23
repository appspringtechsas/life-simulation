"""Automatic task execution workflow with approval server.

This example demonstrates the complete automatic workflow:
1. Simulator starts and agents create tasks  
2. User approves tasks via http://localhost:5000
3. Simulator automatically executes tasks and submits evidence
4. User approves evidence via http://localhost:5000
5. Agents receive resources automatically

Run with approval server in background:
    python run_with_approval_server.py

Then in another terminal:
    python examples/automatic_task_workflow.py
"""

import os
import sys
import time
from threading import Thread

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.simulation import Simulator
from src.agents.task_executor import TaskExecutor


def monitor_task_progress(sim):
    """Monitor and display task progress."""
    
    while True:
        pending = sim.tool_registry.get_pending_real_world_tasks()
        executing = sim.tool_registry.get_executing_real_world_tasks()
        awaiting = sim.tool_registry.get_awaiting_evidence_tasks()
        approved = sim.tool_registry.get_all_tasks()  # Get all tasks to see approved count
        
        approved_count = len([t for t in approved if t.get("status") == "approved"])
        
        print(f"\n[Turn {sim.current_turn}] Task Status:")
        print(f"  ⏳ Pending Approval: {len(pending)} | Executing: {len(executing)} | Awaiting Evidence: {len(awaiting)} | Approved: {approved_count}")
        
        if pending:
            print(f"    → Pending tasks (go to http://localhost:5000 to approve):")
            for p in pending[:3]:
                print(f"      {p['id'][:8]}: {p['expected_outcome'][:50]}...")
        
        if executing:
            print(f"    → Executing tasks (evidence being collected):")
            for e in executing[:2]:
                print(f"      {e['id'][:8]}: {e['expected_outcome'][:50]}...")
        
        if awaiting:
            print(f"    → Awaiting Evidence Review (go to http://localhost:5000 to approve):")
            for a in awaiting[:2]:
                print(f"      {a['id'][:8]}: {a['expected_outcome'][:50]}...")
        
        if approved_count > 0:
            print(f"    → ✅ {approved_count} tasks fully approved and rewarded!")
        
        time.sleep(3)


def run_automatic_workflow():
    """Run simulation with automatic task execution."""
    
    print("\n" + "=" * 70)
    print("AUTOMATIC TASK EXECUTION WORKFLOW")
    print("=" * 70)
    
    print("\nSetup:")
    print("  1. Approval server should be running at http://localhost:5000")
    print("  2. Simulator will automatically execute approved tasks")
    print("  3. You approve/reject tasks and evidence via the web UI")
    print("  4. Resources are granted automatically when evidence approved")
    
    print("\nWorkflow:")
    print("  → Agents propose work during simulation")
    print("  → You approve proposals at http://localhost:5000")
    print("  → Simulator executes work each turn")
    print("  → You approve evidence at http://localhost:5000")
    print("  → Agents receive resources automatically")
    
    # Create simulator
    sim = Simulator(max_turns=30, max_agents=10)
    
    print("\n" + "-" * 70)
    print("Starting simulation...")
    print("-" * 70)
    
    # Start monitoring task progress in background
    monitor_thread = Thread(target=monitor_task_progress, args=(sim,), daemon=True)
    monitor_thread.start()
    
    # Run simulation
    try:
        sim.run_simulation(initial_agents=3, verbose=False)
        
        print("\n" + "=" * 70)
        print("SIMULATION COMPLETE")
        print("=" * 70)
        
        # Print final stats
        print("\nFinal Statistics:")
        print(f"  Turns completed: {sim.current_turn}")
        print(f"  Living agents: {len(sim.get_living_agents())}")
        print(f"  Total tools: {len(sim.tool_registry.get_all_tools())}")
        print(f"  All tasks processed: {len(sim.tool_registry.get_all_tasks())}")
        
        # Show approved tasks
        all_tasks = sim.tool_registry.get_all_tasks()
        approved_tasks = [t for t in all_tasks if t.get("status") == "approved"]
        
        if approved_tasks:
            print(f"\n✅ Approved Tasks ({len(approved_tasks)}):")
            total_resources = sum(t.get("proposed_cost", 0) for t in approved_tasks)
            print(f"  Total resources granted: {total_resources:.0f}")
            print(f"  Tasks completed:")
            for task in approved_tasks[:5]:
                print(f"    - {task['expected_outcome'][:60]}... ({task.get('proposed_cost', 0):.0f} resources)")
        
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user")


if __name__ == "__main__":
    run_automatic_workflow()
