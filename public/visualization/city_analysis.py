import matplotlib.pyplot as plt
import numpy as np
import os
import json
import pandas as pd
from typing import Dict, Tuple
import networkx as nx
import random

def save_city_plot(plt, name: str, policy_name: str, experiment_id: str, city_id: str):
    """Save plot to the correct city-specific location"""
    vis_path = os.path.join(
        "data/policies",
        policy_name,
        "experiments",
        experiment_id,
        "cities",
        f"city_{city_id}",
        "visualizations"
    )
    os.makedirs(vis_path, exist_ok=True)
    plt.savefig(os.path.join(vis_path, f"{name}.png"), bbox_inches='tight', dpi=300)
    plt.close()

def save_city_data(data: Dict, name: str, policy_name: str, experiment_id: str, city_id: str):
    """Save analysis data to the correct city-specific location"""
    data_path = os.path.join(
        "data/policies",
        policy_name,
        "experiments",
        experiment_id,
        "cities",
        f"city_{city_id}",
        "analysis"
    )
    os.makedirs(data_path, exist_ok=True)
    with open(os.path.join(data_path, f"{name}.json"), 'w') as f:
        json.dump(data, f, indent=4)

def plot_city_graph(city_data: Dict, proxy_data: Dict, mission_data: Dict, 
                  policy_name: str, experiment_id: str, city_id: str):
    """Plot the city layout with the evacuation story overlaid"""
    plt.figure(figsize=(15, 12))
    
    # Create graph from city data
    G = nx.Graph()
    
    # Add nodes and edges from definition
    for node in city_data['graph']['nodes']:
        G.add_node(node['id'], pos=(node['x'], node['y']))
    
    for edge in city_data['graph']['edges']:
        G.add_edge(edge['source'], edge['target'], weight=edge['weight'])
    
    # Get node positions
    pos = nx.get_node_attributes(G, 'pos')
    
    # Create figure with two subplots: main graph and event log
    gs = plt.GridSpec(1, 5)
    ax_main = plt.subplot(gs[0, :4])  # Main graph takes 4/5 of the width
    ax_log = plt.subplot(gs[0, 4])    # Event log takes 1/5 of the width
    
    # Draw base graph in light gray
    nx.draw_networkx_edges(G, pos, alpha=0.2, edge_color='gray', ax=ax_main)
    
    # Track actual path and resource usage
    actual_path = []
    events = []  # List of (step_number, event_description) tuples
    
    # Get the planned path and actual progress
    planned_path = mission_data['plan']['path']
    success = mission_data['outcome']['success']
    failure_reason = mission_data['outcome'].get('failure_reason', '')
    
    # Get resource information
    resources_initial = mission_data['outcome']['resources']['initial']
    resources_remaining = mission_data['outcome']['resources']['remaining']
    
    # Track resource usage at each node
    resource_usage_at_node = {}  # node -> {resource: amount}
    death_node = None  # Track where the team died
    
    # Log mission start
    events.append((0, f"Mission started at node {planned_path[0]}"))
    
    # Process each node in the path
    for step, node in enumerate(planned_path, 1):
        actual_path.append(node)
        events.append((step, f"Arrived at node {node}"))
        
        # Initialize resource tracking for this node
        resource_usage_at_node[node] = {}
        
        # Check for hazards at current node
        radiation_level = proxy_data['indicators']['nodes'].get(str(node), {}).get('radiation_readings', 0)
        zombie_level = proxy_data['indicators']['nodes'].get(str(node), {}).get('thermal_readings', 0)
        
        if radiation_level > 0.4:  # Radiation hazard
            events.append((step, f"High radiation detected (level: {radiation_level:.2f})"))
            if resources_remaining['radiation_suits'] <= 0:
                events.append((step, f"TEAM DIED - No radiation suits available"))
                death_node = node
                break
            resources_remaining['radiation_suits'] -= 1
            resource_usage_at_node[node]['radiation_suits'] = 1
            events.append((step, f"Used radiation suit"))
            
        if zombie_level > 0.5:  # Zombie hazard
            events.append((step, f"Zombie horde encountered (level: {zombie_level:.2f})"))
            if resources_remaining['ammo'] <= 0:
                events.append((step, f"TEAM DIED - No ammo available"))
                death_node = node
                break
            resources_remaining['ammo'] -= 1
            resource_usage_at_node[node]['ammo'] = 1
            events.append((step, f"Used ammo against zombies"))
        
        # If not last node, check edge to next node
        if node != planned_path[-1]:
            next_node = planned_path[planned_path.index(node) + 1]
            edge_key = f"{node}_{next_node}"
            blockage_level = proxy_data['indicators']['edges'].get(edge_key, {}).get('structural_damage', 0)
            
            if blockage_level > 0.4:  # Blockage hazard
                events.append((step, f"Path blocked to node {next_node} (damage level: {blockage_level:.2f})"))
                if resources_remaining['explosives'] <= 0:
                    events.append((step, f"TEAM DIED - No explosives available"))
                    death_node = node
                    break
                resources_remaining['explosives'] -= 1
                resource_usage_at_node[node]['explosives'] = 1
                events.append((step, f"Used explosives to clear path"))
            
            events.append((step, f"Moving to node {next_node}"))
    
    # Add final outcome
    final_step = len(actual_path)
    if death_node is None and not success:
        death_node = actual_path[-1]
        events.append((final_step, f"TEAM DIED - {failure_reason}"))
    elif success:
        events.append((final_step, f"Successfully reached extraction point at node {actual_path[-1]}"))
    
    # Sort events chronologically
    events.sort(key=lambda x: x[0])  # Sort by step number (stable sort preserves order within steps)
    log_text = "Mission Events:\n\n"
    current_step = 0
    for step, event in events:
        if step != current_step:
            log_text += f"\nStep {step}:\n"
            current_step = step
        log_text += f"- {event}\n"
    
    # Add resource summary at the end
    log_text += "\nFinal Resource Status:\n"
    for resource, initial in resources_initial.items():
        used = initial - resources_remaining[resource]
        if used > 0 or initial > 0:
            log_text += f"- {resource.replace('_', ' ').title()}: {used}/{initial} used\n"
    
    # Visualization
    node_colors = []
    node_sizes = []
    node_labels = {}
    
    # Process nodes
    for node in G.nodes():
        label_parts = [str(node)]
        
        # Add resource usage to label if any
        if node in resource_usage_at_node and resource_usage_at_node[node]:
            resources_used = []
            for resource, amount in resource_usage_at_node[node].items():
                if amount > 0:
                    resources_used.append(resource.split('_')[0][:3])  # First 3 letters
            if resources_used:
                label_parts.append('+'.join(resources_used))
        
        # Create final label
        if node == city_data['configuration']['start_node']:
            label_parts.append("START")
            node_colors.append('#00ff00')  # Green for start
            node_sizes.append(800)
        elif node in city_data['configuration']['extraction_nodes']:
            label_parts.append("EXIT")
            node_colors.append('#ffd700')  # Gold for exits
            node_sizes.append(800)
        elif node == death_node:
            node_colors.append('#ff0000')  # Red for death location
            node_sizes.append(1000)
            label_parts.append("DIED")
        elif node in actual_path:
            node_colors.append('#87CEEB')  # Sky blue for visited nodes
            node_sizes.append(600)
        else:
            node_colors.append('#D3D3D3')  # Light gray for unvisited
            node_sizes.append(400)
        
        node_labels[node] = '\n'.join(label_parts)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                          node_size=node_sizes, ax=ax_main)
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8, ax=ax_main)
    
    # Draw planned path with dashed blue line
    planned_edges = list(zip(planned_path[:-1], planned_path[1:]))
    nx.draw_networkx_edges(G, pos, edgelist=planned_edges, 
                          edge_color='#1f77b4', width=2,  # Standard blue
                          alpha=0.5, style='dashed',
                          ax=ax_main, label='Planned Path')
    
    # Draw actual traveled path
    actual_edges = list(zip(actual_path[:-1], actual_path[1:]))
    nx.draw_networkx_edges(G, pos, edgelist=actual_edges, 
                          edge_color='#2ecc71' if success else '#e74c3c',  # Green if success, red if failed
                          width=3, alpha=0.8,
                          ax=ax_main, label='Actual Path')
    
    # Add event log in the right panel
    ax_log.axis('off')
    ax_log.text(0, 1, log_text, va='top', ha='left', wrap=True)
    
    # Add legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#00ff00', 
                  markersize=15, label='Start Point'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#ffd700', 
                  markersize=15, label='Exit Point'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#ff0000', 
                  markersize=15, label='Death Location'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#87CEEB', 
                  markersize=15, label='Visited Node'),
        plt.Line2D([0], [0], color='#1f77b4', linestyle='--', 
                  lw=2, label='Planned Path'),
        plt.Line2D([0], [0], color='#2ecc71', linestyle='-', 
                  lw=3, label='Successful Path'),
        plt.Line2D([0], [0], color='#e74c3c', linestyle='-', 
                  lw=3, label='Failed Path')
    ]
    
    ax_main.legend(handles=legend_elements, loc='upper right')
    
    # Main title and information
    plt.suptitle('Evacuation Mission Analysis\n' + 
                f'{"Success" if success else "Failed"} - ' +
                f'Time: {mission_data["outcome"]["time_taken"]:.1f} units\n' +
                f'Path Length: {mission_data["outcome"]["path_length"]:.1f}', 
                y=0.95)
    
    ax_main.axis('off')
    plt.tight_layout()
    
    # Save plot
    save_city_plot(plt, "city_layout", policy_name, experiment_id, city_id)
    plt.close()

