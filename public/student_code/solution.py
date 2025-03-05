import networkx as nx
from typing import Dict, List, Literal

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
        
        
        self.policy_type = "policy_4" # TODO: Cambiar a "policy_2" para probar la política 2, y asi sucesivamente
        
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
        Política 1: Estrategia básica sin uso de proxies.
        Solo utiliza información básica de nodos y aristas para tomar decisiones.
        
        Esta política debe:
        - NO utilizar los proxies
        - Solo usar información básica del grafo (nodos, aristas, pesos)
        - Implementar una estrategia válida para cualquier ciudad
        """
        # Buscar el punto de extracción con la ruta más corta
        best_path = None
        best_length = float('inf')

        for target in city.extraction_nodes:
            try:
                path = nx.shortest_path(city.graph, city.starting_node, target, weight='weight')
                path_length = nx.shortest_path_length(city.graph, city.starting_node, target, weight='weight')

                if path_length < best_length:
                    best_path = path
                    best_length = path_length

            except nx.NetworkXNoPath:
                continue  # Si no hay ruta a este punto, intenta con otro

        if best_path is None:
            # No se encontró ninguna ruta válida
            return PolicyResult([city.starting_node], {'explosives': 0, 'ammo': 0, 'radiation_suits': 0})

        # Ajustar la distribución de recursos (puede mejorarse)
        resources = {
            'explosives': max_resources // 3,
            'ammo': max_resources // 3,
            'radiation_suits': max_resources // 3
        }

        return PolicyResult(best_path, resources)

    
    def _policy_2(self, city: CityGraph, proxy_data: ProxyData, max_resources: int) -> PolicyResult:
        """
        Política 2: Estrategia usando proxies y sus descripciones documentadas.
        
        Objetivo: Incorporar información ambiental en decisiones de evacuación
        basándose en los indicadores de sensores y conocimiento experto.
        """
        # Convertir datos de proxies a DataFrames para análisis más fácil
        proxy_data_nodes_df = convert_node_data_to_df(proxy_data.node_data)
        proxy_data_edges_df = convert_edge_data_to_df(proxy_data.edge_data)
        
        # Encontrar el punto de extracción más seguro basado en múltiples indicadores
        def evaluate_extraction_node(node):
            node_data = proxy_data.node_data.get(node, {})
            
            # Evaluar riesgos y condiciones del nodo
            seismic_risk = node_data.get('seismic_activity', 0)
            radiation_level = node_data.get('radiation_readings', 0)
            structural_health = node_data.get('structural_integrity', 0)
            population_density = node_data.get('population_density', 0)
            emergency_signals = node_data.get('emergency_calls', 0)
            
            # Calcular un puntaje de seguridad
            # Menor es mejor - queremos minimizar riesgos
            safety_score = (
                seismic_risk + 
                radiation_level + 
                (1 - structural_health) + 
                population_density
            )
            
            return safety_score
        
        # Seleccionar el punto de extracción más seguro
        extraction_nodes = city.extraction_nodes
        safest_extraction = min(extraction_nodes, key=evaluate_extraction_node)
        
        # Encontrar ruta considerando condiciones de los bordes
        def path_risk_assessment(path):
            total_risk = 0
            for i in range(len(path) - 1):
                edge = (path[i], path[i+1])
                edge_data = proxy_data.edge_data.get(edge, {})
                
                # Evaluar riesgos del borde
                structural_damage = edge_data.get('structural_damage', 0)
                debris_density = edge_data.get('debris_density', 0)
                movement_sightings = edge_data.get('movement_sightings', 0)
                signal_interference = edge_data.get('signal_interference', 0)
                
                # Calcular riesgo del borde
                edge_risk = (
                    structural_damage + 
                    debris_density + 
                    movement_sightings + 
                    signal_interference
                )
                total_risk += edge_risk
            
            return total_risk
        
        # Encontrar ruta con el menor riesgo
        try:
            # Intentar primero el camino más corto
            initial_path = nx.shortest_path(city.graph, city.starting_node, safest_extraction, weight='weight')
            
            # Si hay múltiples rutas posibles, encontrar la menos riesgosa
            alternative_paths = list(nx.all_simple_paths(city.graph, city.starting_node, safest_extraction))
            path = min(alternative_paths, key=path_risk_assessment)
        except nx.NetworkXNoPath:
            # Último recurso si no hay ruta
            path = [city.starting_node]
        
        # Asignación inteligente de recursos
        def calculate_resource_needs():
            # Analizar necesidades de recursos basado en indicadores
            resource_needs = {
                'explosives': 0,
                'ammo': 0,
                'radiation_suits': 0
            }
            
            # Explosivos basados en daño estructural
            explosive_need = sum(
                proxy_data.edge_data.get((path[i], path[i+1]), {}).get('structural_damage', 0) 
                for i in range(len(path) - 1)
            )
            resource_needs['explosives'] = min(
                int(explosive_need * max_resources * 0.4), 
                max_resources // 3
            )
            
            # Trajes de radiación basados en niveles de radiación
            radiation_risk = max(
                proxy_data.node_data.get(node, {}).get('radiation_readings', 0) 
                for node in path
            )
            resource_needs['radiation_suits'] = min(
                int(radiation_risk * max_resources * 0.4), 
                max_resources // 3
            )
            
            # Municiones basadas en movimientos detectados
            movement_risk = sum(
                proxy_data.edge_data.get((path[i], path[i+1]), {}).get('movement_sightings', 0) 
                for i in range(len(path) - 1)
            )
            resource_needs['ammo'] = min(
                int(movement_risk * max_resources * 0.4), 
                max_resources // 3
            )
            
            # Ajustar para no exceder recursos totales
            total_assigned = sum(resource_needs.values())
            if total_assigned > max_resources:
                scale_factor = max_resources / total_assigned
                resource_needs = {k: int(v * scale_factor) for k, v in resource_needs.items()}
            
            return resource_needs
        
        resources = calculate_resource_needs()
        
        return PolicyResult(path, resources)
    
    def _policy_3(self, city: CityGraph, proxy_data: ProxyData, max_resources: int) -> PolicyResult:
        """
        Política 3: Estrategia usando datos de simulaciones previas.
        Utiliza estadísticas básicas de simulaciones anteriores para mejorar la toma de decisiones.
        
        Esta política debe:
        - Utilizar datos de simulaciones previas
        - Implementar mejoras basadas en estadísticas básicas
        - NO usar modelos de machine learning
        """
        # TODO: Implementa tu solución aquí
        # Aquí deberías cargar y analizar datos de simulaciones previas
        
        target = city.extraction_nodes[0]
        
        try:
            path = nx.shortest_path(city.graph, city.starting_node, target, 
                                  weight='weight')
        except nx.NetworkXNoPath:
            path = [city.starting_node]
            
        resources = {
            'explosives': max_resources // 3,
            'ammo': max_resources // 3,
            'radiation_suits': max_resources // 3
        }
        
        return PolicyResult(path, resources)
    
    def _policy_4(self, city: CityGraph, proxy_data: ProxyData, max_resources: int) -> PolicyResult:
        """
        Política 4: Estrategia avanzada y optimizada.
        - Usa distancia, seguridad y datos históricos para elegir el mejor punto de extracción.
        - Utiliza el algoritmo A* para encontrar la ruta óptima.
        - Asigna recursos de manera eficiente en función del riesgo real.
        """

        # Verificar si la ciudad es conexa
        reachable_extractions = [node for node in city.extraction_nodes if nx.has_path(city.graph, city.starting_node, node)]

        if not reachable_extractions:
            print(f"🔴 ALERTA: La ciudad {len(city.graph.nodes)} nodos NO tiene conexión con los puntos de extracción.")
            return PolicyResult([city.starting_node], {'explosives': 0, 'ammo': 0, 'radiation_suits': 0})


        # 1 Selección Inteligente del Punto de Extracción
        def evaluate_extraction_node(node):
            """Evalúa la seguridad del nodo de extracción en función de múltiples indicadores."""
            node_data = proxy_data.node_data.get(node, {})
            historical_success = node_data.get('past_success_rate', 0.5)  

            # 🔹 Verificamos si hay un camino antes de calcular la distancia
            if not nx.has_path(city.graph, city.starting_node, node):
                return float("inf")  # Penaliza nodos sin conexión para que no se elijan

            distance = nx.shortest_path_length(city.graph, city.starting_node, node)

            safety_score = (
                (node_data.get('radiation_readings', 0) * 2) +
                (node_data.get('seismic_activity', 0) * 1.5) +
                (1 - node_data.get('structural_integrity', 1)) +  
                node_data.get('population_density', 0)
            ) 

            # 🔹 NO considerar puntos a más de 30 nodos de distancia
            if distance > 30:
                return float("inf")  # Penaliza puntos demasiado lejanos

            return safety_score + (distance * 0.3)  # 🔹 Ahora distancia tiene más peso


        valid_extractions = [node for node in city.extraction_nodes if nx.has_path(city.graph, city.starting_node, node)]

        if not valid_extractions:
            return PolicyResult([city.starting_node], {'explosives': 0, 'ammo': 0, 'radiation_suits': 0})  # 🔹 No hay ruta posible

        best_extraction = min(valid_extractions, key=evaluate_extraction_node)


        # 2 Encontrar la Ruta Más Segura con A*
        def edge_risk(edge):
            """Evalúa el riesgo de cada camino en función de los datos del proxy."""
            edge_data = proxy_data.edge_data.get(edge, {})
            return (
                edge_data.get('structural_damage', 0) + 
                edge_data.get('debris_density', 0) +
                edge_data.get('movement_sightings', 0) +
                edge_data.get('signal_interference', 0)
            )  # 🔥 Cuanto más alto, más peligroso

        try:
            path = nx.astar_path(city.graph, city.starting_node, best_extraction, 
                                weight=lambda u, v, d: (d.get('weight', 1) * 0.5) + (edge_risk((u, v)) * 0.5))
            
            if len(path) > 50:  # 🔹 Si la ruta es muy larga, buscar una alternativa
                print(f"⚠️ Ruta a extracción {best_extraction} es de {len(path)} nodos. Buscando alternativa...")
                alternative_paths = list(nx.all_shortest_paths(city.graph, city.starting_node, best_extraction, weight='weight'))
                path = min(alternative_paths, key=len)
                
        except nx.NetworkXNoPath:
            print("❌ No se encontró una ruta con A*, intentando con Dijkstra...")
            try:
                path = nx.shortest_path(city.graph, city.starting_node, best_extraction, weight='weight')
            except nx.NetworkXNoPath:
                print(f"🚨 ERROR: No hay rutas disponibles para evacuar en la ciudad de {len(city.graph.nodes)} nodos.")
                return PolicyResult([city.starting_node], {'explosives': 1, 'ammo': 1, 'radiation_suits': 1})

        # 3 Asignación Inteligente de Recursos
        def allocate_resources():
            """Asigna recursos asegurando que sean proporcionales a la amenaza."""
            total_risk = sum(edge_risk((path[i], path[i+1])) for i in range(len(path)-1))
            path_length_factor = min(len(path) / 50, 1)  # 🔹 Ajuste basado en ruta

            if total_risk == 0:
                return {'explosives': 2, 'ammo': 2, 'radiation_suits': 2}  # 🔹 Recursos mínimos garantizados

            explosive_need = sum(proxy_data.edge_data.get((path[i], path[i+1]), {}).get('structural_damage', 0) for i in range(len(path) - 1))
            radiation_need = max(proxy_data.node_data.get(node, {}).get('radiation_readings', 0) for node in path)
            movement_risk = sum(proxy_data.edge_data.get((path[i], path[i+1]), {}).get('movement_sightings', 0) for i in range(len(path) - 1))

            total_factor = explosive_need + radiation_need + movement_risk + 0.01  
            resources = {
                'explosives': max(min(int((explosive_need / total_factor) * max_resources), max_resources // 3), 2),
                'ammo': max(min(int((movement_risk / total_factor) * max_resources), max_resources // 3), 2),
                'radiation_suits': max(min(int((radiation_need / total_factor) * max_resources), max_resources // 3), 2)
            }
            return resources






        resources = allocate_resources()

        return PolicyResult(path, resources)

    
    
    