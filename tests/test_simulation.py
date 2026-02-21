"""Tests for life simulation components."""
import pytest
from src.agents import Agent, Traits
from src.environment import Environment
from src.mcp import MCPTool, ToolRegistry
from src.simulation import Simulator, EventLogger
from src.llm import parse_agent_response


class TestAgent:
    """Test Agent class."""
    
    def test_agent_creation(self):
        """Test creating an agent."""
        agent = Agent(name="Test Agent")
        assert agent.name == "Test Agent"
        assert agent.energy == 100.0
        assert agent.health == 100.0
        assert agent.is_alive()
    
    def test_agent_energy_loss(self):
        """Test agent energy loss."""
        agent = Agent()
        agent.lose_energy(25)
        assert agent.energy == 75.0
    
    def test_agent_death(self):
        """Test agent death."""
        agent = Agent()
        agent.die(turn=5)
        assert not agent.is_alive()
        assert agent.status.value == "dead"
        assert agent.death_turn == 5
    
    def test_agent_reproduction(self):
        """Test agent reproduction."""
        agent = Agent()
        agent.energy = 100.0
        agent.health = 100.0
        agent.resources = 100.0
        
        assert agent.can_reproduce()
        offspring = agent.reproduce()
        assert offspring is not None
        assert offspring.generation == agent.generation + 1
        assert agent.id in offspring.parent_ids


class TestTraits:
    """Test Traits class."""
    
    def test_traits_mutation(self):
        """Test trait mutation."""
        traits = Traits()
        mutated = traits.mutate(mutation_rate=1.0)  # Guarantee mutation
        
        # At least one trait should be different
        assert traits.to_dict() != mutated.to_dict()
    
    def test_traits_bounds(self):
        """Test that mutations stay within bounds."""
        traits = Traits()
        for _ in range(100):
            mutated = traits.mutate(mutation_rate=1.0)
            for value in mutated.to_dict().values():
                assert 0.1 <= value <= 2.0


class TestEnvironment:
    """Test Environment class."""
    
    def test_environment_creation(self):
        """Test creating an environment."""
        env = Environment()
        assert env.turn == 0
        assert env.resources_available == 500.0
    
    def test_environment_update(self):
        """Test environment update."""
        env = Environment()
        initial = env.resources_available
        env.update()
        assert env.turn == 1
        assert env.resources_available >= initial  # Capped at max_resources
    
    def test_request_resources(self):
        """Test requesting resources from environment."""
        env = Environment()
        initial = env.resources_available
        obtained = env.request_resources("agent1", 100)
        assert obtained == 100.0
        assert env.resources_available == initial - 100


class TestMCPTools:
    """Test MCP Tools."""
    
    def test_tool_creation(self):
        """Test creating a tool."""
        tool = MCPTool(
            name="test_tool",
            description="A test tool"
        )
        assert tool.name == "test_tool"
        assert tool.enabled is True
    
    def test_tool_registry(self):
        """Test tool registry."""
        registry = ToolRegistry()
        tools = registry.get_enabled_tools()
        assert len(tools) > 0  # Should have default tools
    
    def test_register_custom_tool(self):
        """Test registering custom tool."""
        registry = ToolRegistry()
        tool = MCPTool(
            name="custom_tool",
            description="Custom tool",
            creator_id="agent1"
        )
        assert registry.register_tool(tool)
        assert registry.get_tool("custom_tool") is not None
    
    def test_disable_tool(self):
        """Test disabling a tool."""
        registry = ToolRegistry()
        registry.disable_tool("search_resources")
        assert not registry.get_tool("search_resources").enabled


class TestEventLogger:
    """Test Event Logger."""
    
    def test_log_event(self):
        """Test logging an event."""
        logger = EventLogger()
        logger.log_birth(0, "agent1", "Agent1", [])
        assert len(logger.events) == 1
        assert logger.events[0].event_type == "birth"
    
    def test_get_events_by_type(self):
        """Test getting events by type."""
        logger = EventLogger()
        logger.log_birth(0, "agent1", "Agent1", [])
        logger.log_death(1, "agent1", "Agent1", "starvation")
        
        births = logger.get_events_by_type("birth")
        deaths = logger.get_events_by_type("death")
        
        assert len(births) == 1
        assert len(deaths) == 1
    
    def test_event_summary(self):
        """Test event summary."""
        logger = EventLogger()
        logger.log_birth(0, "agent1", "Agent1", [])
        logger.log_reproduction(0, "agent1", "Agent1", "agent2", 30, 40)
        
        summary = logger.get_events_summary()
        assert summary["births"] == 1
        assert summary["reproductions"] == 1


class TestSimulator:
    """Test main Simulator."""
    
    def test_simulator_creation(self):
        """Test creating simulator."""
        sim = Simulator(max_turns=10)
        assert sim.max_turns == 10
        assert len(sim.agents) == 0
    
    def test_add_agent(self):
        """Test adding agent to simulator."""
        sim = Simulator()
        agent = Agent()
        sim.add_agent(agent)
        assert agent.id in sim.agents
    
    def test_get_living_agents(self):
        """Test getting living agents."""
        sim = Simulator()
        sim.add_agent()
        sim.add_agent()
        
        assert len(sim.get_living_agents()) == 2
    
    def test_simulation_run(self):
        """Test running a short simulation."""
        sim = Simulator(max_turns=5, max_agents=20)
        report = sim.run_simulation(initial_agents=2, verbose=False)
        
        assert report["total_turns"] == 4  # 0-4
        assert "agents_alive" in report
        assert "events" in report


class TestLLMResponseParsing:
    """Test LLM response parsing."""
    
    def test_parse_simple_response(self):
        """Test parsing a simple response."""
        response = """REASONING: I need resources
ACTIONS:
-> Search for resources
-> Rest
TOOLS_TO_USE: search_resources
NEW_TOOLS_TO_CREATE: none
"""
        parsed = parse_agent_response(response)
        assert "resources" in parsed["reasoning"].lower()
        assert len(parsed["actions"]) == 2
        assert "search_resources" in parsed["tools_to_use"]
    
    def test_parse_empty_response(self):
        """Test parsing empty components."""
        response = "REASONING: Thinking\nACTIONS:\nTOOLS_TO_USE: none\nNEW_TOOLS_TO_CREATE: none\n"
        parsed = parse_agent_response(response)
        assert len(parsed["actions"]) == 0
        assert len(parsed["tools_to_use"]) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