def analyze_resource_usage(mission_data: Dict, policy_name: str, experiment_id: str, city_id: str):
    """Analyze and visualize resource usage for the mission"""
    plt.figure(figsize=(10, 6))
    
    resources = mission_data['outcome']['resources']
    initial = resources['initial']
    remaining = resources['remaining']
    
    resource_types = list(initial.keys())
    x = range(len(resource_types))
    
    # Calculate used resources
    used = {rt: initial[rt] - remaining[rt] for rt in resource_types}
    
    # Plot bars
    plt.bar(x, [initial[rt] for rt in resource_types], 
            alpha=0.4, label='Initial', color='lightblue')
    plt.bar(x, [used[rt] for rt in resource_types], 
            alpha=0.8, label='Used', color='blue')
    
    plt.xticks(x, [rt.replace('_', ' ').title() for rt in resource_types])
    plt.ylabel('Amount')
    plt.title('Resource Usage Analysis')
    
    # Add efficiency percentages
    for i, rt in enumerate(resource_types):
        if initial[rt] > 0:
            efficiency = (used[rt] / initial[rt]) * 100
            plt.text(i, initial[rt], f'{efficiency:.1f}%\nefficient', 
                    ha='center', va='bottom')
    
    plt.legend()
    save_city_plot(plt, "resource_usage", policy_name, experiment_id, city_id)
    plt.close()

