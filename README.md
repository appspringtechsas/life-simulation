# Life Simulation - Autonomous Agents with LLM & MCP Tools

A complete artificial life simulation system where autonomous agents navigate a dynamic environment, using LLM-based decision-making and dynamically managed MCP (Model Context Protocol) tools.

## 🎯 Features

### Core Agent System
- **Autonomous Agents**: Each agent maintains internal state (energy, health, resources, memory)
- **Genealogy**: Track parent-child relationships across multiple generations
- **Heritable Traits**: Traitable characteristics that affect agent behavior and are passed to offspring with mutations
- **Multi-generation Support**: Agents can reproduce and create offspring with inherited/mutated traits
- **Family Cooperation**: Agents can help parents and offspring

### Agent States & Lifecycle
- **Energy**: Consumed through actions, decreased by metabolism, increased through resource gathering
- **Health**: Affected by environmental hazards, recoverable through resource expenditure
- **Resources**: Gathered from the environment, spent on actions and reproduction
- **Death Conditions**: Agents die when energy ≤ 0 or health ≤ 0

### Environment System
- **Dynamic Resource Management**: Limited resources that regenerate over time  
- **Environmental Hazards**: Random damage based on hazard level
- **Turn-Based Simulation**: Clear turn cycles for deterministic progression
- **Event Tracking**: Complete logging of all major events

### MCP Tools System
- **Default Tools**: Pre-built tools for resource gathering, health recovery, cooperation, etc.
- **Tool Discovery**: Agents can discover new tools from the environment
- **Custom Tool Creation**: Agents can define and create new tools
- **Tool Management**: Enable/disable/remove tools dynamically
- **Tool Execution Tracking**: Monitor tool usage and effectiveness
- **Real-World Task Approval**: Agents propose real-world work (with costs), humans approve/reject proposals, agents submit evidence, humans validate and grant resources

### Real-World Task Workflow
Agents can now request resources through a human-in-the-loop approval system:
- **Proposal Phase**: Agent proposes real-world work + proposed cost
- **Approval Phase**: Human reviews and approves or rejects proposal
- **Execution Phase**: Agent performs actual work (external process)
- **Evidence Phase**: Agent submits proof/deliverables of completion
- **Validation Phase**: Human reviews evidence and approves resource grant
- **Reward Phase**: Agent receives resources upon evidence approval

### LLM Integration
- **State-Based Prompts**: Agents receive complete state information
- **Custom Response Format**: Agents design their own action schemas
- **Decision Making**: Free-form reasoning and action selection
- **Tool Selection**: Agents choose which tools to use for their goals

### Gemini (Google) example

Set the API key and call a Gemini model by passing the model name to `get_response`:

```bash
# Linux / macOS
export GOOGLE_API_KEY=your_key_here
# PowerShell (Windows)
$env:GOOGLE_API_KEY='your_key_here'
```

```python
# use a Gemini model
response = llm_agent.get_response(agent, environment, model='gemini-1.0')
```

## 📁 Project Structure

```
life-simulation/
├── src/
│   ├── agents/              # Agent system
│   │   ├── __init__.py
│   │   ├── agent.py         # Agent class with lifecycle management
│   │   └── traits.py        # Heritable traits system
│   ├── environment/         # Environment simulation
│   │   ├── __init__.py
│   │   └── environment.py   # Environment/world state
│   ├── mcp/                 # MCP tools management
│   │   ├── __init__.py
│   │   └── mcp_tool.py      # Tool registry and management
│   ├── simulation/          # Main simulation engine
│   │   ├── __init__.py
│   │   ├── simulator.py     # Main simulator class
│   │   └── event_logger.py  # Event logging system
│   └── llm/                 # LLM integration
│       ├── __init__.py
│       └── llm_agent.py     # LLM agent handler and prompting
├── examples/                # Example scripts
│   ├── run_examples.py      # Multiple simulation examples
│   └── config_example.py    # Configuration example
├── tests/                   # Test suite
│   └── test_simulation.py   # Unit tests
├── data/                    # Output data directory
├── main.py                  # Main entry point
└── README.md               # This file
```

## 🚀 Installation & Setup

### Requirements
- Python 3.8+
- pytest (for running tests)

### Setup

1. **Clone the repository**:
```bash
git clone https://github.com/appspringtechsas/life-simulation.git
cd life-simulation
```

