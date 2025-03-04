import matplotlib.pyplot as plt
import networkx as nx
from typing import List, Tuple

from public.lib.interfaces import (
    CityGraph, ProxyData, SimulationResult, 
    PolicyResult, ResourceTypes
)

def visualize_simulation(city: CityGraph, proxy_data: ProxyData, 
                        policy_result: PolicyResult, sim_result: SimulationResult):
    """
    Visualize a single evacuation mission with environmental data
    
    Returns:
        matplotlib.figure.Figure: The generated figure
    """
    fig = plt.figure(figsize=(15, 12))
    
    # Create graph from city data
    G = city.graph
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
    planned_path = policy_result.path
    success = sim_result.success
    failure_reason = sim_result.failure_reason
    
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
        radiation_level = proxy_data.node_data[node].get('radiation_readings', 0)
        zombie_level = proxy_data.node_data[node].get('thermal_readings', 0)
        
        if radiation_level > 0.35:  # Radiation hazard
            events.append((step, f"High radiation detected (level: {radiation_level:.2f})"))
            if sim_result.resources.used['radiation_suits'] >= sim_result.resources.allocated['radiation_suits']:
                events.append((step, f"TEAM DIED - No radiation suits available"))
                death_node = node
                break
            resource_usage_at_node[node]['radiation_suits'] = 1
            events.append((step, f"Used radiation suit"))
            
        if zombie_level > 0.45:  # Zombie hazard
            events.append((step, f"Zombie horde encountered (level: {zombie_level:.2f})"))
            if sim_result.resources.used['ammo'] >= sim_result.resources.allocated['ammo']:
                events.append((step, f"TEAM DIED - No ammo available"))
                death_node = node
                break
            resource_usage_at_node[node]['ammo'] = 1
            events.append((step, f"Used ammo against zombies"))
        
        # If not last node, check edge to next node
        if node != planned_path[-1]:
            next_node = planned_path[planned_path.index(node) + 1]
            edge = tuple(sorted([node, next_node]))
            blockage_level = proxy_data.edge_data.get(edge, {}).get('structural_damage', 0)
            
            if blockage_level > 0.4:  # Blockage hazard
                events.append((step, f"Path blocked to node {next_node} (damage level: {blockage_level:.2f})"))
                if sim_result.resources.used['explosives'] >= sim_result.resources.allocated['explosives']:
                    events.append((step, f"TEAM DIED - No explosives available"))
                    death_node = node
                    break
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
    
    # Sort events chronologically and create event log
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
    for resource in ResourceTypes.all_types():
        used = sim_result.resources.used[resource]
        allocated = sim_result.resources.allocated[resource]
        if used > 0 or allocated > 0:
            log_text += f"- {resource.replace('_', ' ').title()}: {used}/{allocated} used\n"
    
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
        if node == city.starting_node:
            label_parts.append("START")
            node_colors.append('#00ff00')  # Green for start
            node_sizes.append(800)
        elif node in city.extraction_nodes:
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
                f'Time: {sim_result.time_taken:.1f} units\n' +
                f'Path Length: {sim_result.path_length:.1f}', 
                y=0.95)
    
    plt.tight_layout()
    plt.show()
    
    return fig 