def analyze_proxy_patterns(city_data: Dict, proxy_data: Dict, mission_data: Dict,
                      policy_name: str, experiment_id: str, city_id: str):
    """Analyze and visualize proxy indicator patterns along the evacuation path"""
    plt.figure(figsize=(15, 12))
    
    # Create subplots with different sizes
    gs = plt.GridSpec(3, 2, height_ratios=[2, 1, 1])
    ax_path = plt.subplot(gs[0, :])  # Path analysis takes full width
    ax_node = plt.subplot(gs[1, 0])  # Node indicators
    ax_edge = plt.subplot(gs[1, 1])  # Edge indicators
    ax_summary = plt.subplot(gs[2, :])  # Summary takes full width
    
    # Get path information
    path = mission_data['plan']['path']
    path_edges = list(zip(path[:-1], path[1:]))
    steps = range(len(path))
    
    # Initialize data structures for indicators
    node_indicators = {}
    edge_indicators = {}
    
    # Collect node indicators along path
    for node in path:
        node_data = proxy_data['indicators']['nodes'].get(str(node), {})
        for indicator, value in node_data.items():
            if indicator not in node_indicators:
                node_indicators[indicator] = []
            node_indicators[indicator].append(value)
    
    # Collect edge indicators along path
    for i, edge in enumerate(path_edges):
        edge_key = f"{edge[0]}_{edge[1]}"
        edge_data = proxy_data['indicators']['edges'].get(edge_key, {})
        for indicator, value in edge_data.items():
            if indicator not in edge_indicators:
                edge_indicators[indicator] = [0] * len(path)  # Initialize with zeros for all nodes
            edge_indicators[indicator][i] = value
            if i < len(path) - 1:  # Copy value to next node except for last edge
                edge_indicators[indicator][i + 1] = value
    
    # Plot path progression if we have data
    has_data = False
    
    # Plot node indicators along path
    for indicator, values in node_indicators.items():
        if values:  # Only plot if we have values
            has_data = True
            label = indicator.replace('_', ' ').title()
            ax_path.plot(steps, values, marker='o', label=f'Node: {label}', alpha=0.7)
    
    # Plot edge indicators along path
    for indicator, values in edge_indicators.items():
        if any(v != 0 for v in values):  # Only plot if we have non-zero values
            has_data = True
            label = indicator.replace('_', ' ').title()
            ax_path.plot(steps, values, marker='s', label=f'Edge: {label}', 
                        linestyle='--', alpha=0.7)
    
    ax_path.set_xlabel('Step Along Path')
    ax_path.set_ylabel('Indicator Value')
    ax_path.set_title('Environmental Indicators Along Evacuation Path\n' +
                     'Showing how conditions change during evacuation')
    if has_data:
        ax_path.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax_path.grid(True, alpha=0.3)
    
    # Node indicators summary
    node_averages = {}
    for indicator, values in node_indicators.items():
        if values:  # Only calculate mean if we have values
            node_averages[indicator] = sum(values) / len(values)
    
    if node_averages:
        bars_node = ax_node.bar(range(len(node_averages)), 
                               list(node_averages.values()),
                               alpha=0.7)
        
        ax_node.set_xticks(range(len(node_averages)))
        ax_node.set_xticklabels([k.replace('_', ' ').title() 
                                for k in node_averages.keys()],
                               rotation=45, ha='right')
        ax_node.set_title('Average Node Indicators')
        
        # Add value labels
        for bar in bars_node:
            height = bar.get_height()
            ax_node.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.2f}',
                        ha='center', va='bottom')
    else:
        ax_node.text(0.5, 0.5, 'No node indicators available',
                    ha='center', va='center')
        ax_node.set_title('Node Indicators (Empty)')
    
    # Edge indicators summary
    edge_averages = {}
    for indicator, values in edge_indicators.items():
        if any(v != 0 for v in values):  # Only calculate mean if we have non-zero values
            edge_averages[indicator] = sum(v for v in values if v != 0) / sum(1 for v in values if v != 0)
    
    if edge_averages:
        bars_edge = ax_edge.bar(range(len(edge_averages)), 
                               list(edge_averages.values()),
                               alpha=0.7, color='orange')
        
        ax_edge.set_xticks(range(len(edge_averages)))
        ax_edge.set_xticklabels([k.replace('_', ' ').title() 
                                for k in edge_averages.keys()],
                               rotation=45, ha='right')
        ax_edge.set_title('Average Edge Indicators')
        
        # Add value labels
        for bar in bars_edge:
            height = bar.get_height()
            ax_edge.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.2f}',
                        ha='center', va='bottom')
    else:
        ax_edge.text(0.5, 0.5, 'No edge indicators available',
                    ha='center', va='center')
        ax_edge.set_title('Edge Indicators (Empty)')
    
    # Create summary statistics (safely handling empty cases)
    summary_data = {
        'Path Length': len(path)
    }
    
    # Only add statistics if we have data
    if node_indicators:
        node_values = [v for values in node_indicators.values() for v in values if v is not None]
        if node_values:
            summary_data['Avg Node Risk'] = sum(node_values) / len(node_values)
            summary_data['Max Node Risk'] = max(node_values)
    
    if edge_indicators:
        edge_values = [v for values in edge_indicators.values() for v in values if v != 0]
        if edge_values:
            summary_data['Avg Edge Risk'] = sum(edge_values) / len(edge_values)
            summary_data['Max Edge Risk'] = max(edge_values)
    
    # Plot summary statistics
    summary_pos = range(len(summary_data))
    summary_vals = list(summary_data.values())
    bars_summary = ax_summary.bar(summary_pos, summary_vals, 
                                alpha=0.7, color='lightblue')
    
    ax_summary.set_xticks(summary_pos)
    ax_summary.set_xticklabels(list(summary_data.keys()),
                              rotation=45, ha='right')
    ax_summary.set_title('Path Summary Statistics')
    
    # Add value labels
    for bar in bars_summary:
        height = bar.get_height()
        ax_summary.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.2f}',
                       ha='center', va='bottom')
    
    plt.tight_layout()
    save_city_plot(plt, "proxy_analysis", policy_name, experiment_id, city_id)
    plt.close()

