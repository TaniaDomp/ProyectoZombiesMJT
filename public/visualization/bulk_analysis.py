import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List
import os
import pandas as pd
from matplotlib.table import Table

def save_plot(plt, name: str, policy_name: str, experiment_id: str):
    """
    Save plot to the correct location in the data structure.
    
    Args:
        plt: matplotlib plot object
        name: name of the visualization
        policy_name: name of the policy being tested
        experiment_id: ID of the current experiment
    """
    # Construct the correct path following the data structure
    vis_path = os.path.join(
        "data/policies",
        policy_name,
        "experiments",
        experiment_id,
        "visualizations"
    )
    os.makedirs(vis_path, exist_ok=True)
    
    # Save the plot
    plt.savefig(os.path.join(vis_path, f"{name}.png"), 
                bbox_inches='tight', dpi=300)
    plt.close()

def plot_success_rates(core_metrics: Dict, policy_name: str, experiment_id: str):
    """Plot success rates by city size"""
    plt.figure(figsize=(10, 6))
    
    sizes = sorted(core_metrics['by_city_size'].keys())
    success_rates = [
        core_metrics['by_city_size'][size]['success_rate'] * 100 
        for size in sizes
    ]
    
    plt.bar(sizes, success_rates, alpha=0.7)
    plt.axhline(
        y=core_metrics['overall_performance']['success_rate'] * 100,
        color='r', linestyle='--',
        label=f'Overall: {core_metrics["overall_performance"]["success_rate"]*100:.1f}%'
    )
    
    plt.xlabel('City Size (Nodes)')
    plt.ylabel('Success Rate (%)')
    plt.title('Mission Success by City Size\nSuccess rate variation across different city sizes')
    plt.legend()
    
    save_plot(plt, "success_rates", policy_name, experiment_id)

def plot_resource_efficiency(resource_metrics: Dict, policy_name: str, experiment_id: str):
    """Plot resource allocation and usage patterns"""
    plt.figure(figsize=(12, 6))
    
    resource_types = list(resource_metrics['overall'].keys())
    x = range(len(resource_types))
    
    allocated = [metrics['avg_allocated'] for metrics in resource_metrics['overall'].values()]
    used = [metrics['avg_used'] for metrics in resource_metrics['overall'].values()]
    
    plt.bar(x, allocated, alpha=0.4, label='Allocated', color='lightblue')
    plt.bar(x, used, alpha=0.8, label='Used', color='blue')
    
    plt.xticks(x, [rt.replace('_', ' ').title() for rt in resource_types])
    plt.ylabel('Average Amount')
    plt.title('Resource Usage Analysis\nComparison of resource allocation vs actual usage')
    
    # Add efficiency percentages
    for i, (a, u) in enumerate(zip(allocated, used)):
        if a > 0:
            efficiency = (u / a) * 100
            plt.text(i, a, f'{efficiency:.1f}%\nefficient', 
                    ha='center', va='bottom')
    
    plt.legend()
    save_plot(plt, "resource_efficiency", policy_name, experiment_id)

def plot_environmental_impact(env_metrics: Dict, policy_name: str, experiment_id: str):
    """Plot environmental factors and their impact"""
    plt.figure(figsize=(15, 10))
    
    # Create correlation heatmap
    node_correlations = env_metrics['correlations']['nodes']
    edge_correlations = env_metrics['correlations']['edges']
    
    all_correlations = {
        **{f"Node: {k}": v for k, v in node_correlations.items()},
        **{f"Edge: {k}": v for k, v in edge_correlations.items()}
    }
    
    # Sort by absolute correlation value
    sorted_items = sorted(
        all_correlations.items(),
        key=lambda x: abs(x[1]),
        reverse=True
    )
    
    labels = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]
    
    plt.barh(range(len(values)), values)
    plt.yticks(range(len(labels)), labels)
    plt.xlabel('Correlation with Mission Success')
    plt.title('Environmental Impact Analysis\nCorrelation between environmental factors and mission success')
    
    # Add correlation values
    for i, v in enumerate(values):
        plt.text(v, i, f'{v:.2f}', va='center')
    
    save_plot(plt, "environmental_impact", policy_name, experiment_id)

