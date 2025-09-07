# Resolución de Problemas de Planificación con CSP y Búsqueda Heurística  

## Descripción
Este proyecto aplica técnicas de Inteligencia Artificial para resolver problemas de planificación y optimización en el contexto de la aviación.  
Se implementaron dos modelos principales:  

### Modelo CSP (Constraint Satisfaction Problem)
- Asignación de aviones a parkings y talleres de mantenimiento.  
- Gestión de múltiples restricciones (capacidad, adyacencia, prioridades de tareas).  
- Obtención de configuraciones óptimas en diferentes escenarios.  

### Modelo de Búsqueda Heurística (A*)
- Planificación de trayectorias de rodaje de aviones hasta la pista de despegue.  
- Comparación entre la heurística Manhattan y la heurística de Congestión.  
- Análisis de eficiencia en términos de tiempo de ejecución, nodos expandidos y makespan.   

## Funcionalidades implementadas
### Modelo CSP
- Asignación única de aviones por franja horaria.  
- Capacidad máxima por taller/parking (máx. 2 aviones, con compatibilidad JMB/STD).  
- Restricciones de adyacencia y capacidad espacial.  
- Priorización de tareas (tipo 2 antes que tipo 1).  
- Cumplimiento de todas las tareas dentro de franjas horarias disponibles.  

### Búsqueda heurística con A*
- Representación del espacio de estados y restricciones dinámicas.  
- Prevención de colisiones y cruces entre aviones.

## Tecnologías y herramientas utilizadas
- Python para implementación de algoritmos CSP y búsqueda heurística.  
- Algoritmo A* para planificación de trayectorias.  
- Heurísticas admisibles: Manhattan y Congestión.  
- Modelado CSP: definición formal con variables, dominios y restricciones.  
- Generación y análisis de resultados con estadísticas de ejecución y validación de restricciones. 
- Comparación de heurísticas Manhattan vs Congestión.  
- Generación de trayectorias válidas optimizando el makespan.  