def plot_resource_correlation(city_data: Dict, proxy_data: Dict, mission_data: Dict,
                        policy_name: str, experiment_id: str, city_id: str):
    """Plot correlation between proxy indicators and resource usage"""
    plt.figure(figsize=(15, 10))
    
    # Create two subplots
    gs = plt.GridSpec(2, 1, height_ratios=[2, 1])
    ax_heatmap = plt.subplot(gs[0])
    ax_summary = plt.subplot(gs[1])
    
    # Collect resource usage data
    resources = mission_data['outcome']['resources']
    initial = resources['initial']
    remaining = resources['remaining']
    used = {rt: initial[rt] - remaining[rt] for rt in initial.keys()}
    resource_names = list(initial.keys())
    
    # Collect proxy indicators
    node_indicators = proxy_data['indicators']['nodes']
    edge_indicators = proxy_data['indicators']['edges']
    
    # Calculate average indicators for the path
    path = mission_data['plan']['path']
    path_edges = list(zip(path[:-1], path[1:]))
    
    # Initialize data structures for indicators
    indicator_values = {
        'Node Indicators': {},
        'Edge Indicators': {}
    }
    
    # Collect node indicators along the path
    for node in path:
        node_data = node_indicators.get(str(node), {})
        for indicator, value in node_data.items():
            if indicator not in indicator_values['Node Indicators']:
                indicator_values['Node Indicators'][indicator] = []
            indicator_values['Node Indicators'][indicator].append(value)
    
    # Collect edge indicators along the path
    for edge in path_edges:
        edge_key = f"{edge[0]}_{edge[1]}"
        edge_data = edge_indicators.get(edge_key, {})
        for indicator, value in edge_data.items():
            if indicator not in indicator_values['Edge Indicators']:
                indicator_values['Edge Indicators'][indicator] = []
            indicator_values['Edge Indicators'][indicator].append(value)
    
    # Calculate averages
    avg_indicators = {}
    for category in indicator_values:
        for indicator, values in indicator_values[category].items():
            if values:  # Only include if we have values
                key = f"{category}: {indicator.replace('_', ' ').title()}"
                avg_indicators[key] = np.mean(values)
    
    # Create correlation matrix
    indicator_names = list(avg_indicators.keys())
    correlation_matrix = np.zeros((len(indicator_names), len(resource_names)))
    
    # Calculate correlations
    for i, indicator in enumerate(indicator_names):
        indicator_val = avg_indicators[indicator]
        for j, resource in enumerate(resource_names):
            # Calculate correlation based on resource usage efficiency
            efficiency = used[resource] / initial[resource] if initial[resource] > 0 else 0
            # Simple correlation based on normalized values
            correlation_matrix[i, j] = indicator_val * efficiency
    
    # Normalize correlation matrix
    if correlation_matrix.size > 0:  # Only normalize if we have data
        correlation_matrix = (correlation_matrix - correlation_matrix.min()) / \
                            (correlation_matrix.max() - correlation_matrix.min() + 1e-10)
    
    # Plot heatmap
    im = ax_heatmap.imshow(correlation_matrix, aspect='auto', cmap='RdYlBu')
    plt.colorbar(im, ax=ax_heatmap, label='Correlation Strength')
    
    # Add labels
    ax_heatmap.set_yticks(range(len(indicator_names)))
    ax_heatmap.set_yticklabels(indicator_names)
    ax_heatmap.set_xticks(range(len(resource_names)))
    ax_heatmap.set_xticklabels([r.replace('_', ' ').title() for r in resource_names], 
                              rotation=45, ha='right')
    
    # Add correlation values
    for i in range(len(indicator_names)):
        for j in range(len(resource_names)):
            text = f'{correlation_matrix[i, j]:.2f}'
            ax_heatmap.text(j, i, text, ha='center', va='center')
    
    ax_heatmap.set_title('Resource Usage vs Environmental Indicators\n' +
                        'Correlation Strength Heatmap')
    
    # Add summary bar plot
    resource_efficiency = []
    for resource in resource_names:
        efficiency = used[resource] / initial[resource] if initial[resource] > 0 else 0
        resource_efficiency.append(efficiency * 100)
    
    bars = ax_summary.bar(range(len(resource_names)), resource_efficiency, 
                         color='skyblue', alpha=0.7)
    
    # Add percentage labels
    for bar in bars:
        height = bar.get_height()
        ax_summary.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}%',
                       ha='center', va='bottom')
    
    ax_summary.set_xticks(range(len(resource_names)))
    ax_summary.set_xticklabels([r.replace('_', ' ').title() for r in resource_names],
                              rotation=45, ha='right')
    ax_summary.set_ylabel('Usage Efficiency (%)')
    ax_summary.set_title('Resource Usage Efficiency Summary')
    
    plt.tight_layout()
    save_city_plot(plt, "resource_correlation", policy_name, experiment_id, city_id)
    plt.close()

