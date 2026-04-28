---
name: frontend-gis-architect
version: 2.0.0
description: Reglas estratégicas para el desarrollo del visor Sentinel. Especialización en Svelte 5, MapLibre GL JS y renderizado de alto rendimiento.
---

# Goal
Diseñar y programar una herramienta de visualización satelital de élite. El objetivo es procesar y combinar bandas de la constelación Copernicus con una latencia de respuesta instantánea, utilizando una interfaz que equilibre la potencia de un software profesional con la estética de un producto premium de 2026.

# Philosophy: Smart Complexity
* **The Svelte Exception**: Se establece **Svelte 5** como el framework oficial. Razón: Su naturaleza de compilador (sin Virtual DOM) garantiza que los recursos de la CPU se centren en el mapa WebGL y no en la gestión pesada de la UI.
* **WebGL First**: El motor de renderizado es **MapLibre GL JS**. Queda estrictamente prohibido el uso de librerías basadas en el DOM (como Leaflet) para la visualización de datos raster multiespectrales.
* **State over DOM**: Toda la lógica de bandas, fechas y coordenadas se gestiona mediante *Svelte Stores* o *Runes*. La UI debe ser una representación reactiva y pura del estado del sistema.

# Design Aesthetics: "The Sentinel Look"
* **Premium Dark Engine**: Interfaz oscura (Dark Mode) para resaltar el contraste de las imágenes satelitales. Paleta HSL: fondos oscuros profundos (`#0a0a0b`), acentos en cian o verde esmeralda.
* **Glassmorphism Estructural**: Paneles de control con desenfoque de fondo (`backdrop-filter: blur`) y bordes minimalistas con transparencia.
* **Micro-interacciones**: Transiciones fluidas en la carga de capas y feedback visual inmediato (hovers/active) en los selectores de bandas e índices (NDVI, EVI, etc.).
* **Tipografía Técnica**: Uso de fuentes sans-serif geométricas (Inter u Outfit) para una lectura clara de coordenadas y metadatos.

# Engineering Standards
1.  **Strict TypeScript**: Prohibido el uso de `any`. Define interfaces rigurosas para las respuestas de la API STAC y las configuraciones de capas de MapLibre.
2.  **Performance Budget**: El visor debe mantenerse a 60 FPS durante el paneo. El procesamiento de bandas se delega a **Titiler** (Backend), manteniendo el cliente ligero.
3.  **Architectural Docker**: Compilación de la app en etapa `node:alpine` y despliegue de assets estáticos sobre `nginx:stable-alpine` optimizado.
4.  **Modularidad Geo**: Separación estricta entre la lógica de búsqueda (STAC Service), el motor de mapa (Map Engine) y la gestión de estados (State Management).

# Workflow & Execution
* **Paso 1 (Contexto Espacial):** Define el `store` global que gestionará el `bbox`, fechas y filtros.
* **Paso 2 (Integración WebGL):** Inicializa el mapa de MapLibre asegurando que la instancia sea accesible pero no saturada por la reactividad del framework.
* **Paso 3 (Lógica de Bandas):** Genera dinámicamente las URLs de Titiler basándose en la selección de bandas (ej. `&bidx=4,3,2`).
* **Paso 4 (Optimización):** Implementa estados de carga (skeletons o spinners) para que el usuario perciba la potencia del procesamiento "on the fly".