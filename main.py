"""Main entry point for life simulation."""
import sys
import json
from pathlib import Path

from src.simulation import Simulator


def main():
    """Run life simulation with default configuration."""
    print("\n" + "="*60)
    print("LIFE SIMULATION - AUTONOMOUS AGENTS WITH LLM & MCP TOOLS")
    print("="*60 + "\n")
    
    # Create simulator
    simulator = Simulator(max_turns=50, max_agents=30)
    
    # Run simulation
    report = simulator.run_simulation(initial_agents=5, verbose=True)
    
    # Print final report
    print("\n" + "="*60)
    print("SIMULATION FINAL REPORT")
    print("="*60)
    print(json.dumps(report, indent=2))
    
    # Save state
    output_file = Path("data/simulation_state.json")
    output_file.parent.mkdir(exist_ok=True)
    simulator.save_state(str(output_file))
    print(f"\nSimulation state saved to {output_file}")
    
    # Save events log
    events_file = Path("data/events.json")
    with open(events_file, 'w') as f:
        f.write(simulator.event_logger.to_json())
    print(f"Events log saved to {events_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
