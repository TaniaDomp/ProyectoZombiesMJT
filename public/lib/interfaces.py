from typing import Dict, List, Tuple
import networkx as nx
import copy

class ResourceTypes:
    """Constants for resource types"""
    EXPLOSIVES = 'explosives'
    AMMO = 'ammo'
    RADIATION_SUITS = 'radiation_suits'
    
    @classmethod
    def all_types(cls) -> List[str]:
        return [cls.EXPLOSIVES, cls.AMMO, cls.RADIATION_SUITS]

class CityGraph:
    """Represents the city layout with nodes and edges"""

    def __init__(self):
        self.graph: nx.Graph = nx.Graph()
        self.starting_node: int = None
        self.extraction_nodes: List[int] = []

    def add_node(self, node_id: int, pos: Tuple[float, float]):
        """Add a node with its position"""
        self.graph.add_node(node_id, pos=pos)

    def add_edge(self, node1: int, node2: int, weight: float):
        """Add an edge between nodes with its weight (distance)"""
        self.graph.add_edge(node1, node2, weight=weight)

    def set_starting_node(self, node_id: int):
        """Set the evacuation starting point"""
        if node_id in self.graph.nodes:
            self.starting_node = node_id

    def add_extraction_node(self, node_id: int):
        """Add a possible extraction point"""
        if node_id in self.graph.nodes:
            self.extraction_nodes.append(node_id)

    def copy(self) -> "CityGraph":
        """Creates a deep copy of the CityGraph object"""
        new_copy = CityGraph()
        new_copy.graph = self.graph.copy()  # Deep copy the graph
        new_copy.starting_node = self.starting_node
        new_copy.extraction_nodes = self.extraction_nodes.copy()  # Copy list to avoid mutation
        return new_copy


class ProxyData:
    """Contains proxy indicators for nodes and edges"""
    def __init__(self):
        self.node_data: Dict[int, Dict] = {}  # node_id -> indicators
        self.edge_data: Dict[Tuple[int, int], Dict] = {}  # (node1, node2) -> indicators
        
    def add_node_indicator(self, node_id: int, indicator_type: str, value: float):
        """Add an indicator for a node"""
        if node_id not in self.node_data:
            self.node_data[node_id] = {}
        self.node_data[node_id][indicator_type] = value
        
    def add_edge_indicator(self, node1: int, node2: int, indicator_type: str, value: float):
        """Add an indicator for an edge"""
        edge = tuple(sorted([node1, node2]))  # Ensure consistent edge representation
        if edge not in self.edge_data:
            self.edge_data[edge] = {}
        self.edge_data[edge][indicator_type] = value

class ResourceUsage:
    """Tracks resource usage and effectiveness"""
    def __init__(self):
        self.allocated: Dict[str, int] = {rt: 0 for rt in ResourceTypes.all_types()}
        self.used: Dict[str, int] = {rt: 0 for rt in ResourceTypes.all_types()}
        self.needed: Dict[str, int] = {rt: 0 for rt in ResourceTypes.all_types()}
        self.effective_uses: Dict[str, int] = {rt: 0 for rt in ResourceTypes.all_types()}
        
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'allocated': self.allocated,
            'used': self.used,
            'needed': self.needed,
            'effective_uses': self.effective_uses,
            'efficiency': {
                rt: (self.effective_uses[rt] / self.used[rt] if self.used[rt] > 0 else 0.0)
                for rt in ResourceTypes.all_types()
            }
        }

class PolicyResult:
    """Contains the evacuation plan"""
    def __init__(self, path: List[int], resources: Dict[str, int]):
        self.path = path  # List of node IDs forming the evacuation path
        self.resources = resources  # Dict mapping resource type to amount
        
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'path': self.path,
            'resources': self.resources
        }

class SimulationResult:
    """Contains the results of a simulation run"""
    def __init__(self):
        self.success: bool = False
        self.path_length: float = 0.0
        self.time_taken: float = 0.0
        self.obstacles_encountered: int = 0
        self.resources = ResourceUsage()
        self.failure_reason: str = None
        self.events: List[Tuple[int, str]] = []  # List of (step_number, event_description)
        
    def set_metrics(self, success: bool, path_length: float, time: float,
                   obstacles: int, resources: ResourceUsage, 
                   failure_reason: str = None, events: List[Tuple[int, str]] = None):
        """Set all metrics at once"""
        self.success = success
        self.path_length = path_length
        self.time_taken = time
        self.obstacles_encountered = obstacles
        self.resources = resources
        self.failure_reason = failure_reason
        if events is not None:
            self.events = events
        
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'success': self.success,
            'path_length': self.path_length,
            'time_taken': self.time_taken,
            'obstacles_encountered': self.obstacles_encountered,
            'resources': self.resources.to_dict(),
            'failure_reason': self.failure_reason,
            'events': self.events
        } 