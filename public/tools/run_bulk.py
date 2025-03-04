import random
import os
import json
from typing import List, Dict, Any, Tuple
import datetime
import numpy as np
import pandas as pd

from public.lib.interfaces import SimulationResult, ResourceTypes
from public.tools.simulator import Simulator
from public.lib.data_manager import DataManager

class BulkRunner:
    """Runs multiple simulations with different parameters"""
    
    def __init__(self, policy_name: str, base_seed: int = None):
        self.policy_name = policy_name
        self.base_seed = base_seed or random.randint(0, 1000000)
        
    def run_batch(self, policy, config: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """
        Run a batch of simulations with different parameters
        
        Args:
            policy: Policy object with plan_evacuation method
            config: Dict with:
                - node_range: Dict with min and max node counts
                - n_runs: int - Number of runs
                
        Returns:
            Tuple of (results dict, experiment_id)
        """
        random.seed(self.base_seed)
        
        # Initialize simulator
        simulator = Simulator(
            policy_name=self.policy_name,
            n_nodes=30,  # Will be overridden
            seed=self.base_seed
        )
        
        # Start new experiment
        experiment_id = simulator.data_manager.start_experiment(config)
        exp_dir = os.path.join('data', 'policies', self.policy_name, 'experiments', experiment_id)
        
        # Initialize raw data collection
        raw_data = {
            'runs': [],  # List to store raw data from each run
            'by_size': {}  # Group runs by city size
        }
        
        # Run simulations and collect raw data
        for run in range(config['n_runs']):
            # Generate random node count for this run
            n_nodes = random.randint(config['node_range']['min'], 
                                   config['node_range']['max'])
            
            # Initialize size data if not seen before
            if n_nodes not in raw_data['by_size']:
                raw_data['by_size'][n_nodes] = []
            
            # Configure simulator for this run
            simulator.n_nodes = n_nodes
            simulator.seed = self.base_seed + run
            
            # Run simulation
            result, city, proxy_data = simulator.run_simulation(policy)
            
            # Get policy result
            max_resources = simulator.city_gen.calculate_max_resources(n_nodes)
            policy_result = policy.plan_evacuation(city, proxy_data, max_resources)
            
            # Store raw run data
            run_data = {
                'run_id': run,
                'city_size': n_nodes,
                'success': result.success,
                'path_length': result.path_length,
                'time_taken': result.time_taken,
                'resources': result.resources.to_dict(),
                'proxy_data': {
                    'nodes': {
                        str(node_id): {
                            k: float(v) for k, v in indicators.items()
                        }
                        for node_id, indicators in proxy_data.node_data.items()
                    },
                    'edges': {
                        str(edge_key): {
                            k: float(v) for k, v in indicators.items()
                        }
                        for edge_key, indicators in proxy_data.edge_data.items()
                    }
                },
                'policy_allocation': policy_result.resources
            }
            
            raw_data['runs'].append(run_data)
            raw_data['by_size'][n_nodes].append(run_data)
        
        # Save raw data
        with open(os.path.join(exp_dir, 'raw_data.json'), 'w') as f:
            json.dump(raw_data, f, indent=4)
        
        # Compute core metrics
        core_metrics = {
            'metadata': {
                'policy_name': self.policy_name,
                'experiment_id': experiment_id,
                'timestamp': datetime.datetime.now().isoformat(),
                'config': config,
                'total_runs': len(raw_data['runs'])
            },
            'overall_performance': {
                'success_rate': sum(1 for r in raw_data['runs'] if r['success']) / len(raw_data['runs']),
                'avg_time': sum(r['time_taken'] for r in raw_data['runs']) / len(raw_data['runs']),
                'avg_path_length': sum(r['path_length'] for r in raw_data['runs']) / len(raw_data['runs']),
                'resources_allocated': sum(sum(r['resources']['allocated'].values()) for r in raw_data['runs']) / len(raw_data['runs']),
                'resources_used': sum(sum(r['resources']['used'].values()) for r in raw_data['runs']) / len(raw_data['runs']),
                'resource_efficiency': sum(sum(r['resources']['used'].values()) / sum(r['resources']['allocated'].values()) 
                                        if sum(r['resources']['allocated'].values()) > 0 else 0 
                                        for r in raw_data['runs']) / len(raw_data['runs']),
                'std_time': np.std([r['time_taken'] for r in raw_data['runs']]),
                'std_path_length': np.std([r['path_length'] for r in raw_data['runs']]),
                'std_resources_allocated': np.std([sum(r['resources']['allocated'].values()) for r in raw_data['runs']]),
                'std_resources_used': np.std([sum(r['resources']['used'].values()) for r in raw_data['runs']])
            },
            'resource_details': {
                rt: {
                    'avg_allocated': np.mean([r['resources']['allocated'][rt] for r in raw_data['runs']]),
                    'std_allocated': np.std([r['resources']['allocated'][rt] for r in raw_data['runs']]),
                    'avg_used': np.mean([r['resources']['used'][rt] for r in raw_data['runs']]),
                    'std_used': np.std([r['resources']['used'][rt] for r in raw_data['runs']]),
                    'efficiency': np.mean([r['resources']['used'][rt] / r['resources']['allocated'][rt] 
                                        if r['resources']['allocated'][rt] > 0 else 0 
                                        for r in raw_data['runs']])
                }
                for rt in ResourceTypes.all_types()
            },
            'proxy_metrics': {
                'nodes': {
                    indicator: {
                        'mean': np.mean([
                            np.mean([float(node[indicator]) 
                                   for node in r['proxy_data']['nodes'].values()])
                            for r in raw_data['runs']
                        ]),
                        'std': np.std([
                            np.mean([float(node[indicator]) 
                                   for node in r['proxy_data']['nodes'].values()])
                            for r in raw_data['runs']
                        ])
                    }
                    for indicator in next(iter(raw_data['runs'][0]['proxy_data']['nodes'].values())).keys()
                },
                'edges': {
                    indicator: {
                        'mean': np.mean([
                            np.mean([float(edge[indicator]) 
                                   for edge in r['proxy_data']['edges'].values()])
                            for r in raw_data['runs']
                        ]),
                        'std': np.std([
                            np.mean([float(edge[indicator]) 
                                   for edge in r['proxy_data']['edges'].values()])
                            for r in raw_data['runs']
                        ])
                    }
                    for indicator in next(iter(raw_data['runs'][0]['proxy_data']['edges'].values())).keys()
                }
            },
            'by_city_size': {}
        }
        
        # Compute metrics by city size
        for size, runs in raw_data['by_size'].items():
            core_metrics['by_city_size'][size] = {
                'n_runs': len(runs),
                'success_rate': sum(1 for r in runs if r['success']) / len(runs),
                'avg_time': sum(r['time_taken'] for r in runs) / len(runs),
                'avg_path_length': sum(r['path_length'] for r in runs) / len(runs),
                'resources_allocated': sum(sum(r['resources']['allocated'].values()) for r in runs) / len(runs),
                'resources_used': sum(sum(r['resources']['used'].values()) for r in runs) / len(runs),
                'resource_efficiency': sum(sum(r['resources']['used'].values()) / sum(r['resources']['allocated'].values()) 
                                        if sum(r['resources']['allocated'].values()) > 0 else 0 
                                        for r in runs) / len(runs),
                'std_time': np.std([r['time_taken'] for r in runs]),
                'std_path_length': np.std([r['path_length'] for r in runs]),
                'std_resources_allocated': np.std([sum(r['resources']['allocated'].values()) for r in runs]),
                'std_resources_used': np.std([sum(r['resources']['used'].values()) for r in runs]),
                'resource_details': {
                    rt: {
                        'avg_allocated': np.mean([r['resources']['allocated'][rt] for r in runs]),
                        'std_allocated': np.std([r['resources']['allocated'][rt] for r in runs]),
                        'avg_used': np.mean([r['resources']['used'][rt] for r in runs]),
                        'std_used': np.std([r['resources']['used'][rt] for r in runs]),
                        'efficiency': np.mean([r['resources']['used'][rt] / r['resources']['allocated'][rt] 
                                            if r['resources']['allocated'][rt] > 0 else 0 
                                            for r in runs])
                    }
                    for rt in ResourceTypes.all_types()
                },
                'proxy_metrics': {
                    'nodes': {
                        indicator: {
                            'mean': np.mean([
                                np.mean([float(node[indicator]) 
                                       for node in r['proxy_data']['nodes'].values()])
                                for r in runs
                            ]),
                            'std': np.std([
                                np.mean([float(node[indicator]) 
                                       for node in r['proxy_data']['nodes'].values()])
                                for r in runs
                            ])
                        }
                        for indicator in next(iter(runs[0]['proxy_data']['nodes'].values())).keys()
                    },
                    'edges': {
                        indicator: {
                            'mean': np.mean([
                                np.mean([float(edge[indicator]) 
                                       for edge in r['proxy_data']['edges'].values()])
                                for r in runs
                            ]),
                            'std': np.std([
                                np.mean([float(edge[indicator]) 
                                       for edge in r['proxy_data']['edges'].values()])
                                for r in runs
                            ])
                        }
                        for indicator in next(iter(runs[0]['proxy_data']['edges'].values())).keys()
                    }
                }
            }

        # Save core metrics
        with open(os.path.join(exp_dir, 'core_metrics.json'), 'w') as f:
            json.dump(core_metrics, f, indent=4)

        # Create CSV version of core metrics
        def flatten_dict(d, parent_key='', sep='_'):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)

        # Flatten and save aggregated metrics
        flattened_metrics = flatten_dict(core_metrics)
        df = pd.DataFrame([flattened_metrics])
        df.to_csv(os.path.join(exp_dir, 'core_metrics.csv'), index=False)

        # Save individual city metrics
        for size, runs in raw_data['by_size'].items():
            for run in runs:
                city_metrics = {
                    'metadata': {
                        'policy_name': self.policy_name,
                        'experiment_id': experiment_id,
                        'city_size': size,
                        'run_id': run['run_id']
                    },
                    'performance': {
                        'success': run['success'],
                        'time_taken': run['time_taken'],
                        'path_length': run['path_length']
                    },
                    'resource_details': {
                        rt: {
                            'allocated': run['resources']['allocated'][rt],
                            'used': run['resources']['used'][rt],
                            'efficiency': run['resources']['used'][rt] / run['resources']['allocated'][rt]
                                        if run['resources']['allocated'][rt] > 0 else 0
                        }
                        for rt in ResourceTypes.all_types()
                    },
                    'proxy_metrics': {
                        'nodes': {
                            indicator: {
                                'mean': np.mean([float(node[indicator]) 
                                               for node in run['proxy_data']['nodes'].values()]),
                                'std': np.std([float(node[indicator]) 
                                             for node in run['proxy_data']['nodes'].values()])
                            }
                            for indicator in run['proxy_data']['nodes'][next(iter(run['proxy_data']['nodes']))].keys()
                        },
                        'edges': {
                            indicator: {
                                'mean': np.mean([float(edge[indicator]) 
                                               for edge in run['proxy_data']['edges'].values()]),
                                'std': np.std([float(edge[indicator]) 
                                             for edge in run['proxy_data']['edges'].values()])
                            }
                            for indicator in run['proxy_data']['edges'][next(iter(run['proxy_data']['edges']))].keys()
                        }
                    }
                }
                
                # Save JSON
                city_metrics_path = os.path.join(exp_dir, 'cities', f'city_{run["run_id"]}_metrics.json')
                os.makedirs(os.path.dirname(city_metrics_path), exist_ok=True)
                with open(city_metrics_path, 'w') as f:
                    json.dump(city_metrics, f, indent=4)
                
                # Save CSV
                flattened_city_metrics = flatten_dict(city_metrics)
                df = pd.DataFrame([flattened_city_metrics])
                df.to_csv(city_metrics_path.replace('.json', '.csv'), index=False)
        
        # Compute resource metrics
        resource_metrics = {
            'overall': {
                rt: {
                    'avg_allocated': sum(r['resources']['allocated'][rt] for r in raw_data['runs']) / len(raw_data['runs']),
                    'avg_used': sum(r['resources']['used'][rt] for r in raw_data['runs']) / len(raw_data['runs']),
                    'avg_needed': sum(r['resources']['needed'][rt] for r in raw_data['runs']) / len(raw_data['runs']),
                    'efficiency': sum(r['resources']['efficiency'][rt] for r in raw_data['runs']) / len(raw_data['runs'])
                }
                for rt in ResourceTypes.all_types()
            },
            'by_city_size': {
                size: {
                    rt: {
                        'avg_allocated': sum(r['resources']['allocated'][rt] for r in runs) / len(runs),
                        'avg_used': sum(r['resources']['used'][rt] for r in runs) / len(runs),
                        'avg_needed': sum(r['resources']['needed'][rt] for r in runs) / len(runs),
                        'efficiency': sum(r['resources']['efficiency'][rt] for r in runs) / len(runs)
                    }
                    for rt in ResourceTypes.all_types()
                }
                for size, runs in raw_data['by_size'].items()
            },
            'analysis': {
                'most_used_resource': max(
                    ((rt, sum(r['resources']['used'][rt] for r in raw_data['runs']))
                     for rt in ResourceTypes.all_types()),
                    key=lambda x: x[1]
                )[0],
                'most_needed_resource': max(
                    ((rt, sum(r['resources']['needed'][rt] for r in raw_data['runs']))
                     for rt in ResourceTypes.all_types()),
                    key=lambda x: x[1]
                )[0]
            }
        }
        
        # Save resource metrics
        with open(os.path.join(exp_dir, 'resource_metrics.json'), 'w') as f:
            json.dump(resource_metrics, f, indent=4)
        
        # Compute environmental metrics
        # First, get the indicator names from the first run
        first_run = raw_data['runs'][0]
        first_node = next(iter(first_run['proxy_data']['nodes'].values()))
        first_edge = next(iter(first_run['proxy_data']['edges'].values()))
        node_indicators = list(first_node.keys())
        edge_indicators = list(first_edge.keys())
        
        env_metrics = {
            'overall': {
                'nodes': {
                    indicator: sum(
                        sum(
                            node[indicator]
                            for node in r['proxy_data']['nodes'].values()
                        ) / len(r['proxy_data']['nodes'])
                        for r in raw_data['runs']
                    ) / len(raw_data['runs'])
                    for indicator in node_indicators
                },
                'edges': {
                    indicator: sum(
                        sum(
                            edge[indicator]
                            for edge in r['proxy_data']['edges'].values()
                        ) / len(r['proxy_data']['edges'])
                        for r in raw_data['runs']
                    ) / len(raw_data['runs'])
                    for indicator in edge_indicators
                }
            },
            'by_city_size': {
                size: {
                    'nodes': {
                        indicator: sum(
                            sum(
                                node[indicator]
                                for node in r['proxy_data']['nodes'].values()
                            ) / len(r['proxy_data']['nodes'])
                            for r in runs
                        ) / len(runs)
                        for indicator in node_indicators
                    },
                    'edges': {
                        indicator: sum(
                            sum(
                                edge[indicator]
                                for edge in r['proxy_data']['edges'].values()
                            ) / len(r['proxy_data']['edges'])
                            for r in runs
                        ) / len(runs)
                        for indicator in edge_indicators
                    }
                }
                for size, runs in raw_data['by_size'].items()
            }
        }
        
        # Add correlations with success
        env_metrics['correlations'] = {
            'nodes': {
                indicator: self.calculate_correlation(
                    [
                        (
                            sum(
                                node[indicator]
                                for node in r['proxy_data']['nodes'].values()
                            ) / len(r['proxy_data']['nodes']),
                            1 if r['success'] else 0
                        )
                        for r in raw_data['runs']
                    ]
                )
                for indicator in node_indicators
            },
            'edges': {
                indicator: self.calculate_correlation(
                    [
                        (
                            sum(
                                edge[indicator]
                                for edge in r['proxy_data']['edges'].values()
                            ) / len(r['proxy_data']['edges']),
                            1 if r['success'] else 0
                        )
                        for r in raw_data['runs']
                    ]
                )
                for indicator in edge_indicators
            }
        }
        
        # Save environmental metrics
        with open(os.path.join(exp_dir, 'environmental_metrics.json'), 'w') as f:
            json.dump(env_metrics, f, indent=4)
        
        return {
            'core_metrics': core_metrics,
            'resource_metrics': resource_metrics,
            'environmental_metrics': env_metrics,
            'raw_data': raw_data
        }, experiment_id

    def calculate_correlation(self, data_pairs: List[Tuple[float, float]]) -> float:
        """
        Calculate correlation coefficient between two series of values.
        Handles edge cases and numerical instabilities.
        
        Args:
            data_pairs: List of (x, y) value pairs to correlate
            
        Returns:
            Correlation coefficient between -1 and 1, or 0 for invalid/insufficient data
        """
        if len(data_pairs) < 2:  # Need at least 2 points for correlation
            return 0.0
        
        x_values = np.array([x for x, _ in data_pairs])
        y_values = np.array([y for _, y in data_pairs])
        
        # Check for constant values (zero variance)
        if np.all(x_values == x_values[0]) or np.all(y_values == y_values[0]):
            return 0.0
            
        try:
            # Calculate correlation with proper error handling
            with np.errstate(divide='ignore', invalid='ignore'):
                correlation = np.corrcoef(x_values, y_values)[0, 1]
                
            # Handle NaN and inf values
            if np.isnan(correlation) or np.isinf(correlation):
                return 0.0
                
            return float(correlation)
        except Exception as e:
            print(f"Warning: Error calculating correlation: {e}")
            return 0.0

    def compute_summary_statistics(self, raw_data: Dict) -> Dict:
        """
        Compute comprehensive summary statistics for key metrics.
        
        Returns:
            Dict containing summary statistics for key performance indicators
        """
        runs = raw_data['runs']
        
        def compute_stats(values):
            """Compute basic statistics for a list of values"""
            values = np.array(values)
            return {
                'mean': float(np.mean(values)),
                'std': float(np.std(values)),
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'median': float(np.median(values))
            }
        
        # Core performance metrics
        success_rates = [1 if r['success'] else 0 for r in runs]
        times = [r['time_taken'] for r in runs]
        path_lengths = [r['path_length'] for r in runs]
        
        # Resource usage metrics
        resource_usage = {
            rt: {
                'allocated': [r['resources']['allocated'][rt] for r in runs],
                'used': [r['resources']['used'][rt] for r in runs],
                'efficiency': [r['resources']['efficiency'][rt] for r in runs]
            }
            for rt in ResourceTypes.all_types()
        }
        
        # Compute overall resource efficiency
        total_used = sum(sum(r['resources']['used'][rt] for rt in ResourceTypes.all_types()) for r in runs)
        total_allocated = sum(sum(r['resources']['allocated'][rt] for rt in ResourceTypes.all_types()) for r in runs)
        overall_efficiency = total_used / total_allocated if total_allocated > 0 else 0
        
        # Success rate by city size
        size_success = {
            size: sum(1 for r in size_runs if r['success']) / len(size_runs)
            for size, size_runs in raw_data['by_size'].items()
        }
        
        return {
            'performance': {
                'success_rate': compute_stats(success_rates),
                'time': compute_stats(times),
                'path_length': compute_stats(path_lengths)
            },
            'resources': {
                rt: {
                    metric: compute_stats(values)
                    for metric, values in metrics.items()
                }
                for rt, metrics in resource_usage.items()
            },
            'overall_resource_efficiency': overall_efficiency,
            'success_by_size': size_success,
            'total_runs': len(runs),
            'city_sizes': list(raw_data['by_size'].keys())
        }

    def format_summary_table(self, summary: Dict) -> str:
        """Format summary statistics into a readable table string"""
        lines = []
        
        # Header
        lines.append("\nBenchmark Summary")
        lines.append("=" * 80)
        
        # Basic information
        lines.append(f"Total Runs: {summary['total_runs']}")
        lines.append(f"City Sizes: {', '.join(map(str, sorted(summary['city_sizes'])))}")
        lines.append("-" * 80)
        
        # Core Performance Metrics
        lines.append("\nCore Performance Metrics:")
        perf = summary['performance']
        metrics = [
            ('Success Rate', perf['success_rate'], '%'),
            ('Time', perf['time'], 'units'),
            ('Path Length', perf['path_length'], 'units')
        ]
        
        for name, stats, unit in metrics:
            lines.append(f"{name:15} | Mean: {stats['mean']:6.2f} ± {stats['std']:5.2f} {unit:5} | "
                       f"Range: [{stats['min']:6.2f}, {stats['max']:6.2f}]")
        
        # Resource Usage
        lines.append("\nResource Usage:")
        for rt, metrics in summary['resources'].items():
            lines.append(f"\n{rt.replace('_', ' ').title()}:")
            lines.append(f"  Efficiency: {metrics['efficiency']['mean']*100:6.2f}% ± {metrics['efficiency']['std']*100:5.2f}%")
            lines.append(f"  Usage Rate: {metrics['used']['mean']:6.2f} / {metrics['allocated']['mean']:6.2f} "
                       f"({metrics['used']['mean']/metrics['allocated']['mean']*100 if metrics['allocated']['mean'] > 0 else 0:5.1f}%)")
        
        # Success by City Size
        lines.append("\nSuccess Rate by City Size:")
        for size, rate in sorted(summary['success_by_size'].items()):
            lines.append(f"  Size {size:2d}: {rate*100:6.2f}%")
        
        return "\n".join(lines) 