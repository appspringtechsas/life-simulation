"""Configuration example for life simulation."""
from src.simulation import Simulator
from src.agents import Agent, Traits


def create_configured_simulation():
    """Create and configure a simulation with specific parameters."""
    
    # Create simulator with custom parameters
    simulator = Simulator(max_turns=100, max_agents=100)
    
    # Configure environment
    simulator.environment.resource_growth_rate = 15.0
    simulator.environment.max_resources = 1000.0
    simulator.environment.hazard_level = 5.0  # 5% chance of hazard per turn
    simulator.environment.fertility_rate = 1.0
    
    # Create agents with specific traits
    traits_aggressive = Traits(
        energy_efficiency=0.9,  # Uses less energy
        health_resistance=0.8,  # Takes more damage
        reproduction_cost=0.8,  # Cheaper reproduction
        resource_affinity=1.2,  # Better at finding resources
        cooperation_tendency=0.3,  # Less cooperative
    )
    
    traits_cooperative = Traits(
        energy_efficiency=1.1,  # Uses more energy
        health_resistance=1.2,  # Takes less damage
        reproduction_cost=1.0,
        resource_affinity=0.9,
        cooperation_tendency=0.8,  # More cooperative
    )
    
    traits_balanced = Traits(
        energy_efficiency=1.0,
        health_resistance=1.0,
        reproduction_cost=1.0,
        resource_affinity=1.0,
        cooperation_tendency=0.5,
    )
    
    # Create diverse population
    for i in range(3):
        agent = Agent(
            name=f"Aggressive-{i}",
            traits=traits_aggressive.mutate(mutation_rate=0.05)
        )
        agent.energy = 100.0
        simulator.add_agent(agent)
    
    for i in range(3):
        agent = Agent(
            name=f"Cooperative-{i}",
            traits=traits_cooperative.mutate(mutation_rate=0.05)
        )
        agent.energy = 100.0
        simulator.add_agent(agent)
    
    for i in range(3):
        agent = Agent(
            name=f"Balanced-{i}",
            traits=traits_balanced.mutate(mutation_rate=0.05)
        )
        agent.energy = 100.0
        simulator.add_agent(agent)
    
    return simulator


if __name__ == "__main__":
    print("Life Simulation Configuration Example")
    print("="*50)
    
    simulator = create_configured_simulation()
    
    print(f"Configured simulator with {len(simulator.agents)} initial agents")
    print(f"Environment settings:")
    print(f"  - Max agents: {simulator.environment.max_agents}")
    print(f"  - Resource growth rate: {simulator.environment.resource_growth_rate}")
    print(f"  - Hazard level: {simulator.environment.hazard_level}%")
    
    print(f"\nAgent population breakdown:")
    aggressive = [a for a in simulator.agents.values() if "Aggressive" in a.name]
    cooperative = [a for a in simulator.agents.values() if "Cooperative" in a.name]
    balanced = [a for a in simulator.agents.values() if "Balanced" in a.name]
    
    print(f"  - Aggressive agents: {len(aggressive)}")
    print(f"  - Cooperative agents: {len(cooperative)}")
    print(f"  - Balanced agents: {len(balanced)}")
    
    print("\nRunning configured simulation...")
    report = simulator.run_simulation(initial_agents=0, verbose=True)
    
    print(f"\nSimulation Results:")
    print(f"  - Total turns: {report['total_turns']}")
    print(f"  - Final population: {report['agents_alive']}")
    print(f"  - Total births: {report['events']['births']}")
    print(f"  - Total deaths: {report['events']['deaths']}")