2. **Create virtual environment** (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -e .
```

## 📖 Quick Start

### Run Basic Simulation

```bash
python main.py
```

This will:
- Create 5 initial agents
- Run simulation for 50 turns
- Save state to `data/simulation_state.json`
- Save events to `data/events.json`

### Run Complete Automatic Workflow (RECOMMENDED) ⭐

**Terminal 1: Start the approval server**
```bash
python examples/run_with_approval_server.py
```

**Terminal 2: Run the simulation with automatic task execution**
```bash
python examples/automatic_task_workflow.py
```

**Browser: Approve tasks**
```
Open http://localhost:5000 and:
1. Approve pending proposals (1-2 per turn)
2. Approval evidence submissions automatically
3. Watch agents receive resources
```

This provides the complete workflow:
- Agents propose real-world work
- You approve proposals via web UI
- Simulator automatically executes tasks each turn ✨
- Evidence appears for review
- You approve evidence via web UI
- Agents receive resources automatically

For complete details, see [QUICK_FIX_GUIDE.md](QUICK_FIX_GUIDE.md).

### Run Simulation with Real-World Task Approval Server

```bash
python examples/run_with_approval_server.py
```

This will:
- Start a web approval server at http://localhost:5000
- Run simulation where agents request real-world work
- Provide a UI at http://localhost:5000 to approve/reject tasks and evidence
- Grant agents resources when human approves evidence

For full details, see [REAL_WORLD_TASKS.md](REAL_WORLD_TASKS.md) and [QUICK_START.md](QUICK_START.md).

### Run Agent Task Execution Examples

```bash
python examples/agent_task_execution_example.py
```

This demonstrates how agents execute real-world tasks and generate evidence:
- Simple task execution (no simulator)
- Full workflow with simulator and manual approvals
- Display of all supported task types

For detailed information, see [AGENT_TASK_EXECUTION.md](AGENT_TASK_EXECUTION.md).

### Run Examples

```bash
python examples/run_examples.py
```

This executes:
1. Basic simulation example
2. Custom configuration example
3. Agent interaction example
4. MCP tools example

### Run Configuration Example

```bash
python examples/config_example.py
```

This demonstrates:
- Creating custom agent traits
- Configuring environment parameters
- Creating diverse populations
- Running with specific settings

## 🧪 Testing

Run the test suite:

```bash
pytest tests/test_simulation.py -v
```

Run specific tests:

```bash
pytest tests/test_simulation.py::TestAgent -v
pytest tests/test_simulation.py::TestSimulator::test_simulation_run -v
```

## 🤖 Agent System Details

### Agent State
```python
Agent(
    id="uuid",
    name="Agent-name",
    generation=0,
    energy=100.0,
    health=100.0,
    resources=50.0,
    parent_ids=[],
    children_ids=[],
    traits=Traits(...),
    memory={},
    discovered_tools=[],
    status=AgentStatus.ALIVE
)
```

### Agent Actions
Agents can:
- **Search for resources**: Find resources from the environment
- **Recover health**: Spend resources to recover health
- **Reproduce**: Create offspring when energy, health, and resources are sufficient
- **Help offspring**: Transfer resources and health to children
- **Help parent**: Transfer resources to parent
- **Rest**: Gain energy
- **Discover tools**: Find new MCP tools
- **Create tools**: Design custom MCP tools

### Heritable Traits
Traits affect agent capabilities:
- `energy_efficiency`: Energy consumption/gain multiplier
- `health_resistance`: Damage reduction multiplier
- `reproduction_cost`: Cost multiplier for reproduction
- `resource_affinity`: Resource gathering ability
- `cooperation_tendency`: Willingness to help others (0-1)

Traits are mutated when passed to offspring with a 10% mutation rate by default.

## 🌍 Environment Details

### Environment Variables
- `resources_available`: Current resources in environment
- `max_resources`: Maximum possible resources
- `resource_growth_rate`: Resources regenerated per turn
- `temperature`: Environmental temperature (informational)
- `hazard_level`: Percentage chance of environmental damage per turn
- `fertility_rate`: Affects reproduction success
- `turn`: Current simulation turn

### Resource System
- Environment has limited but regenerating resources
- Agents request resources, environment provides what's available
- Requesting more than available returns partial amount
- Resources limit: 0-500 (default max)

## 🧰 MCP Tools System

### Default Tools
Available tools agents can use:
- `search_resources`: Find resources in environment
- `consume_energy`: Efficient energy usage
- `recover_health`: Use resources for health
- `help_offspring`: Assist children
- `help_parent`: Assist parents
- `explore_new_tools`: Discover novel tools
- `get_agent_state`: Query own state
- `get_environment_state`: Query environment

### Custom Tool Creation
Agents can create custom tools:
```python
from src.mcp import MCPTool

custom_tool = MCPTool(
    name="advanced_search",
    description="Enhanced resource detection",
    parameters={"intensity": {"type": "float"}},
    creator_id="agent_id"
)
tool_registry.register_tool(custom_tool)
```

### Tool Management
```python
# Get all tools
all_tools = tool_registry.get_all_tools()

# Get enabled tools only
enabled_tools = tool_registry.get_enabled_tools()

# Check tool
tool = tool_registry.get_tool("tool_name")

# Enable/Disable
tool_registry.enable_tool("tool_name")
tool_registry.disable_tool("tool_name")

# Remove
tool_registry.unregister_tool("tool_name")
```

## 📊 Event Logging

### Logged Events
- **birth**: Agent born (includes parent IDs)
- **death**: Agent died (includes cause: starvation, disease, etc.)
- **reproduction**: Successful reproduction (includes offspring ID)
- **resource_gain**: Resources gathered
- **tool_creation**: Custom tool created
- **action**: Generic actions performed

### Accessing Logs
```python
# Get logs from simulator
logger = simulator.event_logger

# Query events
births = logger.get_events_by_type("birth")
deaths = logger.get_events_by_type("death")
agent_events = logger.get_agent_events("agent_id")
turn_events = logger.get_events_by_turn(5)

# Get summary
summary = logger.get_events_summary()
# {"total_events": 42, "births": 10, "deaths": 3, ...}

# Export JSON
json_str = logger.to_json()
```

## 📝 Example Usage

### Basic Simulation
```python
from src.simulation import Simulator

# Create simulator
simulator = Simulator(max_turns=50, max_agents=30)

# Run simulation
report = simulator.run_simulation(initial_agents=5, verbose=True)

# Get results
print(f"Turns completed: {report['total_turns']}")
print(f"Agents alive: {report['agents_alive']}")
print(f"Birth events: {report['events']['births']}")
```

### Custom Configuration
```python
from src.simulation import Simulator
from src.agents import Agent, Traits

simulator = Simulator(max_turns=100, max_agents=50)

# Configure environment
simulator.environment.hazard_level = 10.0
simulator.environment.resource_growth_rate = 20.0

# Create custom agent
agent = Agent(name="CustomAgent")
agent.traits.cooperation_tendency = 0.8
agent.energy = 150.0
simulator.add_agent(agent)

# Run
report = simulator.run_simulation(initial_agents=0)
```

### Accessing Agent State
```python
agent = simulator.get_agent(agent_id)

# Check status
if agent.is_alive():
    print(f"Energy: {agent.energy:.1f}")
    print(f"Health: {agent.health:.1f}")
    print(f"Resources: {agent.resources:.1f}")

# Get genealogy
print(f"Parents: {agent.parent_ids}")
print(f"Children: {agent.children_ids}")

# Get state dictionary
state = agent.to_state_dict()
```

### Saving and Loading State
```python
# Save simulation state
simulator.save_state("checkpoint.json")

# Load simulation state
simulator.load_state("checkpoint.json")
```

## 🔄 Simulation Flow

```
Initialize Agents
    ↓
FOR each turn:
    1. Update environment (resource regeneration, time increment)
    2. FOR each living agent:
        a. Get agent state and environment state
        b. Generate prompt for LLM
        c. Parse agent response
        d. Execute actions (search, reproduce, help, etc.)
        e. Use selected tools
        f. Create new tools if proposed
        g. Apply metabolism costs
        h. Check for environmental hazards
        i. Determine if agent dies
        j. Log events
    3. Check termination conditions
    4. Display turn summary
    ↓
Generate final report and save state
```

## 📈 Simulation Reports

After simulation completes, reports include:

```json
{
  "total_turns": 50,
  "agents_alive": 12,
  "total_agents_created": 47,
  "events": {
    "total_events": 120,
    "births": 42,
    "deaths": 35,
    "reproductions": 28,
    "tool_creations": 5
  },
  "environment_state": {
    "turn": 50,
    "resources_available": 450.5,
    "hazard_level": 5.0
  },
  "tool_registry_size": 18,
  "simulation_status": "completed"
}
```

## 🔧 Customization

### Creating Custom Agent Types

```python
from src.agents import Agent, Traits

traits = Traits(
    energy_efficiency=0.8,
    health_resistance=1.2,
    reproduction_cost=0.9,
    resource_affinity=1.1,
    cooperation_tendency=0.7
)

agent = Agent(
    name="SpecialAgent",
    traits=traits,
    energy=120.0
)
```

### Custom Tool Implementation

```python
from src.mcp import MCPTool

tool = MCPTool(
    name="bio_synthesis",
    description="Convert resources into health",
    parameters={
        "resource_input": {"type": "float"},
        "efficiency": {"type": "float"}
    },
    creator_id="agent_id"
)
```

### Custom Simulation Configuration

```python
simulator = Simulator(max_turns=200, max_agents=100)

# Set environmental conditions
simulator.environment.hazard_level = 15.0
simulator.environment.resource_growth_rate = 25.0
simulator.environment.fertility_rate = 1.5

# Add initial population
for i in range(20):
    agent = Agent(name=f"Agent-{i}")
    simulator.add_agent(agent)

# Run
report = simulator.run_simulation(initial_agents=0)
```

## 📚 API Reference

### Core Classes

#### Agent
- `is_alive()`: Check if agent is alive
- `can_reproduce()`: Check if agent can reproduce
- `gain_energy(amount)`: Gain energy
- `lose_energy(amount)`: Lose energy
- `take_damage(damage)`: Take damage
- `gain_resources(amount)`: Gain resources
- `spend_resources(amount)`: Spend resources
- `reproduce()`: Create offspring
- `die(turn)`: Mark agent as dead
- `to_state_dict()`: Convert to dictionary

#### Environment
- `update()`: Update environment for new turn
- `request_resources(agent_id, amount)`: Get resources
- `get_hazard_damage()`: Get random hazard damage
- `to_state_dict()`: Convert to dictionary

#### Simulator
- `add_agent(agent, assign_birth_turn)`: Add agent
- `remove_agent(agent_id, cause)`: Remove dead agent
- `get_agent(agent_id)`: Get agent by ID
- `get_living_agents()`: Get all living agents
- `process_agent_turn(agent)`: Process one agent turn
- `run_simulation(initial_agents, verbose)`: Run complete simulation
- `save_state(filename)`: Save state to JSON
- `load_state(filename)`: Load state from JSON

#### ToolRegistry
- `register_tool(tool)`: Register new tool
- `unregister_tool(tool_name)`: Remove tool
- `enable_tool(tool_name)`: Enable tool
- `disable_tool(tool_name)`: Disable tool
- `get_tool(tool_name)`: Get tool by name
- `get_enabled_tools()`: Get all enabled tools
- `get_all_tools()`: Get all tools
- `execute_tool(tool_name)`: Execute tool

#### EventLogger
- `log_birth(turn, agent_id, name, parents)`: Log birth
- `log_death(turn, agent_id, name, cause)`: Log death
- `log_reproduction(turn, agent_id, name, offspring_id, energy, resources)`: Log reproduction
- `get_events_by_type(type)`: Query by event type
- `get_agent_events(agent_id)`: Query by agent
- `get_events_summary()`: Get statistics
- `to_json()`: Export as JSON

## 🛡️ Safety & Limitations

### Current Limitations
- LLM integration is simulated (uses deterministic logic instead of real LLM)
- Agent decision-making follows rule-based logic rather than actual model inference
- Reproduction costs are fixed rather than dynamic

### Future Enhancements
- Real LLM integration with selected API (OpenAI, Anthropic, etc.)
- Advanced decision-making algorithms
- Neural network-based trait inheritance
- Visualization dashboard for simulation monitoring
- Parallel agent processing for large populations
- Advanced tool composition and chaining

## 📄 License

This project is part of a technical assessment. See LICENSE for details.

## 👥 Contributing

For improvements or bug reports, please create an issue or pull request.

## 📧 Contact

For questions about this project, contact the development team.

---

**Status**: Issue #2 Resolution - Complete life simulation system with autonomous agents, LLM-based decision making, and dynamic MCP tools.
