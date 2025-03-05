import networkx as nx
from typing import Dict, List, Literal
import pandas as pd
import random

from public.lib.interfaces import CityGraph, ProxyData, PolicyResult
from public.student_code.convert_to_df import convert_edge_data_to_df, convert_node_data_to_df

class EvacuationPolicy:
    """
    Tu implementación de la política de evacuación.
    Esta es la clase que necesitas implementar para resolver el problema de evacuación.
    """
    
    def __init__(self):
        """Inicializa tu política de evacuación"""
        self.policy_type = "policy_1"  # Política por defecto
        
    def set_policy(self, policy_type: Literal["policy_1", "policy_2", "policy_3", "policy_4"]):
        """
        Selecciona la política a utilizar
        Args:
            policy_type: Tipo de política a utilizar
                - "policy_1": Política básica sin uso de proxies
                - "policy_2": Política usando proxies y sus descripciones
                - "policy_3": Política usando datos de simulaciones previas
                - "policy_4": Política personalizada
        """
        self.policy_type = policy_type
    
    def plan_evacuation(self, city: CityGraph, proxy_data: ProxyData, 
                       max_resources: int) -> PolicyResult:
        """
        Planifica la ruta de evacuación y la asignación de recursos.
        
        Args:
            city: El layout de la ciudad
                 - city.graph: Grafo NetworkX con el layout de la ciudad
                 - city.starting_node: Tu posición inicial
                 - city.extraction_nodes: Lista de puntos de extracción posibles
                 
            proxy_data: Información sobre el ambiente
                 - proxy_data.node_data[node_id]: Dict con indicadores de nodos
                 - proxy_data.edge_data[(node1,node2)]: Dict con indicadores de aristas
                 
            max_resources: Máximo total de recursos que puedes asignar
            
        Returns:
            PolicyResult con:
            - path: List[int] - Lista de IDs de nodos formando tu ruta de evacuación
            - resources: Dict[str, int] - Cuántos recursos de cada tipo llevar:
                       {'explosives': x, 'ammo': y, 'radiation_suits': z}
                       donde x + y + z <= max_resources
        """
        # print(f'City graph: {city.graph} \n')
        # print(f'City starting_node: {city.starting_node}\n')
        # print(f'City extraction_nodes: {city.extraction_nodes}\n')
        # print(f'Proxy node_data: {proxy_data.node_data} \n \n')
        # print(f'Proxy edge_data: {proxy_data.edge_data} \n \n')
        # print(f'Max Resources: {max_resources} \n \n')
        
        
        self.policy_type = "policy_3" # TODO: Cambiar a "policy_2" para probar la política 2, y asi sucesivamente
        
        if self.policy_type == "policy_1":
            return self._policy_1(city, max_resources)
        elif self.policy_type == "policy_2":
            return self._policy_2(city, proxy_data, max_resources)
        elif self.policy_type == "policy_3":
            return self._policy_3(city, proxy_data, max_resources)
        else:  # policy_4
            return self._policy_4(city, proxy_data, max_resources)
    
    def _policy_1(self, city: CityGraph, max_resources: int) -> PolicyResult:
        """
        Política 1 Mejorada: Estrategia básica con selección inteligente del nodo de extracción
        y asignación de recursos basada en la longitud de la ruta.
        Si no se puede llegar a ningún nodo de extracción, no se asignan recursos.
        """
        # Paso 1: Encontrar el nodo de extracción más cercano
        shortest_path_length = float('inf')  # Inicializar con un valor grande
        best_target = None
        best_path = None

        for target in city.extraction_nodes:
            try:
                path = nx.shortest_path(city.graph, city.starting_node, target, weight='weight')
                path_length = nx.shortest_path_length(city.graph, city.starting_node, target, weight='weight')
                
                # Seleccionar el nodo de extracción con la ruta más corta
                if path_length < shortest_path_length:
                    shortest_path_length = path_length
                    best_target = target
                    best_path = path
            except nx.NetworkXNoPath:
                continue  # Si no hay camino, ignorar este nodo de extracción

        # Paso 2: Verificar si se encontró un camino válido
        if best_path is None:
            # Si no hay camino a ningún nodo de extracción, no asignar recursos
            return PolicyResult(path=[city.starting_node], resources={
                'explosives': 0,
                'ammo': 0,
                'radiation_suits': 0
            })

        # Paso 3: Asignar recursos de manera más inteligente
        # - Más "radiation_suits" si la ruta es larga
        # - Más "explosives" si hay muchos obstáculos (aquí asumimos que no tenemos datos de obstáculos)
        # - Más "ammo" si la ruta es peligrosa (aquí asumimos que no tenemos datos de peligro)
        if shortest_path_length > 10:  # Si la ruta es larga
            resources = {
                'explosives': max_resources // 4,
                'ammo': max_resources // 4,
                'radiation_suits': max_resources // 2
            }
        else:  # Si la ruta es corta
            resources = {
                'explosives': max_resources // 3,
                'ammo': max_resources // 3,
                'radiation_suits': max_resources // 3
        }
        return PolicyResult(best_path, resources)
    
    def _policy_2(self, city: CityGraph, proxy_data: ProxyData, max_resources: int) -> PolicyResult:
        """
        Política 2 Mejorada: Estrategia usando proxies y sus descripciones.
        Combina con la Política 1 si no se encuentra una ruta válida.
        """
        # Convertir los datos de nodos y aristas en DataFrames
        proxy_data_nodes_df = convert_node_data_to_df(proxy_data.node_data)
        proxy_data_edges_df = convert_edge_data_to_df(proxy_data.edge_data)
        
        # Verificar si las columnas 'node1' y 'node2' están presentes
        if 'node1' not in proxy_data_edges_df.columns or 'node2' not in proxy_data_edges_df.columns:
            # Si no están, generarlas a partir de las claves del diccionario
            edges = list(proxy_data.edge_data.keys())
            proxy_data_edges_df['node1'] = [edge[0] for edge in edges]
            proxy_data_edges_df['node2'] = [edge[1] for edge in edges]
        
        # Definir umbrales de seguridad más relajados para nodos
        unsafe_nodes = proxy_data_nodes_df[
            (proxy_data_nodes_df['seismic_activity'] > 0.8) |  # Actividad sísmica muy alta
            (proxy_data_nodes_df['radiation_readings'] > 0.7) |  # Radiación muy alta
            (proxy_data_nodes_df['population_density'] > 0.8) |  # Densidad poblacional muy alta
            (proxy_data_nodes_df['structural_integrity'] < 0.2)  # Integridad estructural muy baja
        ].index.tolist()
        
        # Definir rutas peligrosas con umbrales más relajados
        unsafe_edges = proxy_data_edges_df[
            (proxy_data_edges_df['structural_damage'] > 0.8) |  # Daño estructural muy alto
            (proxy_data_edges_df['debris_density'] > 0.8) |  # Densidad de escombros muy alta
            (proxy_data_edges_df['signal_interference'] > 0.9)  # Interferencia de señal muy alta
        ][['node1', 'node2']].values.tolist()
        
        # Crear un grafo seguro sin nodos inseguros ni rutas peligrosas
        safe_graph = city.graph.copy()
        safe_graph.remove_nodes_from(unsafe_nodes)
        safe_graph.remove_edges_from(unsafe_edges)
        
        # Verificar si el nodo de inicio está en el grafo seguro
        if city.starting_node not in safe_graph:
            # Si no está, recurrir a la Política 1
            return self._policy_1(city, max_resources)
        
        # Definir objetivo (supervivientes con buena conectividad)
        possible_targets = proxy_data_nodes_df[
            (proxy_data_nodes_df['emergency_calls'] > 0.5) &  # Llamadas de emergencia moderadas
            (proxy_data_nodes_df['thermal_readings'].between(0.2, 0.8)) &  # Lecturas térmicas moderadas
            (proxy_data_nodes_df['signal_strength'] > 0.4)  # Fuerza de señal moderada
        ].index.tolist()
        
        # Seleccionar el objetivo más cercano en el grafo seguro
        target = None
        shortest_path_length = float('inf')
        for possible_target in possible_targets:
            if possible_target in safe_graph:
                try:
                    path_length = nx.shortest_path_length(safe_graph, city.starting_node, possible_target, weight='weight')
                    if path_length < shortest_path_length:
                        shortest_path_length = path_length
                        target = possible_target
                except nx.NetworkXNoPath:
                    continue
        
        # Si no hay objetivos válidos, recurrir a la Política 1
        if target is None:
            return self._policy_1(city, max_resources)
        
        # Buscar camino seguro
        try:
            path = nx.shortest_path(safe_graph, city.starting_node, target, weight='weight')
        except nx.NetworkXNoPath:
            # Si no hay camino, recurrir a la Política 1
            return self._policy_1(city, max_resources)
        
        # Distribución de recursos basada en la longitud de la ruta
        if shortest_path_length > 10:  # Si la ruta es larga
            resources = {
                'explosives': max_resources // 4,
                'ammo': max_resources // 4,
                'radiation_suits': max_resources // 2
            }
        else:  # Si la ruta es corta
            resources = {
                'explosives': max_resources // 3,
                'ammo': max_resources // 3,
                'radiation_suits': max_resources // 3
            }
        
        return PolicyResult(path, resources)
    
    def _policy_3(self, city: CityGraph, proxy_data: ProxyData, max_resources: int) -> PolicyResult:
        """
        Política 3: Estrategia usando datos de simulaciones previas.
        Utiliza estadísticas básicas de simulaciones anteriores para mejorar la toma de decisiones.

        - Usa datos de simulaciones previas para elegir mejores rutas.
        - Evita caminos que han fallado en el pasado.
        - Distribuye los recursos basándose en estadísticas.
        - NO usa modelos de machine learning.
        """
        
        # Supongamos que existe una estructura `self.simulation_history` con datos previos
        # Cada entrada podría ser: {'path': [...], 'success': True/False, 'resources_used': {...}}

        if hasattr(self, 'simulation_history') and self.simulation_history:
            # Contar el número de veces que un nodo estuvo en una misión exitosa
            node_success_count = {}
            for sim in self.simulation_history:
                if sim['success']:
                    for node in sim['path']:
                        node_success_count[node] = node_success_count.get(node, 0) + 1

            # Ordenar nodos de extracción por frecuencia de éxito
            sorted_targets = sorted(city.extraction_nodes, key=lambda x: node_success_count.get(x, 0), reverse=True)
        else:
            # Si no hay datos previos, elegir la primera opción
            sorted_targets = city.extraction_nodes

        # Intentar encontrar la mejor ruta hacia el nodo más exitoso
        target = sorted_targets[0] if sorted_targets else city.starting_node

        try:
            path = nx.shortest_path(city.graph, city.starting_node, target, weight='weight')
        except nx.NetworkXNoPath:
            path = [city.starting_node]

        # Distribuir recursos según estadísticas previas
        if hasattr(self, 'simulation_history') and self.simulation_history:
            avg_explosives = sum(sim['resources_used'].get('explosives', 0) for sim in self.simulation_history) / len(self.simulation_history)
            avg_ammo = sum(sim['resources_used'].get('ammo', 0) for sim in self.simulation_history) / len(self.simulation_history)
            avg_suits = sum(sim['resources_used'].get('radiation_suits', 0) for sim in self.simulation_history) / len(self.simulation_history)

            # Ajustar recursos según el uso promedio anterior
            total_avg = avg_explosives + avg_ammo + avg_suits
            if total_avg > 0:
                resources = {
                    'explosives': int((avg_explosives / total_avg) * max_resources),
                    'ammo': int((avg_ammo / total_avg) * max_resources),
                    'radiation_suits': int((avg_suits / total_avg) * max_resources)
                }
            else:
                # Distribución estándar si no hay datos previos
                resources = {
                    'explosives': max_resources // 3,
                    'ammo': max_resources // 3,
                    'radiation_suits': max_resources // 3
                }
        else:
            # Distribución estándar si no hay datos previos
            resources = {
                'explosives': max_resources // 3,
                'ammo': max_resources // 3,
                'radiation_suits': max_resources // 3
            }

        return PolicyResult(path, resources)

    def _policy_4(self, city: CityGraph, proxy_data: ProxyData, max_resources: int) -> PolicyResult:
        """
        Política 4: Estrategia controlada de mitigación de riesgos con recursos ajustados.
        """
        proxy_data_nodes_df = convert_node_data_to_df(proxy_data.node_data)
        proxy_data_edges_df = convert_edge_data_to_df(proxy_data.edge_data)

        # Verificar qué columnas existen en los datos de nodos
        available_columns = proxy_data_nodes_df.columns

        # Definir los umbrales para cada tipo de riesgo
        max_seismic = 0.6
        max_radiation = 0.7
        max_movement = 0.8

        # Crear un valor de "riesgo" ponderado para cada nodo
        node_risks = {}
        for node in proxy_data_nodes_df.index:
            seismic_risk = proxy_data_nodes_df.loc[node, 'seismic_activity'] if 'seismic_activity' in available_columns else 0
            radiation_risk = proxy_data_nodes_df.loc[node, 'radiation_readings'] if 'radiation_readings' in available_columns else 0
            movement_risk = proxy_data_nodes_df.loc[node, 'movement_sightings'] if 'movement_sightings' in available_columns else 0
            
            # El riesgo es la suma ponderada de estos factores (puedes ajustar los pesos)
            total_risk = (seismic_risk * 0.3) + (radiation_risk * 0.4) + (movement_risk * 0.3)
            node_risks[node] = min(total_risk, 1.0)  # Limitamos a 1.0 para evitar valores mayores

        # Ordenar los nodos por su riesgo
        sorted_risks = sorted(node_risks.items(), key=lambda x: x[1], reverse=True)

        # Elegir un nodo de extracción con el menor riesgo posible entre los nodos más bajos
        best_target = None
        for node, risk in sorted_risks:
            if risk < max_seismic and risk < max_radiation and risk < max_movement:
                best_target = node
                break

        if best_target is None:
            # Si todos los nodos tienen un riesgo alto, tomamos el nodo con el menor riesgo
            best_target = sorted_risks[0][0]

        print(f"Destino elegido: {best_target}")

        # Crear un grafo seguro eliminando los nodos de alto riesgo
        safe_graph = city.graph.copy()
        high_risk_nodes = [node for node, risk in node_risks.items() if risk > 0.7]
        safe_graph.remove_nodes_from(high_risk_nodes)

        # Generar un camino aleatorio pero limitado a los nodos de riesgo bajo
        path = [city.starting_node]
        while len(path) < 5:
            next_node = random.choice(list(safe_graph.neighbors(path[-1])))
            if next_node not in path:  # Evitar nodos repetidos
                path.append(next_node)

        print(f"Camino seleccionado: {path}")

        # Asignación de recursos
        resources = {
            'explosives': random.randint(0, max_resources // 3),
            'ammo': random.randint(0, max_resources // 3),
            'radiation_suits': random.randint(0, max_resources // 3)
        }

        # Asignación de más recursos a nodos con alto riesgo de radiación o sismos
        for node, risk in sorted_risks:
            if node in path:
                if risk > max_radiation:
                    resources['radiation_suits'] += 2  # Aumentar trajes de radiación
                elif risk > max_seismic:
                    resources['explosives'] += 2  # Aumentar explosivos en nodos de sismos

        print(f"Recursos asignados: {resources}")

        # Definir éxito basado en si la cantidad de recursos mitigó el riesgo
        total_risk = sum(node_risks[node] for node in path)
        resources_used = sum(resources.values())
        
        success_rate = max(0, min(1, (resources_used / total_risk) if total_risk > 0 else 1))

        # Resultado final
        print(f"Tasa de éxito: {success_rate}")
        return PolicyResult(path, resources)
