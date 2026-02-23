"""Example: Run simulation with approval server for real-world task management.

This example shows how to:
1. Start the approval server in a background thread
2. Run the simulator
3. Test task creation, approval, evidence submission, and resource grants

To use with Slack:
  Set SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
  Set APPROVAL_BASE_URL=http://your-approval-server.com (or localhost:5000 for local)
  Set APPROVAL_TOKEN=secret-token (optional, for secure approval links)
"""

import os
import sys
import time
from threading import Thread

# Add parent to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.simulation import Simulator
from src.mcp.slack_approval import SlackApprovalServer


def main():
    """Run simulation with approval server."""
    
    # Optional: Set environment variables for Slack integration
    # os.environ["SLACK_WEBHOOK_URL"] = "https://hooks.slack.com/services/YOUR/URL"
    # os.environ["APPROVAL_BASE_URL"] = "http://localhost:5000"
    # os.environ["APPROVAL_TOKEN"] = "my-secret-token"
    
    print("Initializing simulator and approval server...")
    sim = Simulator(max_turns=20, max_agents=10)
    
    # Start approval server in background thread
    server = SlackApprovalServer(host='0.0.0.0', port=5000)
    server_thread = Thread(
        target=server.start, 
        args=(sim.tool_registry,), 
        kwargs={'debug': False},
        daemon=True
    )
    server_thread.start()
    
    print("\nApproval server started at http://localhost:5000")
    print("Open the URL in your browser to review and approve/reject tasks.\n")
    
    # Wait a moment for server to start
    time.sleep(1)
    
    # Run simulation
    print("Starting simulation...")
    report = sim.run_simulation(initial_agents=3, verbose=True)
    
    print("\n" + "="*60)
    print("SIMULATION REPORT")
    print("="*60)
    print(f"Total turns: {report['total_turns']}")
    print(f"Agents alive: {report['agents_alive']}")
    print(f"Total agents created: {report['total_agents_created']}")
    print(f"Tool registry size: {report['tool_registry_size']}")
    
    # Print pending tasks (if any)
    pending = sim.tool_registry.get_pending_real_world_tasks()
    if pending:
        print(f"\nStill pending ({len(pending)} tasks):")
        for t in pending:
            print(f"  - {t['id']}: {t['agent_id']} proposed cost={t['proposed_cost']}")
    
    # Print awaiting evidence (if any)
    awaiting = sim.tool_registry.get_awaiting_evidence_tasks()
    if awaiting:
        print(f"\nAwaiting evidence review ({len(awaiting)} tasks):")
        for t in awaiting:
            print(f"  - {t['id']}: {t['agent_id']}")


if __name__ == "__main__":
    main()