def plot_performance_metrics(core_metrics: Dict, policy_name: str, experiment_id: str):
    """Plot overall performance metrics"""
    plt.figure(figsize=(12, 8))
    
    # Prepare data for the table
    performance = core_metrics['overall_performance']
    data = [
        ['Success Rate', f"{performance['success_rate']*100:.1f}%"],
        ['Average Time', f"{performance['avg_time']:.2f} units"],
        ['Average Path Length', f"{performance['avg_path_length']:.2f} units"],
        ['Resources Allocated', f"{performance['resources_allocated']:.1f} units"],
        ['Resources Used', f"{performance['resources_used']:.1f} units"],
        ['Resource Efficiency', f"{performance['resource_efficiency']*100:.1f}%"]
    ]
    
    # Add city size specific data
    for size, metrics in sorted(core_metrics['by_city_size'].items()):
        data.append([
            f'City Size {size}',
            f"{metrics['success_rate']*100:.1f}% success, "
            f"{metrics['avg_time']:.1f} time, "
            f"{metrics['resource_efficiency']*100:.1f}% resource eff."
        ])

    # Create table
    ax = plt.gca()
    ax.axis('off')
    table = Table(ax, bbox=[0.1, 0.1, 0.8, 0.8])
    
    # Add cells
    n_rows = len(data)
    width = 0.4
    height = 0.8 / n_rows
    
    for i, (metric, value) in enumerate(data):
        table.add_cell(i, 0, width, height, text=metric,
                      loc='left', facecolor='lightgray')
        table.add_cell(i, 1, width, height, text=value,
                      loc='right')
    
    ax.add_table(table)
    plt.title('Mission Performance Summary\nKey Performance Indicators', pad=20)
    
    save_plot(plt, "performance_metrics", policy_name, experiment_id)

def plot_resource_impact(resource_metrics: Dict, policy_name: str, experiment_id: str):
    """Plot resource impact on mission success"""
    plt.figure(figsize=(12, 6))
    
    # Extract data
    resource_types = list(resource_metrics['overall'].keys())
    efficiencies = [
        metrics['efficiency'] * 100 
        for metrics in resource_metrics['overall'].values()
    ]
    
    # Create bar chart
    x = range(len(resource_types))
    plt.bar(x, efficiencies, alpha=0.7)
    
    plt.xticks(x, [rt.replace('_', ' ').title() for rt in resource_types])
    plt.ylabel('Resource Efficiency (%)')
    plt.title('Resource Impact Analysis\nEfficiency of different resource types')
    
    # Add percentage labels
    for i, eff in enumerate(efficiencies):
        plt.text(i, eff, f'{eff:.1f}%', ha='center', va='bottom')
    
    # Add most used/needed resource annotations
    plt.figtext(
        0.02, 0.02,
        f"Most Used: {resource_metrics['analysis']['most_used_resource'].replace('_', ' ').title()}\n"
        f"Most Needed: {resource_metrics['analysis']['most_needed_resource'].replace('_', ' ').title()}",
        fontsize=8
    )
    
    save_plot(plt, "resource_impact", policy_name, experiment_id)

