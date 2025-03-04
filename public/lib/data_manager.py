import os
import json
import datetime
import uuid
from typing import Dict, Any

class DataManager:
    """Manages data storage for the simulation"""
    
    def __init__(self, policy_name: str):
        self.policy_name = policy_name
        self.base_dir = "data/policies"
        self.policy_dir = os.path.join(self.base_dir, policy_name)
        self.current_experiment = None
        
    def start_experiment(self, config: Dict[str, Any] = None) -> str:
        """Start a new experiment and create necessary directories"""
        # Generate experiment ID with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        exp_id = f"{timestamp}"
        
        # Create experiment directory structure
        exp_dir = os.path.join(self.policy_dir, "experiments", exp_id)
        os.makedirs(os.path.join(exp_dir, "cities"), exist_ok=True)
        os.makedirs(os.path.join(exp_dir, "visualizations"), exist_ok=True)
        
        # Save experiment metadata
        metadata = {
            "metadata": {
                "experiment_id": exp_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "configuration": config or {},
                "total_runs": 0
            },
            "overall_performance": {
                "success_rate": 0.0,
                "avg_path_length": 0.0,
                "avg_time": 0.0
            },
            "resource_usage": {
                "avg_allocated": 0.0,
                "avg_used": 0.0,
                "avg_needed": 0.0,
                "efficiency": 0.0
            }
        }
        
        with open(os.path.join(exp_dir, "core_metrics.json"), "w") as f:
            json.dump(metadata, f, indent=4)
            
        self.current_experiment = exp_id
        return exp_id
        
    def save_city_scenario(self, city_id: str, city_data: Dict, proxy_data: Dict, 
                          policy_result: Dict, sim_result: Dict, max_resources: int) -> str:
        """Save all data for a single city scenario"""
        if not self.current_experiment:
            raise ValueError("No active experiment")
            
        # Create directory for this city
        city_dir = os.path.join(
            self.policy_dir, "experiments",
            self.current_experiment, "cities",
            f"city_{city_id}"
        )
        os.makedirs(city_dir, exist_ok=True)
        
        # Save city definition (only layout and configuration)
        city_def = {
            "metadata": {
                "timestamp": datetime.datetime.now().isoformat(),
                "n_nodes": city_data['metadata']['n_nodes'],
                "max_resources": max_resources
            },
            "graph": city_data['graph'],
            "configuration": {
                "start_node": city_data['simulation']['start_node'],
                "extraction_nodes": city_data['simulation']['extraction_nodes']
            }
        }
        with open(os.path.join(city_dir, "definition.json"), "w") as f:
            json.dump(city_def, f, indent=4)
            
        # Save proxy data (what the team can observe)
        proxy_info = {
            "metadata": {
                "timestamp": datetime.datetime.now().isoformat()
            },
            "indicators": proxy_data['indicators']
        }
        with open(os.path.join(city_dir, "proxy_data.json"), "w") as f:
            json.dump(proxy_info, f, indent=4)
            
        # Save mission results (only observable outcomes)
        mission_results = {
            "metadata": {
                "timestamp": datetime.datetime.now().isoformat(),
                "solution_class": self.policy_name
            },
            "plan": {
                "path": policy_result['path'],
                "resources_allocated": policy_result['resources']
            },
            "outcome": {
                "success": sim_result['success'],
                "time_taken": sim_result['time_taken'],
                "path_length": sim_result['path_length'],
                "resources": {
                    "initial": policy_result['resources'],
                    "remaining": {
                        rt: policy_result['resources'][rt] - sim_result['resources']['used'][rt]
                        for rt in policy_result['resources']
                    }
                }
            },
            "events": {
                "chronological": sim_result.get('events',[]),#sim_result.events if hasattr(sim_result, 'events') else [],
                "resource_summary": {
                    rt: {
                        "allocated": sim_result['resources']['allocated'][rt],
                        "used": sim_result['resources']['used'][rt],
                        "needed": sim_result['resources']['needed'][rt],
                        "effective_uses": sim_result['resources']['effective_uses'][rt]
                    }
                    for rt in sim_result['resources']['allocated'].keys()
                }
            }
        }
        with open(os.path.join(city_dir, "mission_results.json"), "w") as f:
            json.dump(mission_results, f, indent=4)
            
        return city_dir
        
    def update_experiment_summary(self, metrics: Dict[str, float]):
        """Update the experiment summary with new metrics"""
        if not self.current_experiment:
            raise ValueError("No active experiment")
            
        summary_file = os.path.join(
            self.policy_dir, "experiments",
            self.current_experiment, "core_metrics.json"
        )
        
        with open(summary_file, "r") as f:
            summary = json.load(f)
            
        # Update running averages
        current_n = summary["metadata"]["total_runs"]
        new_n = current_n + 1
        
        # Update basic metrics
        for key in ['success_rate', 'avg_path_length', 'avg_time']:
            if key in metrics:
                current_val = summary["overall_performance"][key]
                new_val = metrics[key]
                summary["overall_performance"][key] = (
                    (current_val * current_n + new_val) / new_n
                )
        
        # Update resource usage
        if 'resource_usage' in metrics:
            for key in ['avg_allocated', 'avg_used', 'avg_needed', 'efficiency']:
                if key in metrics['resource_usage']:
                    current_val = summary["resource_usage"][key]
                    new_val = metrics['resource_usage'][key]
                    summary["resource_usage"][key] = (
                        (current_val * current_n + new_val) / new_n
                    )
        
        summary["metadata"]["total_runs"] = new_n
        
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=4)
            
    def save_policy_metadata(self):
        """Save policy metadata"""
        metadata_file = os.path.join(self.policy_dir, "metadata.json")
        
        metadata = {
            "policy_name": self.policy_name,
            "policy_class": self.policy_name,
            "source_file": "solution.py",
            "created_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "description": "Student implementation of evacuation policy"
        }
        
        os.makedirs(os.path.dirname(metadata_file), exist_ok=True)
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=4) 