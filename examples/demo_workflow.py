"""Demo script showing complete real-world task workflow."""

from src.mcp import ToolRegistry


def main():
    """Demonstrate the complete workflow."""
    
    registry = ToolRegistry()
    
    print('=' * 60)
    print('REAL-WORLD TASK APPROVAL WORKFLOW DEMO')
    print('=' * 60)
    
    # Step 1: Create task
    print('\n1. Agent creates task (proposes work with cost)')
    task_id = registry.create_real_world_task(
        'search_resources',
        'agent-alice',
        {
            'proposed_cost': 40.0,
            'expected_outcome': 'Create marketing landing page at example.com/campaign',
            'description': 'Setting up Q1 marketing campaign'
        }
    )
    print(f'   Task created: {task_id}')
    print(f'   Status: pending_approval')
    print(f'   Proposed reward: 40 resources')
    
    # Step 2: Human approves
    print('\n2. Human reviews and APPROVES proposal')
    registry.approve_real_world_task(task_id)
    print(f'   Status: executing (agent can now do the work)')
    
    # Step 3: Agent does work
    print('\n3. Agent performs external real-world work')
    print(f'   [Agent creates webpage at example.com/campaign]')
    
    # Step 4: Agent submits evidence
    print('\n4. Agent submits deliverables/evidence')
    registry.submit_task_evidence(task_id, {
        'webpage_url': 'https://example.com/campaign',
        'response_time_ms': 245,
        'http_status': 200,
        'mobile_friendly': True,
        'screenshot_url': 's3://bucket/campaign.png'
    })
    print(f'   Status: awaiting_evidence_approval')
    print(f'   Evidence submitted for verification')
    
    # Step 5: Human approves evidence
    print('\n5. Human reviews and APPROVES evidence')
    registry.approve_task_evidence(task_id)
    print(f'   Status: approved')
    
    # Step 6: Simulator grants resources
    print('\n6. Simulator processes approved tasks (each turn)')
    approved = registry.get_and_clear_approved_tasks()
    for task in approved:
        agent_id = task["agent_id"]
        cost = task["proposed_cost"]
        print(f'   Agent {agent_id} receives {cost} resources!')
    
    print('\n' + '=' * 60)
    print('WORKFLOW COMPLETE')
    print('=' * 60)
    print(f'✓ Task proposed with cost: 40 resources')
    print(f'✓ Proposal approved by human')
    print(f'✓ Work completed by agent')
    print(f'✓ Evidence submitted and validated')
    print(f'✓ Reward granted to agent')


if __name__ == "__main__":
    main()
