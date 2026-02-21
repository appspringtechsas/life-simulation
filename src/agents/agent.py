"""Agent class representing an autonomous entity in the simulation."""
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid
from datetime import datetime

from .traits import Traits


class AgentStatus(Enum):
    """Agent status enumeration."""
    ALIVE = "alive"
    DEAD = "dead"
    REPRODUCING = "reproducing"


@dataclass
class Agent:
    """Autonomous agent in the life simulation."""
    
    # Identity and genealogy
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    generation: int = 0
    parent_ids: List[str] = field(default_factory=list)
    children_ids: List[str] = field(default_factory=list)
    
    # State
    energy: float = 100.0
    health: float = 100.0
    resources: float = 50.0
    
    # Traits
    traits: Traits = field(default_factory=Traits)
    
    # Memory and knowledge
    memory: Dict[str, Any] = field(default_factory=dict)
    discovered_tools: List[str] = field(default_factory=list)
    
    # Metadata
    birth_turn: int = 0
    death_turn: Optional[int] = None
    status: AgentStatus = AgentStatus.ALIVE
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        """Initialize agent after creation."""
        if not self.name:
            self.name = f"Agent-{self.id[:8]}"
    
    def is_alive(self) -> bool:
        """Check if agent is alive."""
        return self.status == AgentStatus.ALIVE and self.energy > 0 and self.health > 0
    
    def can_reproduce(self) -> bool:
        """Check if agent can reproduce."""
        if not self.is_alive():
            return False
        # Require minimum energy and health, and enough resources
        min_energy = 60 / self.traits.reproduction_cost
        min_health = 60 / self.traits.health_resistance
        min_resources = 30 / self.traits.reproduction_cost
        return (
            self.energy >= min_energy and
            self.health >= min_health and
            self.resources >= min_resources
        )
    
    def gain_energy(self, amount: float):
        """Gain energy."""
        self.energy = min(200.0, self.energy + amount * self.traits.energy_efficiency)
    
    def lose_energy(self, amount: float):
        """Lose energy."""
        self.energy = max(0.0, self.energy - amount / self.traits.energy_efficiency)
    
    def take_damage(self, damage: float):
        """Take damage to health."""
        adjusted_damage = damage / self.traits.health_resistance
        self.health = max(0.0, self.health - adjusted_damage)
        if self.health <= 0:
            self.die()
    
    def gain_resources(self, amount: float):
        """Gain resources."""
        self.resources = min(500.0, self.resources + amount)
    
    def spend_resources(self, amount: float) -> bool:
        """Spend resources. Returns True if successful."""
        if self.resources >= amount:
            self.resources -= amount
            return True
        return False
    
    def reproduce(self) -> Optional["Agent"]:
        """Reproduce and create offspring. Returns None if cannot reproduce."""
        if not self.can_reproduce():
            return None
        
        cost = 40 * self.traits.reproduction_cost
        if not self.spend_resources(cost):
            return None
        
        # Lose energy from reproduction
        self.lose_energy(30 * self.traits.reproduction_cost)
        
        # Create offspring with mutated traits
        offspring = Agent(
            name=f"{self.name}-child",
            generation=self.generation + 1,
            parent_ids=[self.id],
            birth_turn=0,  # Will be set by simulation
            traits=self.traits.mutate(),
            energy=50.0,
            health=80.0,
            resources=20.0,
        )
        
        # Record offspring
        self.children_ids.append(offspring.id)
        
        return offspring
    
    def die(self, turn: Optional[int] = None):
        """Mark agent as dead."""
        self.status = AgentStatus.DEAD
        self.death_turn = turn
        self.energy = 0.0
    
    def to_state_dict(self) -> Dict[str, Any]:
        """Convert agent to state dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "generation": self.generation,
            "energy": round(self.energy, 2),
            "health": round(self.health, 2),
            "resources": round(self.resources, 2),
            "status": self.status.value,
            "parent_ids": self.parent_ids,
            "children_ids": self.children_ids,
            "birth_turn": self.birth_turn,
            "death_turn": self.death_turn,
            "traits": self.traits.to_dict(),
            "discovered_tools": self.discovered_tools,
            "memory": self.memory,
        }
    
    @staticmethod
    def from_state_dict(data: Dict[str, Any]) -> "Agent":
        """Reconstruct agent from state dictionary."""
        traits_data = data.pop("traits", {})
        traits = Traits(**traits_data) if traits_data else Traits()
        
        status_str = data.pop("status", "alive")
        status = AgentStatus(status_str)
        
        agent = Agent(
            **{k: v for k, v in data.items() if k in [
                "id", "name", "generation", "parent_ids", "children_ids",
                "energy", "health", "resources", "birth_turn", "death_turn",
                "discovered_tools", "memory", "created_at"
            ]},
            traits=traits,
            status=status,
        )
        return agent
