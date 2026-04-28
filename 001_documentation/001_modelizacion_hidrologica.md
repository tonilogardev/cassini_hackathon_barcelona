# Modelización Hidrológica (Data Engine)

## Index

1. [Visión General](#1-vision-general)
2. [Fase 1: Modelo Digital del Terreno](#2-fase-1-modelo-digital-del-terreno)
3. [Fase 2: Alineación Espacial](#3-fase-2-alineacion-espacial)
4. [Fase 3: Curve Number (CN)](#4-fase-3-curve-number-cn)
5. [Fase 4: Ruteo de Flujo](#5-fase-4-ruteo-de-flujo)
6. [Fase 5: Índice de Inundación (Flood Index)](#6-fase-5-indice-de-inundacion-flood-index)
7. [Fase 6: Resultados y Visualización](#7-fase-6-resultados-y-visualizacion)
8. [Añadir un Nuevo Proyecto](#8-anadir-un-nuevo-proyecto)

---

## 1 Visión General

- Motor geoespacial contenerizado basado en Docker para análisis hidrológico y cálculo de riesgo de inundación superficial.
- Construido con `typer`, `rasterio` y `pyflwdir`.
- Analiza el código fuente principal: [main.py](../002_local_processes/src/main.py).

[←Index](#index)

## 2 Fase 1: Modelo Digital del Terreno

- Lee el MDT (Modelo Digital de Terreno) y define la resolución base y el CRS por defecto (`EPSG:25831`).
- Calcula el área del píxel (`cell_area_m2`) para las transformaciones volumétricas.
- Limpia los valores `NoData` para evitar la propagación de ruido.
- Archivo responsable de IO: [io.py](../002_local_processes/src/utils/io.py).

[←Index](#index)

## 3 Fase 2: Alineación Espacial

- Remuestrea las capas de Usos del Suelo, Edificios y Carreteras para que coincidan topológicamente con el MDT.
- Aplica `Resampling.nearest` para mantener la integridad de los valores categóricos (sin interpolación decimal).
- Enmascara los bordes de todos los rásters usando la máscara del MDT.
- Función clave: `align_to_dem` en [terrain.py](../002_local_processes/src/core/terrain.py).

[←Index](#index)

## 4 Fase 3: Curve Number (CN)

- Asigna empíricamente la capacidad de infiltración a cada píxel. Valores bajos = permeable (ej. Bosque `CN: 65`), Valores altos = impermeable (ej. Asfalto `CN: 98`).
- Mapea las clases de suelo y sobrescribe (aplasta) las celdas donde hay Edificios o Carreteras garantizando un escurrimiento máximo.
- Exporta el ráster base: `04_curve_number_cn.tif`.

[←Index](#index)

## 5 Fase 4: Ruteo de Flujo

- Utiliza `scs_runoff` para convertir los mm de lluvia caídos en volumen escurrido en función del CN.
- Emplea el método `pyflwdir.from_dem` para calcular las direcciones de flujo topográficas basadas en los 8 vecinos (D8).
- Rueda la lluvia no infiltrada ladera abajo (`accuflux`), sumando el volumen propio y el de las celdas aguas arriba.
- Lógica de cálculo: [hydrology.py](../002_local_processes/src/core/hydrology.py).

[←Index](#index)

## 6 Fase 5: Índice de Inundación (Flood Index)

- Normaliza (0 a 1) las variables mediante `minmax_norm`.
- Aplica un cálculo multivariante ponderado:
  - `70%`: Acumulación topográfica de volumen (`accum_n`).
  - `20%`: Zonas de baja altitud relativa (`lowland`).
  - `10%`: Escorrentía local pura (`runoff_n`).
- Genera el ráster central del análisis: `10_flood_index.tif`.

[←Index](#index)

## 7 Fase 6: Resultados y Visualización

- Exporta 11 rásters intermedios TIFF en el directorio [output_badalona/](../002_local_processes/output_badalona/).
- Genera zonas críticas (Hotspots) para los píxeles con un Flood Index `> 0.95`.
- Genera el reporte estadístico y la vista general.
- ***Visuals***:
    ![Quicklook Modelo de Inundación](../002_local_processes/output_badalona/quicklook_modelo_inundacao.png)

[←Index](#index)

## 8 Añadir un Nuevo Proyecto

- Crea un directorio en `002_local_processes/input/` con el nombre del proyecto (ej. `barcelona`).
- Asegúrate de copiar exactamente las 4 capas físicas con los nombres estandarizados:
  - `mdt_2m.tif`
  - `land_use.tif`
  - `buildings.tif`
  - `roads.tif`
- Edita el [docker-compose.yml](../002_local_processes/docker-compose.yml) modificando el parámetro `--project` en la instrucción `command`:
  ```yaml
  command: "python3 src/main.py --project barcelona"
  ```
- Lanza el contenedor y el motor creará el pipeline completo en `output/barcelona/`.

[←Index](#index)
