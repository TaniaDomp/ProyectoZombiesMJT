import random
import networkx as nx
import numpy as np
from typing import Dict, Tuple, List

from public.lib.interfaces import CityGraph

class TrueStateGenerator:
    """Generates the true state of obstacles in the city"""
    
    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            
    def _generate_blockages(self, city: CityGraph) -> Dict[Tuple[int, int], bool]:
        """
        Generate blockages that require explosives.
        Pattern: Blockages tend to form barriers around important paths.
        """
        blockages = {}
        
        # Calculate shortest paths to extraction points
        paths = []
        for target in city.extraction_nodes:
            try:
                path = nx.shortest_path(city.graph, city.starting_node, target, 
                                      weight='weight')
                paths.append(path)
            except nx.NetworkXNoPath:
                continue
                
        # Block edges near but not on these paths
        for path in paths:
            path_edges = set(zip(path[:-1], path[1:]))
            for i in range(len(path) - 1):
                # Look at edges adjacent to path
                for node in (path[i], path[i+1]):
                    for neighbor in city.graph.neighbors(node):
                        edge = tuple(sorted((node, neighbor)))
                        if edge not in path_edges:  # Don't block the actual path
                            if random.random() < 0.5:  # Increased from 0.4
                                blockages[edge] = True
                                
        # Add random blockages throughout the graph
        for edge in city.graph.edges():
            edge = tuple(sorted(edge))
            if edge not in blockages and random.random() < 0.25:  # 25% chance of random blockage
                blockages[edge] = True
                                
        return blockages
        
    def _generate_zombie_zones(self, city: CityGraph) -> Dict[int, float]:
        """
        Generate zombie concentrations that require ammo.
        Pattern: Zombies cluster in "chokepoints" of the graph.
        """
        zombies = {}
        
        # Calculate betweenness centrality (identifies chokepoints)
        centrality = nx.betweenness_centrality(city.graph)
        
        # Higher zombie concentration in high-centrality nodes
        for node in city.graph.nodes():
            base_prob = centrality[node] * 3  # Tripled to get higher values
            # Add more randomness for unpredictability
            zombies[node] = min(1.0, max(0.0, base_prob + random.uniform(-0.1, 0.3)))
            
            # 30% chance of zombie horde regardless of centrality
            if random.random() < 0.3:
                zombies[node] = max(zombies[node], random.uniform(0.5, 0.9))
        
        return zombies
        
    def _generate_radiation_zones(self, city: CityGraph) -> Dict[int, float]:
        """
        Generate radiation zones that require suits.
        Pattern: Radiation forms in connected regions, often near extraction points.
        """
        radiation = {node: 0.0 for node in city.graph.nodes()}
        
        # Start with extraction points as potential radiation sources
        candidates = set(city.extraction_nodes)
        
        # Add more random nodes to candidates
        n_extra = max(2, len(city.graph.nodes) // 8)  # Increased number of radiation sources
        candidates.update(random.sample(list(city.graph.nodes()), n_extra))
        
        # Select actual sources (more sources than before)
        sources = random.sample(list(candidates), 
                              k=max(2, len(candidates) * 2 // 3))
        
        # Calculate radiation spread (increased spread distance)
        max_distance = 4  # Increased from 3
        for source in sources:
            # Get all nodes within max_distance
            for node in city.graph.nodes():
                try:
                    distance = nx.shortest_path_length(city.graph, source, node)
                    if distance <= max_distance:
                        # Radiation decays less with distance
                        intensity = 1.0 * (1 - distance/max_distance)**1.5  # Reduced power for slower decay
                        radiation[node] = max(radiation[node], intensity)
                except nx.NetworkXNoPath:
                    continue
                    
        return radiation
        
    def generate(self, city: CityGraph) -> Dict:
        """
        Generate the true state of the city following logical patterns.
        Each type of obstacle requires specific resources to overcome:
        - Blockages -> Explosives
        - Zombies -> Ammo
        - Radiation -> Radiation Suits
        
        Args:
            city: The city layout
            
        Returns:
            Dict containing:
            - blockages: Dict[Tuple[int, int], bool]
            - zombies: Dict[int, float]
            - radiation: Dict[int, float]
        """
        # Generate each type of obstacle
        radiation = self._generate_radiation_zones(city)
        zombies = self._generate_zombie_zones(city)
        blockages = self._generate_blockages(city)
        
        return {
            'blockages': blockages,
            'zombies': zombies,
            'radiation': radiation
        } 