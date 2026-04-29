#!/bin/bash

# Asegura el contexto de ejecución correcto
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$DIR" || exit

shopt -s nullglob
FILES=(input/*.shp)

if [ ${#FILES[@]} -eq 0 ]; then
    echo "ERROR: No hay archivos Shapefile (.shp) en la carpeta input/."
    exit 1
fi

echo "Iniciando Pipeline Robusto: SHP -> GeoJSON -> MBTiles -> PMTiles..."

for file in "${FILES[@]}"; do
    filename=$(basename "$file")
    name="${filename%.*}"
    
    echo "======================================"
    echo "⏳ Transformando: $filename"
    echo "======================================"
    
    # Gatekeeper: Verificación de Proyección
    if [ ! -f "input/${name}.prj" ]; then
        echo "❌ ERROR CRÍTICO: Falta el archivo input/${name}.prj"
        echo "   GDAL necesita el archivo .prj para re-proyectar correctamente."
        exit 1
    fi

    # 1. GDAL reproyecta a web (WGS84)
    echo "   [1/4] GDAL -> Extrayendo a GeoJSON (EPSG:4326)..."
    docker compose run --rm gdal "ogr2ogr -f GeoJSON -t_srs EPSG:4326 output/${name}_temp.geojson input/${filename}"
    
    # 2. Tippecanoe genera la pirámide vectorial en formato nativo MBTiles
    echo "   [2/4] Tippecanoe -> Generando pirámide MBTiles (Capa: '${name}')..."
    docker compose run --rm tippecanoe "tippecanoe -l \"${name}\" -f -Z0 -z15 --drop-densest-as-needed -o output/${name}_temp.mbtiles output/${name}_temp.geojson"
    
    # 3. Protomaps empaqueta a PMTiles (El paso clave que faltaba)
    echo "   [3/4] Protomaps -> Empaquetando MBTiles a PMTiles..."
    docker compose run --rm pmtiles convert "output/${name}_temp.mbtiles" "output/${name}.pmtiles"
    
    # 4. Limpieza
    echo "   [4/4] Limpiando archivos temporales pesados..."
    rm -f "output/${name}_temp.geojson" "output/${name}_temp.mbtiles"
    
    echo "✅ Terminado con éxito: output/${name}.pmtiles"
    echo ""
done

echo "Transformación Completa. Listo para test en Protomaps."