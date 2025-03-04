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
        
        
        self.policy_type = "policy_2" # TODO: Cambiar a "policy_2" para probar la política 2, y asi sucesivamente
        
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
        Política 4: Estrategia personalizada.
        Implementa tu mejor estrategia usando cualquier recurso disponible.
        
        Esta política puede:
        - Usar cualquier técnica o recurso que consideres apropiado
        - Implementar estrategias avanzadas de tu elección
        """
        # TODO: Implementa tu solución aquí
        proxy_data_nodes_df = convert_node_data_to_df(proxy_data.node_data)
        proxy_data_edges_df = convert_edge_data_to_df(proxy_data.edge_data)
        
        #print(f'\n Node Data: \n {proxy_data_nodes_df}')
        #print(f'\n Edge Data: \n {proxy_data_edges_df}')
        
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
    
    
    