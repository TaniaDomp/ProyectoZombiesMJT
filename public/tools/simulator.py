import uuid
from typing import Tuple, Dict, Any

from public.lib.interfaces import CityGraph, ProxyData, SimulationResult
from public.lib.data_manager import DataManager
from hidden.generation.city_gen import CityGenerator
from hidden.generation.obstacles_gen import TrueStateGenerator
from hidden.generation.proxy_gen import ProxyGenerator
from hidden.evaluation.evaluator import PathEvaluator
import copy

class Simulator:
    """Interface for running evacuation simulations"""
    
    def __init__(self, policy_name: str, n_nodes: int = 30, seed: int = None):
        """
        Initialize simulator
        
        Args:
            policy_name: Name of the policy being tested
            n_nodes: Number of nodes in the city
            seed: Random seed for reproducibility
        """
        self.n_nodes = n_nodes
        self.seed = seed
        
        # Initialize components
        self.city_gen = CityGenerator(seed)
        self.true_state_gen = TrueStateGenerator(seed)
        self.proxy_gen = ProxyGenerator(seed=seed)
        self.evaluator = PathEvaluator(seed)
        
        # Initialize data manager
        self.data_manager = DataManager(policy_name)
        self.data_manager.save_policy_metadata()
        
    def run_simulation(self, policy) -> Tuple[SimulationResult, CityGraph, ProxyData]:
        """
        Run a single simulation following the data flow:
        1. Generate city (nodes, edges)
        2. Generate true state and proxy indicators
        3. Get policy decision (path + resources)
        4. Evaluate success/failure
        
        Args:
            policy: Policy object with plan_evacuation method
            
        Returns:
            Tuple of (SimulationResult, CityGraph used, ProxyData given to policy)
        """
        # 1. Generate city and get max resources
        city, max_resources = self.city_gen.generate(self.n_nodes)
        
        # 2. Generate true state and proxy data
        true_state = self.true_state_gen.generate(city)
        proxy_data = self.proxy_gen.generate(city, true_state)
        pass_city = city.copy()
        real_max_resources = max_resources
        # 3. Get policy decision
        policy_result = policy.plan_evacuation(pass_city, proxy_data, max_resources)
        
        # 4. Evaluate
        result = self.evaluator.evaluate(
            path=policy_result.path,
            resources=policy_result.resources,
            city=city,
            true_state=true_state,
            max_resources=real_max_resources
        )
        
        # Save data if experiment is active
        if self.data_manager.current_experiment:
            city_id = str(uuid.uuid4())[:8]
            
            # Prepare city data
            city_data = {
                'metadata': {
                    'n_nodes': self.n_nodes,
                    'seed': self.seed
                },
                'graph': {
                    'nodes': [
                        {
                            'id': node,
                            'x': city.graph.nodes[node]['pos'][0],
                            'y': city.graph.nodes[node]['pos'][1]
                        }
                        for node in city.graph.nodes()
                    ],
                    'edges': [
                        {
                            'source': edge[0],
                            'target': edge[1],
                            'weight': city.graph[edge[0]][edge[1]]['weight']
                        }
                        for edge in city.graph.edges()
                    ]
                },
                'simulation': {
                    'start_node': city.starting_node,
                    'extraction_nodes': city.extraction_nodes
                }
            }
            
            # Prepare proxy data
            proxy_info = {
                'indicators': {
                    'nodes': proxy_data.node_data,
                    'edges': {
                        f"{edge[0]}_{edge[1]}": indicators
                        for edge, indicators in proxy_data.edge_data.items()
                    }
                }
            }
            
            # Save all data for this city scenario
            self.data_manager.save_city_scenario(
                city_id=city_id,
                city_data=city_data,
                proxy_data=proxy_info,
                policy_result=policy_result.to_dict(),
                sim_result=result.to_dict(),
                max_resources=max_resources
            )
            
            # Calculate resource metrics
            resource_data = result.resources.to_dict()
            total_allocated = sum(resource_data['allocated'].values())
            total_used = sum(resource_data['used'].values())
            total_needed = sum(resource_data['needed'].values())
            
            # Calculate overall efficiency
            if total_used > 0:
                efficiency = sum(resource_data['effective_uses'].values()) / total_used
            else:
                efficiency = 0.0
            
            # Update summary with this city's results
            self.data_manager.update_experiment_summary({
                'success_rate': 1.0 if result.success else 0.0,
                'avg_path_length': result.path_length,
                'avg_time': result.time_taken,
                'resource_usage': {
                    'avg_allocated': total_allocated,
                    'avg_used': total_used,
                    'avg_needed': total_needed,
                    'efficiency': efficiency
                }
            })
        
        return result, city, proxy_data 