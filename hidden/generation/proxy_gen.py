import random
import networkx as nx
from typing import Dict, Tuple

from public.lib.interfaces import CityGraph, ProxyData

class ProxyGenerator:
    """Generates environmental indicators based on complex patterns of true events"""
    
    def __init__(self, noise_level: float = 0.1, seed: int = None):
        """
        Args:
            noise_level: Uncertainty in observations (0-1)
            seed: Random seed for reproducibility
        """
        self.noise_level = noise_level
        if seed is not None:
            random.seed(seed)
            
    def _add_noise(self, value: float) -> float:
        """Add uncertainty to observations while keeping in [0,1]"""
        noise = random.uniform(-self.noise_level, self.noise_level)
        return max(0.0, min(1.0, value + noise))
    
    def _calculate_node_metrics(self, city: CityGraph, true_state: Dict) -> Dict[int, Dict]:
        """Calculate complex node metrics based on neighborhood patterns"""
        metrics = {}
        
        # Calculate base network metrics
        centrality = nx.betweenness_centrality(city.graph)
        clustering = nx.clustering(city.graph)
        
        for node in city.graph.nodes():
            neighbors = list(city.graph.neighbors(node))
            metrics[node] = {
                # Infrastructure metrics
                'centrality': centrality[node],
                'clustering': clustering.get(node, 0),
                
                # Neighborhood radiation analysis
                'radiation_zone': any(
                    true_state['radiation'].get(n, 0) > 0.6
                    for n in neighbors + [node]
                ),
                'radiation_gradient': sum(
                    true_state['radiation'].get(n, 0)
                    for n in neighbors + [node]
                ) / (len(neighbors) + 1),
                
                # Zombie activity patterns
                'zombie_presence': sum(
                    1 for n in neighbors + [node]
                    if true_state['zombies'].get(n, 0) > 0.7
                ) / (len(neighbors) + 1),
                'zombie_cluster': any(
                    true_state['zombies'].get(n1, 0) > 0.5 and
                    true_state['zombies'].get(n2, 0) > 0.5
                    for n1 in neighbors
                    for n2 in set(city.graph.neighbors(n1)) & set(neighbors)
                ),
                
                # Structural analysis
                'blocked_paths': sum(
                    1 for n in neighbors
                    if true_state['blockages'].get(tuple(sorted([node, n])), False)
                ),
                'access_routes': len(neighbors),
                'isolation_risk': sum(
                    1 for n in neighbors
                    if sum(1 for nn in city.graph.neighbors(n)
                        if true_state['blockages'].get(tuple(sorted([n, nn])), False)
                    ) > len(list(city.graph.neighbors(n))) / 2
                ) / max(1, len(neighbors))
            }
        
        return metrics
    
    def _calculate_edge_metrics(self, city: CityGraph, true_state: Dict, node_metrics: Dict) -> Dict[Tuple[int, int], Dict]:
        """Calculate complex edge metrics based on endpoint patterns"""
        edge_metrics = {}
        
        for edge in city.graph.edges():
            n1, n2 = edge
            edge_key = tuple(sorted(edge))
            
            # Get common neighbors between endpoints
            common_neighbors = set(city.graph.neighbors(n1)) & set(city.graph.neighbors(n2))
            
            edge_metrics[edge_key] = {
                # Structural integrity
                'is_blocked': true_state['blockages'].get(edge_key, False),
                'nearby_blockages': sum(
                    1 for n in common_neighbors
                    if any(true_state['blockages'].get(tuple(sorted([n, end])), False)
                          for end in [n1, n2])
                ) / max(1, len(common_neighbors)),
                
                # Environmental hazards
                'radiation_exposure': max(
                    true_state['radiation'].get(n1, 0),
                    true_state['radiation'].get(n2, 0)
                ),
                'radiation_gradient': abs(
                    true_state['radiation'].get(n1, 0) -
                    true_state['radiation'].get(n2, 0)
                ),
                
                # Activity patterns
                'zombie_movement': (
                    true_state['zombies'].get(n1, 0) +
                    true_state['zombies'].get(n2, 0)
                ) / 2,
                'activity_cluster': sum(
                    1 for n in common_neighbors
                    if true_state['zombies'].get(n, 0) > 0.4
                ) / max(1, len(common_neighbors))
            }
            
        return edge_metrics
            
    def generate(self, city: CityGraph, true_state: Dict) -> ProxyData:
        """
        Generate proxy indicators based on complex environmental patterns
        
        Node Indicators:
            - seismic_activity: Based on nearby blockages and structural patterns
            - radiation_readings: Direct measurements with uncertainty
            - population_density: Pre-event data and current activity
            - emergency_calls: Historical distress patterns
            - thermal_readings: Current activity signatures
            - signal_strength: Communications infrastructure status
            - structural_integrity: Building and infrastructure condition
            
        Edge Indicators:
            - structural_damage: Physical route condition
            - signal_interference: Communications disruption
            - movement_sightings: Reported activity patterns
            - debris_density: Route blockage assessment
            - hazard_gradient: Change in environmental conditions
        """
        proxy = ProxyData()
        
        # Calculate complex metrics
        node_metrics = self._calculate_node_metrics(city, true_state)
        edge_metrics = self._calculate_edge_metrics(city, true_state, node_metrics)
        
        # Generate node indicators
        for node, metrics in node_metrics.items():
            # Seismic activity (structural patterns)
            seismic = (
                0.7 * (metrics['blocked_paths'] / max(1, metrics['access_routes'])) +
                0.3 * metrics['isolation_risk']
            )
            proxy.add_node_indicator(node, 'seismic_activity', self._add_noise(seismic))
            
            # Radiation readings (with detection patterns)
            radiation = (
                0.8 * true_state['radiation'].get(node, 0) +
                0.2 * metrics['radiation_gradient']
            )
            proxy.add_node_indicator(node, 'radiation_readings', self._add_noise(radiation))
            
            # Population density (pre-event patterns)
            density = (
                0.4 * metrics['clustering'] * metrics['centrality'] * 2 +
                0.6 * metrics['zombie_presence']
            )
            proxy.add_node_indicator(node, 'population_density', self._add_noise(density))
            
            # Emergency calls (historical patterns)
            emergency = max(
                metrics['zombie_cluster'] * 0.8,
                metrics['radiation_zone'] * 0.9,
                metrics['isolation_risk'] * 0.7
            )
            proxy.add_node_indicator(node, 'emergency_calls', self._add_noise(emergency))
            
            # Thermal readings (current activity)
            thermal = (
                0.7 * metrics['zombie_presence'] +
                0.3 * metrics['clustering']
            )
            proxy.add_node_indicator(node, 'thermal_readings', self._add_noise(thermal))
            
            # Signal strength (infrastructure status)
            signal = max(0, 1 - (
                0.4 * metrics['radiation_gradient'] +
                0.3 * (metrics['blocked_paths'] / max(1, metrics['access_routes'])) +
                0.3 * metrics['isolation_risk']
            ))
            proxy.add_node_indicator(node, 'signal_strength', self._add_noise(signal))
            
            # Structural integrity
            structural = max(0, 1 - (
                0.5 * (metrics['blocked_paths'] / max(1, metrics['access_routes'])) +
                0.3 * metrics['isolation_risk'] +
                0.2 * seismic
            ))
            proxy.add_node_indicator(node, 'structural_integrity', self._add_noise(structural))
        
        # Generate edge indicators
        for edge in city.graph.edges():
            edge_key = tuple(sorted(edge))
            metrics = edge_metrics[edge_key]
            
            # Structural damage
            damage = (
                0.6 * float(metrics['is_blocked']) +
                0.4 * metrics['nearby_blockages']
            )
            proxy.add_edge_indicator(edge[0], edge[1], 'structural_damage',
                                   self._add_noise(damage))
            
            # Signal interference
            interference = (
                0.4 * metrics['radiation_exposure'] +
                0.4 * metrics['radiation_gradient'] +
                0.2 * float(metrics['is_blocked'])
            )
            proxy.add_edge_indicator(edge[0], edge[1], 'signal_interference',
                                   self._add_noise(interference))
            
            # Movement sightings
            movement = (
                0.6 * metrics['zombie_movement'] +
                0.4 * metrics['activity_cluster']
            )
            proxy.add_edge_indicator(edge[0], edge[1], 'movement_sightings',
                                   self._add_noise(movement))
            
            # Debris density
            debris = (
                0.5 * damage +
                0.3 * metrics['nearby_blockages'] +
                0.2 * interference
            )
            proxy.add_edge_indicator(edge[0], edge[1], 'debris_density',
                                   self._add_noise(debris))
            
            # Hazard gradient
            hazard = max(
                metrics['radiation_gradient'],
                abs(node_metrics[edge[0]]['zombie_presence'] -
                    node_metrics[edge[1]]['zombie_presence'])
            )
            proxy.add_edge_indicator(edge[0], edge[1], 'hazard_gradient',
                                   self._add_noise(hazard))
            
        return proxy 