"""Main entry point for life simulation."""
import sys
import json
from pathlib import Path

from src.simulation import Simulator
from src.mcp.slack_approval import SlackApprovalServer
from threading import Thread

def main():
    """Run life simulation with default configuration."""
    # Create simulator
    simulator = Simulator(max_turns=5, max_agents=1, logging_dir="logs")
        
    server = SlackApprovalServer(host='0.0.0.0', port=5000)
    
    # run the Flask app in a separate thread so simulator continues
    t = Thread(target=server.start, args=(simulator.tool_registry,), kwargs={'debug': False}, daemon=True)
    t.start()
    
    
    # Run simulation
    report = simulator.run_simulation(initial_agents=1)
    
    # Print final report
    report_str = json.dumps(report, indent=2)
    simulator.event_logger.log_info("\n" + "="*60)
    simulator.event_logger.log_info("SIMULATION FINAL REPORT")
    simulator.event_logger.log_info("="*60)
    simulator.event_logger.log_info(report_str)
    
    # Save state
    output_file = Path("data/simulation_state.json")
    output_file.parent.mkdir(exist_ok=True)
    simulator.save_state(str(output_file))
    simulator.event_logger.log_info(f"\nSimulation state saved to {output_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
