# Bugigangass | CASSINI Hackathon

## Index

1. [Descripción del Proyecto](#1-descripción-del-proyecto)
2. [El Equipo](#2-el-equipo)
3. [Stack Tecnológico](#3-stack-tecnológico)
4. [Estructura del Proyecto](#4-estructura-del-proyecto)
5. [Urban flood prediction](#5-urban-flood-prediction)
6. [Water quality monitoring](#6-water-quality-monitoring)
7. [Next steps](#7-next-steps)

---

## 1 Descripción del Proyecto

## Descripción del Proyecto
Bugigangass creara una solución solución de monitoreo y análisis hídrico que utiliza datos satelitales de la constelación **Copernicus (Sentinel)** para abordar desafíos críticos en la gestión del agua. Nuestro enfoque combina el pensamiento sistémico colaborativo, la arquitectura de datos geoespaciales y el procesamiento de imágenes satelitales para ofrecer insights accionables.

> **Reto seleccionado:**  
Elegir uno:  
Challenge 5: Urban flood prediction  

Challenge 3: Water quality monitoring  

Idea ganadora challenge 3: Water quality monitoring  


[←Index](#index)

## 2 El Equipo Blue Pixel

- **Ivan Pantaleoni**: *Earth Observation (EO) Lead & Geospatial Scientist*. Geólogo y especialista en observación de la Tierra, enfocado en análisis espacial y generación de cartografía a partir de datos geoespaciales.  
https://www.linkedin.com/in/ivan-pcm/  

- **Ameneh Alcalá**: *Urban Researcher and Spatial Data Analyst*. Urbanista investigadora especializada en gestión y análisis de datos espaciales, enfocada en la justicia social y espacial.   
https://www.linkedin.com/in/ameneh-alcala/?skipRedirect=true  

- **Antonio López García**: *Full-Stack Web GIS Developer & DevOps Architect*. De la idea el tratamiento de datos hasta el despliegue.   
https://www.linkedin.com/in/tonilogar/

[←Index](#index)

## 3 Stack Tecnológico

Nuestra metodología se divide en dos entornos diferenciados para maximizar la eficiencia técnica y la estabilidad del producto final.

### 1. Laboratorio Local: Procesamiento Geoespacial e IA
Espacio de trabajo dedicado a pruebas, testeo de soluciones GIS, cambios de formato y entrenamiento de modelos. Basado en la arquitectura robusta de [tonilogardev](https://github.com/tonilogardev/basic_structure_gdal_machine_learning).

* **Entorno Controlado**: Uso de Docker para resolver conflictos de dependencias entre **GDAL** (Rasterio) y **Machine Learning** (PyTorch).
* **Eficiencia de Datos**: Implementación de **Lectura en Ventanas** (Windowed Reading) de 512x512 para procesar GeoTIFFs masivos de Sentinel sin saturar la RAM.
* **Herramientas**: CLI basada en Typer para automatización de tareas de inferencia y procesamiento de imágenes satelitales.
* **Requisito de paridad**: Desarrollo obligatorio sobre **WSL (Linux)** para garantizar consistencia con producción.

### 2. MVP: Infraestructura de la Solución (Producción)
La herramienta mínima viable desplegada, centrada en el usuario y basada en la lógica de servicios de [web_basic_project].

* **Orquestación**: Docker Compose con inyección dinámica de variables de entorno *.env para desarrollo y producción.
* **Visualización**: Frontend VITE, sveltekit, maplibre-gl-js y pmtiles sin servidor.
En el caso de tener que trabajar con datos "on the fly" "COGs" se utilizará un servidor local de datos geoespaciales con titiler.

[←Index](#index)

## 4 Estructura del Proyecto

- [001_documentation/](./001_documentation/): Guías técnicas y manuales de arquitectura.
- [002_local_processes/](./002_local_processes/): Procesamiento local de datos Geo-AI.
- [003_MVP/](./003_MVP/):
    - [sentinel-viewer/](./003_MVP/sentinel-viewer/): Visor cartográfico Svelte/Vite.
    - [003_MVP/dev_run.sh](./003_MVP/dev_run.sh): Script de automatización y limpieza.

[←Index](#index)

## 5 Urban flood prediction

**Objetivo:**
Desarrollar un modelo de modelización hidrológica distribuida que permita identificar zonas susceptibles a inundación en un entorno urbano, a partir de la integración de datos de topografía (MDT) y uso del suelo.  

El modelo estima la generación de escorrentía mediante el método SCS-CN y simula su propagación utilizando análisis de flujo, permitiendo calcular la acumulación de agua en el territorio.  

A partir de estos resultados, se genera un índice de inundación que facilita la identificación de zonas críticas y la toma de decisiones.  

**Datos de entrada: 

- Zona MDT (2m ICGC) 
- Uso del suelo () 

[←Index](#index)

## 6 Water quality monitoring

**Objetivo:**  
Pronta detección de contaminación a través del monitoreo de la calidad del agua, conformado por indicadores de niveles de clorofila y turbidez.    

[←Index](#index)

## 7 Next steps

- [001_modelizacion_hidrologica.md](./001_documentation/001_modelizacion_hidrologica.md)                       