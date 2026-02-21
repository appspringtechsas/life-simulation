"""Example: Basic life simulation run."""
from src.simulation import Simulator
from src.agents import Agent
import json


def example_basic_simulation():
    """Run a basic life simulation with default settings."""
    print("Starting basic life simulation example...")
    
    # Create simulator
    simulator = Simulator(max_turns=30, max_agents=20)
    
    # Run simulation
    report = simulator.run_simulation(initial_agents=3, verbose=True)
    
    # Print results
    print("\n--- Simulation Results ---")
    print(f"Total turns completed: {report['total_turns']}")
    print(f"Agents alive at end: {report['agents_alive']}")
    print(f"Total agents created: {report['total_agents_created']}")
    print(f"Birth events: {report['events']['births']}")
    print(f"Death events: {report['events']['deaths']}")
    print(f"Reproduction events: {report['events']['reproductions']}")
    print(f"Tool creation events: {report['events']['tool_creations']}")
    
    return simulator


def example_custom_configuration():
    """Run simulation with custom configuration."""
    print("\nStarting custom configuration example...")
    
    # Create custom simulator
    simulator = Simulator(max_turns=20, max_agents=50)
    
    # Increase environmental hazards
    simulator.environment.hazard_level = 10.0
    simulator.environment.resource_growth_rate = 5.0
    
    # Add custom initial agents
    for i in range(10):
        agent = Agent(name=f"Custom-Agent-{i}")
        agent.energy = 120.0
        agent.health = 100.0
        agent.resources = 75.0
        simulator.add_agent(agent)
    
    # Run simulation
    report = simulator.run_simulation(initial_agents=0, verbose=False)
    
    print(f"\nCustom simulation completed: {report['total_turns']} turns")
    print(f"Final population: {report['agents_alive']} agents")
    
    return simulator


def example_agent_interaction():
    """Demonstrate agent-to-agent interactions."""
    print("\nStarting agent interaction example...")
    
    simulator = Simulator(max_turns=15, max_agents=10)
    
    # Create parent agent
    parent = Agent(name="Parent-Alpha")
    parent.energy = 150.0
    parent.health = 100.0
    parent.resources = 100.0
    simulator.add_agent(parent)
    
    # Create child through reproduction
    if parent.can_reproduce():
        child = parent.reproduce()
        simulator.add_agent(child)
        print(f"Parent '{parent.name}' reproduced, created '{child.name}'")
    
    # Simulate a few turns
    for turn in range(5):
        simulator.current_turn = turn
        simulator.environment.turn = turn
        simulator.environment.update()
        
        # Parent helps child
        if parent.is_alive() and child.is_alive():
            if parent.spend_resources(10):
                child.gain_resources(10)
                print(f"Turn {turn}: Parent helped child with resources")
    
    print(f"\nAgent interaction example completed")
    print(f"Parent final state - Energy: {parent.energy:.1f}, Health: {parent.health:.1f}, Resources: {parent.resources:.1f}")
    print(f"Child final state - Energy: {child.energy:.1f}, Health: {child.health:.1f}, Resources: {child.resources:.1f}")
    
    return simulator


def example_mcp_tools():
    """Demonstrate MCP tool system."""
    print("\nStarting MCP tools example...")
    
    simulator = Simulator(max_turns=10, max_agents=5)
    
    # List default tools
    print(f"\nAvailable MCP tools ({len(simulator.tool_registry.get_enabled_tools())} enabled):")
    for tool in simulator.tool_registry.get_enabled_tools():
        print(f"  - {tool.name}: {tool.description}")
    
    # Simulate tool creation
    from src.mcp import MCPTool
    custom_tool = MCPTool(
        name="advanced_analysis",
        description="Advanced data analysis tool",
        creator_id="test_agent"
    )
    
    if simulator.tool_registry.register_tool(custom_tool):
        print(f"\nSuccessfully created custom tool: {custom_tool.name}")
    
    # List tools after creation
    print(f"\nTools after creation ({len(simulator.tool_registry.get_enabled_tools())} enabled):")
    for tool in simulator.tool_registry.get_enabled_tools()[:5]:
        print(f"  - {tool.name}")
    
    return simulator


if __name__ == "__main__":
    print("="*60)
    print("LIFE SIMULATION - EXAMPLES")
    print("="*60)
    
    # Run examples
    simulator1 = example_basic_simulation()
    simulator2 = example_custom_configuration()
    simulator3 = example_agent_interaction()
    simulator4 = example_mcp_tools()
    
    print("\n" + "="*60)
    print("All examples completed successfully!")
    print("="*60)
