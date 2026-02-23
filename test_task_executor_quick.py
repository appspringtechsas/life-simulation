#!/usr/bin/env python
"""Quick test of task executor."""

from src.agents import Agent
from src.agents.task_executor import TaskExecutor

# Create agent and executor
agent = Agent(name='TestAgent')
executor = TaskExecutor()

# Test multiple task types
tasks = [
    ('Create a marketing webpage at example.com', 'webpage'),
    ('Send an email requesting database permissions', 'email'),
    ('Create project documentation', 'document'),
]

print('Testing Task Execution with Agent:', agent.name)
print('=' * 60)

for outcome, task_type in tasks:
    evidence = executor.execute_task('test-id', outcome, agent.id, agent.name)
    print(f'\n{task_type.upper()}:')
    print(f'  Task: {outcome}')
    print(f'  Evidence keys: {list(evidence.keys())[:5]}...')
    print(f'  Task Type: {evidence.get("task_type")}')

print('\n' + '=' * 60)
print('✓ All task types executed successfully!')