def plot_environmental_correlations(env_metrics: Dict, policy_name: str, experiment_id: str):
    """Plot correlations between environmental factors"""
    plt.figure(figsize=(15, 10))
    
    # Combine node and edge indicators
    indicators = {
        **{f"Node: {k}": v for k, v in env_metrics['overall']['nodes'].items()},
        **{f"Edge: {k}": v for k, v in env_metrics['overall']['edges'].items()}
    }
    
    # Create correlation matrix
    labels = list(indicators.keys())
    n = len(labels)
    correlation_matrix = np.zeros((n, n))
    
    def safe_correlation(x, y):
        """Safely compute correlation between two variables"""
        if len(x) < 2 or len(y) < 2:  # Need at least 2 points
            return 0.0
            
        # Check for zero variance
        if np.all(np.array(x) == x[0]) or np.all(np.array(y) == y[0]):
            return 0.0
            
        try:
            # Use np.nan_to_num to handle NaN values
            corr = np.corrcoef(x, y)[0, 1]
            return np.nan_to_num(corr, nan=0.0)
        except:
            return 0.0
    
    # Compute correlations with proper error handling
    for i, label1 in enumerate(labels):
        for j, label2 in enumerate(labels):
            if i == j:
                correlation_matrix[i, j] = 1.0
            else:
                # Get values, ensuring they're lists
                values1 = [indicators[label1]] if not isinstance(indicators[label1], list) else indicators[label1]
                values2 = [indicators[label2]] if not isinstance(indicators[label2], list) else indicators[label2]
                correlation_matrix[i, j] = safe_correlation(values1, values2)
    
    # Plot heatmap with a symmetric colormap centered at zero
    plt.imshow(correlation_matrix, cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)
    plt.colorbar(label='Correlation Coefficient')
    
    # Add labels
    plt.xticks(range(n), labels, rotation=45, ha='right')
    plt.yticks(range(n), labels)
    
    # Add correlation values to the cells
    for i in range(n):
        for j in range(n):
            color = 'black' if abs(correlation_matrix[i, j]) < 0.5 else 'white'
            plt.text(j, i, f'{correlation_matrix[i, j]:.2f}',
                    ha='center', va='center', color=color)
    
    plt.title('Environmental Factor Correlations\nRelationships between different environmental indicators')
    plt.tight_layout()
    
    save_plot(plt, "environmental_correlations", policy_name, experiment_id)

