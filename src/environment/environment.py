"""Environment system for the life simulation."""
from dataclasses import dataclass, field
from typing import Dict, Any, List
import random


@dataclass
class Environment:
    """Represents the environment in which agents live."""
    
    # Resource availability
    resources_available: float = 500.0
    max_resources: float = 500.0
    resource_growth_rate: float = 10.0  # Resources regenerated per turn
    
    # Environmental conditions
    temperature: float = 20.0  # Celsius
    hazard_level: float = 0.0  # 0-100, chance of damage
    fertility_rate: float = 1.0  # Affects reproduction success
    
    # History
    turn: int = 0
    events: List[str] = field(default_factory=list)
    resource_history: List[float] = field(default_factory=list)
    
    # Configuration
    max_agents: int = 100
    
    def update(self):
        """Update environment state for a new turn."""
        self.turn += 1
        
        # Resource regeneration
        self.resources_available = min(
            self.max_resources,
            self.resources_available + self.resource_growth_rate
        )
        
        # Track resource history
        self.resource_history.append(self.resources_available)
        
        # Environmental hazard damage calculation
        hazard_damage = random.random() * self.hazard_level
        if hazard_damage > 0:
            self.events.append(f"Turn {self.turn}: Environmental hazard level {self.hazard_level:.1f}% caused {hazard_damage:.2f} damage")
    
    def request_resources(self, agent_id: str, amount: float) -> float:
        """
        Agent requests resources from environment.
        Returns amount of resources obtained (may be less than requested).
        """
        available = min(amount, self.resources_available)
        self.resources_available -= available
        return available
    
    def get_hazard_damage(self) -> float:
        """Get random hazard damage based on current hazard level."""
        if random.random() < self.hazard_level / 100.0:
            return random.uniform(5, 20)
        return 0.0
    
    def to_state_dict(self) -> Dict[str, Any]:
        """Convert environment to state dictionary."""
        return {
            "turn": self.turn,
            "resources_available": round(self.resources_available, 2),
            "max_resources": self.max_resources,
            "resource_growth_rate": self.resource_growth_rate,
            "temperature": self.temperature,
            "hazard_level": round(self.hazard_level, 2),
            "fertility_rate": self.fertility_rate,
            "max_agents": self.max_agents,
            "events": self.events[-10:],  # Last 10 events
        }
    
    def add_event(self, event: str):
        """Add event to history."""
        self.events.append(f"Turn {self.turn}: {event}")