def analyze_city_scenario(city_id: str, policy_name: str, experiment_id: str):
    """Analyze a single city scenario"""
    # Load city data
    city_dir = os.path.join('data', 'policies', policy_name, 'experiments',
                           experiment_id, 'cities', f'city_{city_id}')
    
    with open(os.path.join(city_dir, 'definition.json'), 'r') as f:
        city_data = json.load(f)
    
    with open(os.path.join(city_dir, 'proxy_data.json'), 'r') as f:
        proxy_data = json.load(f)
    
    with open(os.path.join(city_dir, 'mission_results.json'), 'r') as f:
        mission_data = json.load(f)
    
    # Create visualizations directory
    os.makedirs(os.path.join(city_dir, 'visualizations'), exist_ok=True)
    
    # Generate visualizations
    plot_city_graph(city_data, proxy_data, mission_data, 
                   policy_name, experiment_id, city_id)
    analyze_resource_usage(mission_data, policy_name, experiment_id, city_id)
    analyze_proxy_patterns(city_data, proxy_data, mission_data,
                          policy_name, experiment_id, city_id)
    plot_resource_correlation(city_data, proxy_data, mission_data,
                               policy_name, experiment_id, city_id)

def generate_aggregated_data(results: Dict, policy_name: str, experiment_id: str):
    """Generate and save aggregated analysis data"""
    agg_dir = os.path.join('data', 'policies', policy_name, 'experiments',
                          experiment_id, 'aggregated')
    os.makedirs(agg_dir, exist_ok=True)
    
    # Save summary statistics
    summary = {
        'overall': {
            'total_missions': results['total_runs'],
            'success_rate': results['success_rate'],
            'avg_mission_time': results['avg_time'],
            'avg_path_length': results['avg_path_length']
        },
        'resources': results['resource_metrics'],
        'by_city_size': results['by_size']
    }
    
    with open(os.path.join(agg_dir, 'summary.json'), 'w') as f:
        json.dump(summary, f, indent=4)
    
    # Save detailed metrics for each resource type
    resource_metrics = {
        'resource_type': [],
        'avg_allocated': [],
        'avg_used': [],
        'avg_remaining': [],
        'efficiency': []
    }
    
    for rt, metrics in results['resource_metrics'].items():
        resource_metrics['resource_type'].append(rt)
        resource_metrics['avg_allocated'].append(metrics['avg_allocated'])
        used = metrics['avg_allocated'] - metrics['avg_remaining']
        resource_metrics['avg_used'].append(used)
        resource_metrics['avg_remaining'].append(metrics['avg_remaining'])
        efficiency = used / metrics['avg_allocated'] if metrics['avg_allocated'] > 0 else 0
        resource_metrics['efficiency'].append(efficiency)
    
    with open(os.path.join(agg_dir, 'resource_metrics.json'), 'w') as f:
        json.dump(resource_metrics, f, indent=4) 