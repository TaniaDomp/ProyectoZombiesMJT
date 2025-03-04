# Métricas y Resultados de Simulación

Este documento describe las métricas, visualizaciones y archivos de resultados generados durante las simulaciones de evacuación. Los datos se organizan en una estructura jerárquica dentro del directorio `data/policies/<policy_name>/experiments/<experiment_id>/`.

## Estructura de Directorios

```
data/policies/<policy_name>/
├── experiments/
│   └── <experiment_id>/
│       ├── core_metrics.json
│       ├── core_metrics.csv
│       ├── resource_metrics.json
│       ├── environmental_metrics.json
│       ├── raw_data.json
│       ├── cities/
│       │   └── city_<run_id>_metrics.json
│       │   └── city_<run_id>_metrics.csv
│       └── visualizations/
│           ├── key_metrics.png
│           ├── success_rates.png
│           ├── resource_efficiency.png
│           ├── environmental_impact.png
│           ├── performance_metrics.png
│           ├── resource_impact.png
│           └── environmental_correlations.png
```

## Archivos de Métricas

### 1. Core Metrics (`core_metrics.json`, `core_metrics.csv`)

Contiene las métricas principales del experimento, incluyendo:

- **Metadata**:
  - Nombre de la política
  - ID del experimento
  - Timestamp
  - Configuración
  - Total de ejecuciones

- **Overall Performance**:
  - Tasa de éxito
  - Tiempo promedio
  - Longitud promedio de ruta
  - Recursos asignados y utilizados
  - Eficiencia de recursos
  - Desviaciones estándar de todas las métricas

- **Resource Details** (por tipo de recurso):
  - Promedio asignado y desviación estándar
  - Promedio utilizado y desviación estándar
  - Eficiencia

- **Proxy Metrics**:
  - Estadísticas de nodos y bordes
  - Medias y desviaciones estándar de indicadores

- **By City Size**:
  - Todas las métricas anteriores desglosadas por tamaño de ciudad

### 2. Resource Metrics (`resource_metrics.json`)

Métricas detalladas sobre el uso de recursos:

- **Overall**:
  - Promedios por tipo de recurso
  - Eficiencia de uso
  - Recursos necesarios vs utilizados

- **By City Size**:
  - Desglose de uso de recursos por tamaño de ciudad

- **Analysis**:
  - Recurso más utilizado
  - Recurso más necesitado

### 3. Environmental Metrics (`environmental_metrics.json`)

Métricas ambientales y su impacto:

- **Overall**:
  - Indicadores de nodos y bordes
  - Promedios globales

- **By City Size**:
  - Indicadores desglosados por tamaño de ciudad

- **Correlations**:
  - Correlaciones con el éxito de la misión
  - Correlaciones entre indicadores

### 4. Métricas por Ciudad (`cities/city_<run_id>_metrics.json`)

Métricas detalladas para cada ejecución individual:

- **Metadata**:
  - ID de la ejecución
  - Tamaño de la ciudad
  - Configuración específica

- **Performance**:
  - Éxito/fracaso
  - Tiempo y distancia
  - Uso de recursos

- **Resource Details**:
  - Uso detallado por tipo de recurso
  - Eficiencia individual

- **Proxy Metrics**:
  - Estadísticas de indicadores
  - Medias y desviaciones por ciudad

## Visualizaciones

### 1. Key Metrics (`key_metrics.png`)
Dashboard principal que muestra:
- Distribución de resultados de misión
- Distribución de tiempos
- Comparación de uso de recursos
- Eficiencia de recursos por resultado
- Eficiencia por tamaño de ciudad

### 2. Success Rates (`success_rates.png`)
- Tasas de éxito por tamaño de ciudad
- Línea de referencia de éxito global

### 3. Resource Efficiency (`resource_efficiency.png`)
- Comparación de recursos asignados vs utilizados
- Eficiencia por tipo de recurso

### 4. Environmental Impact (`environmental_impact.png`)
- Correlaciones con éxito de misión
- Impacto de factores ambientales

### 5. Performance Metrics (`performance_metrics.png`)
- Tabla resumen de indicadores clave
- Métricas por tamaño de ciudad

### 6. Resource Impact (`resource_impact.png`)
- Eficiencia de recursos
- Análisis de recursos críticos

### 7. Environmental Correlations (`environmental_correlations.png`)
- Matriz de correlación de factores ambientales
- Identificación de patrones clave

## Formatos de Datos

Los datos se proporcionan en dos formatos para facilitar diferentes tipos de análisis:

1. **JSON**: Formato jerárquico que mantiene la estructura completa de los datos.
2. **CSV**: Formato tabular que facilita el análisis en herramientas como Excel o pandas.

Los archivos CSV utilizan un sistema de nombres de columnas aplanado donde las jerarquías se indican con guiones bajos (por ejemplo, `overall_performance_success_rate`). 