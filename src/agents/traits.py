"""Heritable traits for agents in the simulation."""
from dataclasses import dataclass, asdict
from typing import Dict, Any
import random


@dataclass
class Traits:
    """Represents heritable traits of an agent."""
    
    energy_efficiency: float = 1.0  # Energy consumption multiplier
    health_resistance: float = 1.0  # Health resistance to damage
    reproduction_cost: float = 1.0  # Cost multiplier for reproduction
    resource_affinity: float = 1.0  # Ability to find resources
    cooperation_tendency: float = 0.5  # Tendency to help others
    
    def mutate(self, mutation_rate: float = 0.1) -> "Traits":
        """Create mutated copy with random variations."""
        new_traits = asdict(self)
        for key in new_traits:
            if random.random() < mutation_rate:
                # Random mutation between -20% and +20%
                variation = random.uniform(0.8, 1.2)
                new_traits[key] *= variation
                # Keep values bounded
                new_traits[key] = max(0.1, min(2.0, new_traits[key]))
        
        return Traits(**new_traits)
    
    def to_dict(self) -> Dict[str, float]:
        """Convert traits to dictionary."""
        return asdict(self)
