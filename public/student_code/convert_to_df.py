import pandas as pd

def convert_node_data_to_df(node_data):
    """
    Convert a node data dictionary into a pandas DataFrame.
    
    Parameters:
        node_data (dict): A dictionary where each key is a node identifier and the 
                          corresponding value is a dictionary of attributes.
                          Example:
                          {
                              0: {'attr1': value, 'attr2': value, ...},
                              1: {...},
                              ...
                          }
                          
    Returns:
        pd.DataFrame: A DataFrame with a column 'node' for node identifiers 
                      and columns for the attributes.
    """
    # Create DataFrame from dictionary and reset index to convert keys into a column.
    df = pd.DataFrame.from_dict(node_data, orient='index').reset_index()
    df = df.rename(columns={'index': 'node'})
    return df

def convert_edge_data_to_df(edge_data):
    """
    Convert an edge data dictionary into a pandas DataFrame.
    
    Parameters:
        edge_data (dict): A dictionary where each key is a tuple representing an edge 
                          (e.g., (node_1, node_2)) and the corresponding value is a 
                          dictionary of edge attributes.
                          Example:
                          {
                              (0, 1): {'attrA': value, 'attrB': value, ...},
                              (1, 2): {...},
                              ...
                          }
                          
    Returns:
        pd.DataFrame: A DataFrame with columns 'node_1', 'node_2', and the edge attributes.
    """
    records = []
    for edge, attributes in edge_data.items():
        if isinstance(edge, tuple) and len(edge) == 2:
            node_1, node_2 = edge
        else:
            # Handle cases where the edge key isn't a tuple of length 2
            node_1, node_2 = edge, None
        record = {'node_1': node_1, 'node_2': node_2}
        record.update(attributes)
        records.append(record)
    
    df = pd.DataFrame(records)
    return df

# ------------------------------
# Example usage with provided data:
# ------------------------------
if __name__ == "__main__":
    # Example node_data dictionary
    node_data = {
        0: {'seismic_activity': 0.8979664357940168, 'radiation_readings': 0.6515937220346393, 'population_density': 0.0, 'emergency_calls': 0.8533955644098227, 'thermal_readings': 0.3373309175424988, 'signal_strength': 0.18872250436811971, 'structural_integrity': 0.11182620113339772},
        1: {'seismic_activity': 0.6842277296396193, 'radiation_readings': 0.7233828882013326, 'population_density': 0.0, 'emergency_calls': 0.8758910883515296, 'thermal_readings': 0.34790467012731907, 'signal_strength': 0.26211537928961964, 'structural_integrity': 0.26138994875492927},
        2: {'seismic_activity': 1.0, 'radiation_readings': 1.0, 'population_density': 0.05519998230924897, 'emergency_calls': 0.8458096143928209, 'thermal_readings': 0.20642004878080755, 'signal_strength': 0.06823489376031767, 'structural_integrity': 0.0},
        3: {'seismic_activity': 0.6921965687172652, 'radiation_readings': 0.7661394714782737, 'population_density': 0.1123105623315708, 'emergency_calls': 0.8629355761596956, 'thermal_readings': 0.281087733058976, 'signal_strength': 0.21324180753093394, 'structural_integrity': 0.33290951794810875},
        4: {'seismic_activity': 0.5251037038508131, 'radiation_readings': 0.9004038912253598, 'population_density': 0.0, 'emergency_calls': 0.9122736268326301, 'thermal_readings': 0.252548321704587, 'signal_strength': 0.32206148219320935, 'structural_integrity': 0.5062312433871621}
    }
    
    # Example edge_data dictionary
    edge_data = {
        (0, 4): {'structural_damage': 0.9798801010280794, 'signal_interference': 0.6840565306961252, 'movement_sightings': 0.3518253685841467, 'debris_density': 0.9499437345082267, 'hazard_gradient': 0.2686628295964298},
        (0, 3): {'structural_damage': 0.9094232750849469, 'signal_interference': 0.38173744720546343, 'movement_sightings': 0.2881919637164742, 'debris_density': 0.9503773970996593, 'hazard_gradient': 0.0},
        (0, 1): {'structural_damage': 0.9127055412303914, 'signal_interference': 0.436131478436639, 'movement_sightings': 0.34404934260782905, 'debris_density': 0.8977843932468939, 'hazard_gradient': 0.09421567552272364},
        (0, 2): {'structural_damage': 1.0, 'signal_interference': 0.6424885832532324, 'movement_sightings': 0.1886329733357352, 'debris_density': 0.9843805495782487, 'hazard_gradient': 0.35787501324343},
        (1, 3): {'structural_damage': 0.8200317046571752, 'signal_interference': 0.48799998085129326, 'movement_sightings': 0.11508115919128972, 'debris_density': 0.7122479076942206, 'hazard_gradient': 0.0},
        (1, 2): {'structural_damage': 1.0, 'signal_interference': 0.8153629669403073, 'movement_sightings': 0.027234388710172676, 'debris_density': 0.9481556983829934, 'hazard_gradient': 0.28621132326769727},
        (1, 4): {'structural_damage': 0.48252556786896417, 'signal_interference': 0.6142960928320218, 'movement_sightings': 0.14207477467110957, 'debris_density': 0.6358283747461347, 'hazard_gradient': 0.3722749894493055},
        (2, 3): {'structural_damage': 0.9305678537099269, 'signal_interference': 0.7926945388796988, 'movement_sightings': 0.10031007339992616, 'debris_density': 1.0, 'hazard_gradient': 0.3565516816007065},
        (3, 4): {'structural_damage': 0.3001143792255887, 'signal_interference': 0.5050235902656031, 'movement_sightings': 0.1041588536745959, 'debris_density': 0.6938581990258571, 'hazard_gradient': 0.42622532272630786}
    }
    
    # Convert dictionaries to DataFrames
    node_df = convert_node_data_to_df(node_data)
    edge_df = convert_edge_data_to_df(edge_data)
    
    # Display the DataFrames
    print("Node DataFrame:")
    print(node_df.head())
    
    print("\nEdge DataFrame:")
    print(edge_df.head())