def plot_key_metrics_distribution(results: Dict, policy_name: str, experiment_id: str):
    """Plot distribution of key performance metrics"""
    plt.figure(figsize=(15, 10))
    
    # Extract raw data
    raw_data = results['raw_data']['runs']
    
    # Create subplots
    gs = plt.GridSpec(2, 3)
    
    # 1. Success Rate Pie Chart
    ax1 = plt.subplot(gs[0, 0])
    success_count = sum(1 for r in raw_data if r['success'])
    failure_count = len(raw_data) - success_count
    ax1.pie([success_count, failure_count], 
            labels=['Success', 'Failure'],
            autopct='%1.1f%%',
            colors=['lightgreen', 'lightcoral'])
    ax1.set_title('Mission Outcomes')
    
    # 2. Time Distribution
    ax2 = plt.subplot(gs[0, 1])
    times = [r['time_taken'] for r in raw_data]
    ax2.hist(times, bins=min(20, len(times)//2), alpha=0.7)
    ax2.axvline(np.mean(times), color='r', linestyle='--', 
                label=f'Mean: {np.mean(times):.2f}')
    ax2.set_title('Mission Time Distribution')
    ax2.set_xlabel('Time Units')
    ax2.legend()
    
    # 3. Resource Usage Comparison
    ax3 = plt.subplot(gs[0, 2])
    resource_types = list(raw_data[0]['resources']['allocated'].keys())
    x = np.arange(len(resource_types))
    width = 0.35
    
    allocated = [np.mean([r['resources']['allocated'][rt] for r in raw_data]) 
                for rt in resource_types]
    used = [np.mean([r['resources']['used'][rt] for r in raw_data]) 
            for rt in resource_types]
    
    ax3.bar(x - width/2, allocated, width, label='Allocated', alpha=0.7)
    ax3.bar(x + width/2, used, width, label='Used', alpha=0.7)
    ax3.set_xticks(x)
    ax3.set_xticklabels([rt.replace('_', ' ').title() for rt in resource_types])
    ax3.set_title('Resource Usage')
    ax3.legend()
    
    # 4. Success vs Resources Scatter
    ax4 = plt.subplot(gs[1, :2])
    success_allocated = [sum(r['resources']['allocated'].values()) for r in raw_data if r['success']]
    failure_allocated = [sum(r['resources']['allocated'].values()) for r in raw_data if not r['success']]
    success_used = [sum(r['resources']['used'].values()) for r in raw_data if r['success']]
    failure_used = [sum(r['resources']['used'].values()) for r in raw_data if not r['success']]
    
    ax4.scatter(success_allocated, success_used, c='green', label='Success', alpha=0.6)
    ax4.scatter(failure_allocated, failure_used, c='red', label='Failure', alpha=0.6)
    ax4.plot([0, max(success_allocated + failure_allocated)], 
             [0, max(success_allocated + failure_allocated)], 
             'k--', alpha=0.3, label='Perfect Efficiency')
    ax4.set_xlabel('Resources Allocated')
    ax4.set_ylabel('Resources Used')
    ax4.set_title('Resource Efficiency by Mission Outcome')
    ax4.legend()
    
    # 5. Resource Efficiency by City Size
    ax5 = plt.subplot(gs[1, 2])
    sizes = sorted(results['raw_data']['by_size'].keys())
    efficiencies = []
    
    for size in sizes:
        size_runs = results['raw_data']['by_size'][size]
        total_used = sum(sum(r['resources']['used'].values()) for r in size_runs)
        total_allocated = sum(sum(r['resources']['allocated'].values()) for r in size_runs)
        efficiency = total_used / total_allocated if total_allocated > 0 else 0
        efficiencies.append(efficiency * 100)
    
    ax5.plot(sizes, efficiencies, marker='o')
    ax5.set_xlabel('City Size')
    ax5.set_ylabel('Overall Resource Efficiency (%)')
    ax5.set_title('Resource Efficiency vs City Size')
    
    plt.tight_layout()
    save_plot(plt, "key_metrics", policy_name, experiment_id)

def generate_all_visualizations(results: Dict, policy_name: str, experiment_id: str):
    """Generate and save all visualization types with explanations"""
    print("\nGenerating Visualizations...")
    
    # Key Metrics Analysis
    print("\n1. Key Performance Metrics:")
    plot_key_metrics_distribution(results, policy_name, experiment_id)
    print("- Shows distribution of core performance indicators")
    print("- Visualizes relationships between key metrics")
    print("- Provides overview of mission outcomes")
    
    # Success Rate Analysis
    print("\n2. Success Rate Analysis:")
    plot_success_rates(results['core_metrics'], policy_name, experiment_id)
    print("- Shows how mission success varies with city size")
    print("- Helps identify optimal operational scale")
    print("- Highlights potential complexity thresholds")
    
    # Resource Efficiency
    print("\n3. Resource Efficiency Analysis:")
    plot_resource_efficiency(results['resource_metrics'], policy_name, experiment_id)
    print("- Compares resource allocation vs actual usage")
    print("- Identifies potential over/under-allocation")
    print("- Highlights resource utilization patterns")
    
    # Environmental Impact
    print("\n4. Environmental Impact Analysis:")
    plot_environmental_impact(results['environmental_metrics'], policy_name, experiment_id)
    print("- Shows how different factors affect mission outcomes")
    print("- Identifies key environmental indicators")
    print("- Helps in risk assessment and planning")
    
    # Performance Metrics
    print("\n5. Performance Metrics Summary:")
    plot_performance_metrics(results['core_metrics'], policy_name, experiment_id)
    print("- Provides overview of mission performance")
    print("- Shows success patterns across different scenarios")
    print("- Highlights areas for improvement")
    
    # Resource Impact
    print("\n6. Resource Impact Analysis:")
    plot_resource_impact(results['resource_metrics'], policy_name, experiment_id)
    print("- Shows effectiveness of different resources")
    print("- Helps optimize resource allocation")
    print("- Identifies critical resources")
    
    # Environmental Correlations
    print("\n7. Environmental Correlations:")
    plot_environmental_correlations(results['environmental_metrics'], policy_name, experiment_id)
    print("- Shows relationships between environmental factors")
    print("- Identifies key success predictors")
    print("- Helps in mission planning")
    
    vis_path = os.path.join("data/policies", policy_name, "experiments", experiment_id, "visualizations")
    print(f"\nAll visualizations have been saved to '{vis_path}/'")

def visualize_bulk_results(results: Dict):
    """
    Create comprehensive visualizations of bulk simulation results
    showing patterns and relationships between environmental indicators
    """
    plt.figure(figsize=(20, 15))
    
    # 1. Success Rate Analysis
    plt.subplot(3, 2, 1)
    sizes = sorted(results['by_size'].keys())
    success_rates = [results['by_size'][size]['success_rate'] * 100 for size in sizes]
    
    plt.bar(sizes, success_rates, alpha=0.7)
    plt.axhline(y=results['success_rate'] * 100, color='r', linestyle='--',
                label=f'Overall: {results["success_rate"]*100:.1f}%')
    plt.xlabel('City Size (Nodes)')
    plt.ylabel('Success Rate (%)')
    plt.title('Mission Success by City Size')
    plt.legend()
    
    # 2. Resource Efficiency Analysis
    plt.subplot(3, 2, 2)
    resource_types = list(results['resource_metrics'].keys())
    x = range(len(resource_types))
    
    carried = [metrics['avg_allocated'] for metrics in results['resource_metrics'].values()]
    remaining = [metrics['avg_remaining'] for metrics in results['resource_metrics'].values()]
    used = [c - r for c, r in zip(carried, remaining)]
    
    plt.bar(x, carried, alpha=0.4, label='Carried', color='lightblue')
    plt.bar(x, used, alpha=0.8, label='Used', color='blue')
    plt.xticks(x, [rt.replace('_', ' ').title() for rt in resource_types])
    plt.ylabel('Average Amount')
    plt.title('Resource Usage Patterns')
    plt.legend()
    
    # 3. Environmental Risk Patterns
    plt.subplot(3, 2, 3)
    risk_metrics = ['avg_structural_risk', 'avg_path_difficulty', 'avg_resource_demand']
    risk_data = {
        size: [results['by_size'][size]['proxy_metrics'][m] for m in risk_metrics]
        for size in sizes
    }
    
    x = np.arange(len(sizes))
    width = 0.25
    
    for i, metric in enumerate(risk_metrics):
        values = [risk_data[size][i] for size in sizes]
        plt.bar(x + i*width, values, width, alpha=0.7,
                label=metric.replace('avg_', '').replace('_', ' ').title())
    
    plt.xlabel('City Size (Nodes)')
    plt.ylabel('Risk Level')
    plt.title('Environmental Risk Patterns by City Size')
    plt.xticks(x + width, sizes)
    plt.legend()
    
    # 4. Time vs Distance Analysis
    plt.subplot(3, 2, 4)
    times = [results['by_size'][size]['avg_time'] for size in sizes]
    distances = [results['by_size'][size]['avg_path_length'] for size in sizes]
    success_sizes = [s for s, r in zip(sizes, success_rates) if r > 0]
    success_times = [t for t, r in zip(times, success_rates) if r > 0]
    success_distances = [d for d, r in zip(distances, success_rates) if r > 0]
    
    plt.scatter(success_distances, success_times, c=success_sizes, 
                cmap='viridis', s=100, alpha=0.6)
    plt.colorbar(label='City Size (Nodes)')
    plt.xlabel('Path Length')
    plt.ylabel('Time Taken')
    plt.title('Mission Time vs Path Length\n(Successful Missions)')
    
    # 5. Risk Correlation Analysis
    plt.subplot(3, 2, (5, 6))
    metrics = ['structural_risk', 'path_difficulty', 'resource_demand']
    n_metrics = len(metrics)
    correlation_matrix = np.zeros((n_metrics, n_metrics))
    
    # Calculate correlations between metrics
    for i, m1 in enumerate(metrics):
        for j, m2 in enumerate(metrics):
            values1 = [results['by_size'][size]['proxy_metrics'][f'avg_{m1}'] 
                      for size in sizes]
            values2 = [results['by_size'][size]['proxy_metrics'][f'avg_{m2}']
                      for size in sizes]
            correlation_matrix[i, j] = np.corrcoef(values1, values2)[0, 1]
    
    plt.imshow(correlation_matrix, cmap='RdYlBu', aspect='auto')
    plt.colorbar(label='Correlation')
    plt.xticks(range(n_metrics), [m.replace('_', ' ').title() for m in metrics])
    plt.yticks(range(n_metrics), [m.replace('_', ' ').title() for m in metrics])
    plt.title('Risk Metric Correlations')
    
    # Add correlation values
    for i in range(n_metrics):
        for j in range(n_metrics):
            plt.text(j, i, f'{correlation_matrix[i, j]:.2f}',
                    ha='center', va='center')
    
    plt.tight_layout()
    plt.show()

def visualize_pattern_analysis(results: Dict):
    """
    Analyze and visualize specific environmental patterns and their impact
    """
    plt.figure(figsize=(20, 10))
    
    # 1. Resource Demand vs Environmental Factors
    plt.subplot(2, 2, 1)
    sizes = sorted(results['by_size'].keys())
    
    structural = [results['by_size'][size]['proxy_metrics']['avg_structural_risk']
                 for size in sizes]
    resource_demand = [results['by_size'][size]['proxy_metrics']['avg_resource_demand']
                      for size in sizes]
    success_rates = [results['by_size'][size]['success_rate'] for size in sizes]
    
    plt.scatter(structural, resource_demand, c=success_rates, 
                s=100, alpha=0.6, cmap='RdYlBu')
    plt.colorbar(label='Success Rate')
    plt.xlabel('Structural Risk')
    plt.ylabel('Resource Demand')
    plt.title('Resource Demand vs Structural Risk')
    
    # 2. Path Difficulty Distribution
    plt.subplot(2, 2, 2)
    difficulties = [results['by_size'][size]['proxy_metrics']['avg_path_difficulty']
                   for size in sizes]
    
    plt.hist(difficulties, bins=10, alpha=0.7)
    plt.axvline(np.mean(difficulties), color='r', linestyle='--',
                label=f'Mean: {np.mean(difficulties):.2f}')
    plt.xlabel('Path Difficulty')
    plt.ylabel('Frequency')
    plt.title('Distribution of Path Difficulties')
    plt.legend()
    
    # 3. Success Rate vs Resource Allocation
    plt.subplot(2, 2, 3)
    resource_types = list(results['resource_metrics'].keys())
    allocation_ratios = []
    
    for rt in resource_types:
        metrics = results['resource_metrics'][rt]
        ratio = metrics['avg_remaining'] / metrics['avg_allocated']
        allocation_ratios.append(ratio)
    
    plt.bar(range(len(resource_types)), allocation_ratios, alpha=0.7)
    plt.xticks(range(len(resource_types)), 
               [rt.replace('_', ' ').title() for rt in resource_types])
    plt.ylabel('Remaining/Allocated Ratio')
    plt.title('Resource Allocation Efficiency')
    
    # 4. Risk Factor Analysis
    plt.subplot(2, 2, 4)
    metrics = ['structural_risk', 'path_difficulty', 'resource_demand']
    success_threshold = 0.7
    
    high_success = [size for size in sizes 
                   if results['by_size'][size]['success_rate'] >= success_threshold]
    low_success = [size for size in sizes 
                  if results['by_size'][size]['success_rate'] < success_threshold]
    
    def get_avg_metrics(size_group):
        return [
            np.mean([results['by_size'][size]['proxy_metrics'][f'avg_{m}']
                    for size in size_group])
            for m in metrics
        ]
    
    high_metrics = get_avg_metrics(high_success)
    low_metrics = get_avg_metrics(low_success)
    
    x = np.arange(len(metrics))
    width = 0.35
    
    plt.bar(x - width/2, high_metrics, width, label=f'Success ≥ {success_threshold*100}%',
            alpha=0.7)
    plt.bar(x + width/2, low_metrics, width, label=f'Success < {success_threshold*100}%',
            alpha=0.7)
    
    plt.xticks(x, [m.replace('_', ' ').title() for m in metrics])
    plt.ylabel('Average Risk Level')
    plt.title('Risk Factors: High vs Low Success Missions')
    plt.legend()
    
    plt.tight_layout()
    plt.show() 