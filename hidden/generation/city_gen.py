import random
import networkx as nx
import numpy as np
from typing import Tuple, List

from public.lib.interfaces import CityGraph

class CityGenerator:
    """Generates the city layout"""
    
    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            
    def calculate_max_resources(self, n_nodes: int) -> int:
        """
        Calculate maximum resource slots available.
        Makes scenarios challenging by:
        - Sometimes providing too few resources (impossible)
        - Sometimes just enough (need perfect allocation)
        - Sometimes more than needed (test efficiency)
        """
        # Base calculation using graph size
        base = max(2, int(np.log2(n_nodes) * 2))
        
        # Add randomization to create different scenarios
        scenario_type = random.random()
        
        if scenario_type < 0.2:  # 20% chance of impossible scenario
            # Reduce resources to make it impossible
            max_resources = max(1, base - random.randint(2, 4))
            
        elif scenario_type < 0.5:  # 30% chance of challenging scenario
            # Just enough resources if used perfectly
            max_resources = base
            
        elif scenario_type < 0.8:  # 30% chance of normal scenario
            # Slightly more resources than minimum needed
            max_resources = base + random.randint(1, 3)
            
        else:  # 20% chance of abundant resources
            # Test efficiency with extra resources
            max_resources = base + random.randint(4, 6)
            
        return max_resources
            
    def generate(self, n_nodes: int) -> Tuple[CityGraph, int]:
        """
        Generate a random city layout
        
        Returns:
            Tuple of (CityGraph, max_resources)
        """
        city = CityGraph()
        
        # Generate random positions
        positions = [(random.uniform(0, 100), random.uniform(0, 100)) 
                    for _ in range(n_nodes)]
        
        # Add nodes
        for i in range(n_nodes):
            city.add_node(i, positions[i])
            
        # Add edges (connect to 3 nearest neighbors)
        for i in range(n_nodes):
            distances = [(j, np.sqrt((positions[i][0] - positions[j][0])**2 + 
                                   (positions[i][1] - positions[j][1])**2))
                        for j in range(n_nodes) if j != i]
            nearest = sorted(distances, key=lambda x: x[1])[:3]
            for j, dist in nearest:
                city.add_edge(i, j, dist)
                
        # Set starting node (random)
        city.set_starting_node(random.randint(0, n_nodes-1))
        
        # Set extraction nodes (2 random nodes)
        available_nodes = list(set(range(n_nodes)) - {city.starting_node})
        extraction_nodes = random.sample(available_nodes, 2)
        for node in extraction_nodes:
            city.add_extraction_node(node)
            
        # Calculate max resources for this city
        max_resources = self.calculate_max_resources(n_nodes)
            
        return city, max_resources 