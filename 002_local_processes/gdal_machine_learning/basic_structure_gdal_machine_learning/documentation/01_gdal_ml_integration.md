# GDAL & Machine Learning Integration

## Objetivo
Este proyecto base (Boilerplate) resuelve el conflicto histórico de dependencias (ABI Hell) entre **GDAL** (Rasterio, C++) y **Machine Learning** (PyTorch, CUDA). Garantiza que ambos puedan coexistir y procesar datos masivos en memoria sin errores de `segmentation fault` ni pérdida de metadatos espaciales (EPSG).

## Arquitectura de la Solución
1.  **Aislamiento Docker**: Multi-stage build puro usando imagen base NVIDIA CUDA.
2.  **Wheels Oficiales**: Instalación de `rasterio` y `torch` vía `pip` usando binarios pre-compilados (`manylinux`).
3.  **Ambiente Limpio**: Sin instalación de librerías en el Sistema Operativo (`libgdal-dev`) y sin variables de entorno invasivas (`PROJ_LIB`), forzando a cada paquete a usar sus propios binarios sellados de forma segura.

---

## Cómo Comprobar la Integración

Si acabas de clonar este repositorio y quieres asegurarte de que tu entorno está listo para producción y es inmune a los conflictos mencionados, ejecuta la tubería de validación (End-to-End).

### Paso 1: Levantar y Validar
Abre tu terminal (WSL/Linux/macOS) en la raíz del proyecto y ejecuta la prueba:

```bash
docker compose build  # Construye la imagen unificada
docker compose run --rm cli validate-pipeline
```

### Paso 2: Entender qué ha ocurrido
El comando `validate-pipeline` hace lo siguiente:
1.  **[GDAL]**: Genera una imagen `.tif` (Raster) sintética de gran tamaño llamada `dummy_input.tif`.
2.  **[GDAL]**: Lee este archivo mediante "Lectura en Ventanas" (*Windowed Reading*) cargando solo un parche de 512x512 para no ahogar la RAM.
3.  **[PyTorch]**: Transforma ese cuadrante en un Tensor e inyecta la carga en un modelo neuronal (*DummyModel*) residente en memoria.
4.  **[GDAL]**: Escribe el resultado como `dummy_output.tif`, pero obligando a que se inyecte exactamente el mismo mapeo espacial y el código EPSG original (CRS).

### Paso 3: Verificar Resultados (Éxito)
Si el Boilerplate funciona en tu máquina, deberías ver esto por consola sin ningún error:

```text
1. Generating synthetic GeoTIFF (EPSG:4326)...
2. Reading a 512x512 window via SatelliteImageHandler...
3. Running PyTorch Inference Engine on Tensor of shape torch.Size([1, 512, 512])...
4. Writing result back to GeoTIFF preserving CRS...
Success! Output written to data/dummy_output.tif. Pipeline is robust.
```

¡Ya puedes empezar a construir tu lógica real en `src/models` y `src/data` con total tranquilidad!
