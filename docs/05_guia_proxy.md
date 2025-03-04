# Guía de Indicadores Proxy: La Historia Detrás de los Datos

En los días posteriores al incidente, el Comando Estratégico de Respuesta a Emergencias estableció una red de monitoreo utilizando la infraestructura sobreviviente y equipos especializados. Esta es la historia de cómo recopilamos los datos que guían a nuestros equipos de rescate.

Para estandarizar los reportes, todos nuestros instrumentos han sido calibrados para reportar en una escala de 0 a 1, donde 0 representa la ausencia total del fenómeno medido y 1 su máxima intensidad registrada hasta la fecha.

## Indicadores de Nodos (Ubicaciones)

### Actividad Sísmica (`seismic_activity`)
Los sismógrafos de la red de monitoreo geológico de la ciudad, originalmente diseñados para detectar terremotos, ahora registran las vibraciones causadas por colapsos estructurales y movimientos masivos de escombros. Los equipos veteranos han aprendido a interpretar estas lecturas: números cercanos a 0 suelen indicar terreno estable, mientras que lecturas que se aproximan a 1 han precedido a colapsos catastróficos. Los equipos de rescate son especialmente cautelosos cuando las lecturas aumentan repentinamente en áreas con múltiples rutas bloqueadas.

### Lecturas de Radiación (`radiation_readings`)
Una red de detectores Geiger-Müller, instalados estratégicamente en postes y edificios sobrevivientes, transmite constantemente niveles de radiación. Los técnicos de radiación han calibrado los detectores para que marquen 0 cuando detectan solo la radiación de fondo natural de la ciudad, mientras que el valor de 1 corresponde a los niveles más letales encontrados hasta ahora. Los equipos de campo reportan que las lecturas intermedias suelen indicar zonas donde los trajes de protección son suficientes.

### Densidad Poblacional (`population_density`)
Combinando datos históricos del censo con lecturas térmicas actuales de drones de vigilancia, estimamos la concentración de actividad en diferentes áreas. El 0 en nuestros instrumentos corresponde a zonas verdaderamente desiertas, mientras que el 1 indica la máxima concentración de actividad registrada. Sin embargo, los rescatistas experimentados advierten que las lecturas altas no siempre son buenas noticias: a veces indican grandes concentraciones de infectados.

### Llamadas de Emergencia (`emergency_calls`)
Aunque la red celular está mayormente caída, algunas torres siguen funcionando. Los operadores del centro de comando han calibrado los sistemas para que marquen 0 en zonas sin ninguna señal de socorro, mientras que 1 representa la máxima intensidad de señales de emergencia jamás registrada. Los picos en las lecturas frecuentemente han llevado a rescates exitosos, aunque las señales más intensas también han coincidido con situaciones de peligro extremo.

### Lecturas Térmicas (`thermal_readings`)
Una flota de drones equipados con cámaras térmicas patrulla la ciudad continuamente. Las lecturas de 0 corresponden a la temperatura ambiente normal, mientras que 1 representa la máxima actividad térmica detectada hasta ahora. Los analistas han observado que las lecturas intermedias son las más interesantes: los infectados generan patrones térmicos distintivos que los operadores han aprendido a reconocer, mientras que los grupos de supervivientes producen firmas térmicas más variables.

### Fuerza de Señal (`signal_strength`)
Los repetidores de emergencia instalados tras el incidente proporcionan una red de comunicaciones básica. Los técnicos han calibrado los medidores para que marquen 1 en zonas con conectividad perfecta, mientras que 0 indica pérdida total de comunicación. Las lecturas intermedias suelen indicar zonas donde la comunicación es posible pero puede ser inestable.

### Integridad Estructural (`structural_integrity`)
Equipos de ingenieros utilizan una combinación de inspección visual mediante drones y análisis de vibraciones para evaluar la estabilidad de edificios y estructuras. Una lectura de 1 corresponde a estructuras que han resistido perfectamente el desastre, mientras que 0 indica colapso inminente o ya ocurrido. Los ingenieros de campo han aprendido a ser especialmente cautelosos en zonas donde múltiples estructuras muestran lecturas bajas simultáneamente.

## Indicadores de Bordes (Rutas)

### Daño Estructural (`structural_damage`)
Escáneres LIDAR montados en drones mapean constantemente el estado de las calles y puentes. Una lectura de 0 indica una ruta perfectamente despejada, mientras que 1 representa un bloqueo total que requiere explosivos para ser despejado. Los equipos de demolición han aprendido a estimar la cantidad de explosivos necesarios basándose en estas lecturas.

### Interferencia de Señal (`signal_interference`)
Los patrones de degradación en las comunicaciones entre puntos adyacentes revelan mucho sobre el terreno. Una lectura de 0 indica transmisión perfecta sin interferencia, mientras que 1 representa interferencia total que impide cualquier comunicación. Los técnicos han notado que la interferencia tiende a aumentar cerca de zonas con alta radiación.

### Avistamientos de Movimiento (`movement_sightings`)
Una red de cámaras de seguridad sobrevivientes y sensores de movimiento monitorea el flujo de actividad. Las lecturas van desde 0, que indica ausencia total de movimiento, hasta 1, que representa la máxima actividad detectada hasta ahora. Los observadores experimentados han aprendido a distinguir entre los patrones de movimiento de supervivientes y de infectados.

### Densidad de Escombros (`debris_density`)
El análisis fotogramétrico de imágenes de drones y satélite revela la acumulación de obstáculos en las rutas. Una lectura de 0 corresponde a una ruta completamente despejada, mientras que 1 indica la máxima acumulación de escombros registrada hasta ahora. Los equipos de rescate usan estas lecturas para planificar qué herramientas llevar a cada misión.

### Gradiente de Peligro (`hazard_gradient`)
Este indicador compuesto surgió de la experiencia de los primeros equipos de rescate, que notaron cómo los cambios bruscos en las condiciones eran a menudo más peligrosos que las condiciones adversas constantes. Una lectura de 0 indica condiciones uniformes sin cambios, mientras que 1 representa el cambio más abrupto en condiciones ambientales registrado hasta ahora.

## Notas sobre la Recopilación de Datos

- Los datos se actualizan cada 30 minutos, sujetos a la disponibilidad de los sistemas de monitoreo.
- La precisión de las lecturas varía según las condiciones ambientales y el estado de los sensores.
- Algunos sensores funcionan con energía solar y pueden tener datos limitados durante la noche.
- La red de monitoreo se expande continuamente conforme se recuperan y reparan más sistemas.

## Limitaciones Conocidas

- Las lecturas pueden verse afectadas por interferencia electromagnética de la radiación.
- La cobertura no es uniforme; algunas áreas tienen datos más precisos que otras.
- Los sistemas de monitoreo ocasionalmente fallan debido a daños o agotamiento de energía.
- Las condiciones pueden cambiar rápidamente entre actualizaciones de datos.

## Uso en Planificación de Misiones

Los equipos de rescate deben considerar estos indicadores como guías aproximadas, no como verdades absolutas. La experiencia en el campo y el juicio situacional siguen siendo cruciales para el éxito de las misiones de evacuación. Los veteranos insisten en que ninguna lectura individual cuenta la historia completa; es la combinación de múltiples indicadores y la experiencia del equipo lo que marca la diferencia entre el éxito y el fracaso. 