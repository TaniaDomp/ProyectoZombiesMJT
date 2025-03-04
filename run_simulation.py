from public.tools.simulator import Simulator
from public.student_code.solution import EvacuationPolicy
from public.visualization.single_run import visualize_simulation
import os
import matplotlib.pyplot as plt

def main():
    # Create simulator with policy name
    sim = Simulator(
        policy_name="EvacuationPolicy",
        n_nodes=30,
        seed=42
    )
    
    # Start an experiment for this run
    experiment_id = sim.data_manager.start_experiment({
        'type': 'single_run',
        'n_nodes': 30,
        'seed': 42
    })
    
    # Create student's policy
    policy = EvacuationPolicy()
    
    # Run simulation
    result, city, proxy_data = sim.run_simulation(policy)
    
    # Get the policy result again for visualization
    policy_result = policy.plan_evacuation(city, proxy_data, max_resources=10)
    
    # Create visualization directory
    vis_dir = os.path.join('data/policies/EvacuationPolicy/experiments', 
                          experiment_id, 'visualizations')
    os.makedirs(vis_dir, exist_ok=True)
    
    # Visualize and save results
    fig = visualize_simulation(city, proxy_data, policy_result, result)
    plt.savefig(os.path.join(vis_dir, 'city_simulation.png'))
    plt.close()
    
    # Print detailed results
    print("\nSimulation Results:")
    print(f"Success: {result.success}")
    if result.failure_reason:
        print(f"Failure Reason: {result.failure_reason}")
    print(f"Path Length: {result.path_length:.2f}")
    print(f"Time Taken: {result.time_taken:.2f}")
    print(f"Obstacles Encountered: {result.obstacles_encountered}")
    print("\nResource Usage:")
    for resource_type, usage in result.resources.to_dict()['efficiency'].items():
        print(f"{resource_type.replace('_', ' ').title()}: {usage*100:.1f}% efficient")
    
    print(f"\nVisualization saved to: {vis_dir}/city_simulation.png")

if __name__ == "__main__":
    main() 