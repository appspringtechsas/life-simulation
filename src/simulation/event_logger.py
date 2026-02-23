"""Event logging system for the simulation."""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import os


@dataclass
class EventLog:
    """Represents a single event in the simulation."""
    
    turn: int
    timestamp: str
    event_type: str  # birth, death, reproduction, resource_gain, tool_creation, etc.
    agent_id: str
    agent_name: str
    details: Dict[str, Any]


class EventLogger:
    """Logger for simulation events."""
    
    def __init__(self, logging_dir: str = "logs"):
        """Initialize event logger."""
        self.events: List[EventLog] = []
        self.logging_dir = logging_dir
        if not os.path.exists(self.logging_dir):
            os.makedirs(self.logging_dir)

    def log_info(self, message: str):
        """Log an informational message to the console."""
        print(message)
        self.log_to_file(message)

    def log_to_file(self, message: str):
        """Append a message to the log file."""
        log_file = os.path.join(self.logging_dir, "simulation.log")
        with open(log_file, "a") as f:
            f.write(f"{datetime.now().isoformat()} - {message}\n")
    
    def log_event(self, 
                 turn: int,
                 agent_id: str,
                 agent_name: str,
                 event_type: str,
                 details: Dict[str, Any]) -> EventLog:
        """Log a simulation event."""
        event = EventLog(
            turn=turn,
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            agent_id=agent_id,
            agent_name=agent_name,
            details=details,
        )
        self.events.append(event)
        self.log_to_file(f"Event: {event_type} for agent {agent_name} ({agent_id}) at turn {turn}. Details: {details}")
        return event
    
    def log_birth(self, turn: int, agent_id: str, agent_name: str, parent_ids: List[str]):
        """Log agent birth."""
        self.log_event(turn, agent_id, agent_name, "birth", {
            "parent_ids": parent_ids,
        })
    
    def log_death(self, turn: int, agent_id: str, agent_name: str, cause: str):
        """Log agent death."""
        self.log_event(turn, agent_id, agent_name, "death", {
            "cause": cause,
        })
    
    def log_reproduction(self, turn: int, agent_id: str, agent_name: str, 
                        offspring_id: str, energy_spent: float, resources_spent: float):
        """Log reproduction event."""
        self.log_event(turn, agent_id, agent_name, "reproduction", {
            "offspring_id": offspring_id,
            "energy_spent": energy_spent,
            "resources_spent": resources_spent,
        })
    
    def log_resource_gain(self, turn: int, agent_id: str, agent_name: str, amount: float):
        """Log resource gathering."""
        self.log_event(turn, agent_id, agent_name, "resource_gain", {
            "amount": amount,
        })
    
    def log_tool_creation(self, turn: int, agent_id: str, agent_name: str, tool_name: str):
        """Log tool creation."""
        self.log_event(turn, agent_id, agent_name, "tool_creation", {
            "tool_name": tool_name,
        })
    
    def log_action(self, turn: int, agent_id: str, agent_name: str, action: str, details: Optional[Dict[str, Any]] = None):
        """Log a generic action."""
        self.log_event(turn, agent_id, agent_name, "action", {
            "action": action,
            **(details or {})
        })
    
    def get_events_by_type(self, event_type: str) -> List[EventLog]:
        """Get all events of a specific type."""
        return [e for e in self.events if e.event_type == event_type]
    
    def get_agent_events(self, agent_id: str) -> List[EventLog]:
        """Get all events for a specific agent."""
        return [e for e in self.events if e.agent_id == agent_id]
    
    def get_events_by_turn(self, turn: int) -> List[EventLog]:
        """Get all events from a specific turn."""
        return [e for e in self.events if e.turn == turn]
    
    def get_events_summary(self) -> Dict[str, Any]:
        """Get summary statistics of logged events."""
        births = len(self.get_events_by_type("birth"))
        deaths = len(self.get_events_by_type("death"))
        reproductions = len(self.get_events_by_type("reproduction"))
        tool_creations = len(self.get_events_by_type("tool_creation"))
        
        return {
            "total_events": len(self.events),
            "births": births,
            "deaths": deaths,
            "reproductions": reproductions,
            "tool_creations": tool_creations,
        }
    
    def to_json(self) -> str:
        """Convert logs to JSON string."""
        events_data = []
        for event in self.events:
            events_data.append({
                "turn": event.turn,
                "timestamp": event.timestamp,
                "event_type": event.event_type,
                "agent_id": event.agent_id,
                "agent_name": event.agent_name,
                "details": event.details,
            })
        return json.dumps(events_data, indent=2)
