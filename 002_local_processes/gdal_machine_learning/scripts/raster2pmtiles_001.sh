#!/bin/bash

# Asegura que siempre corremos Docker-Compose desde el directorio 007
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$DIR" || exit

shopt -s nullglob
FILES=(input/*.tif input/*.tiff input/*.vrt)

if [ ${#FILES[@]} -eq 0 ]; then
    echo "ERROR: No hay archivos Raster (TIF/TIFF/VRT) en la carpeta input/"
    exit 1
fi

echo "Iniciando Raster -> PMTiles pipeline usando GDAL 3.8+ (OSGeo)..."

for file in "${FILES[@]}"; do
    filename=$(basename "$file")
    name="${filename%.*}"
    
    echo "======================================"
    echo "⏳ Transformando: $filename -> $name.pmtiles"
    echo "======================================"
    
    # 1. GDAL traduce TIF a MBTILES (Formato intermedio SQLite)
    echo "   [1/3] GDAL -> Generando pirámide base (MBTiles)..."
    docker compose run --rm gdal "gdal_translate -of MBTILES -co MAXZOOM=14 input/${filename} output/${name}_temp.mbtiles"
    
    # 2. Protomaps PMTiles convierte el MBTiles en PMTiles optimizado
    echo "   [2/3] Protomaps (go-pmtiles) -> Convirtiendo a PMTiles crudo..."
    docker compose run --rm pmtiles convert "output/${name}_temp.mbtiles" "output/${name}.pmtiles"
    
    # 3. Limpieza de rastros pesados
    echo "   [3/3] Limpiando base de datos intermedia (MBTiles)..."
    rm -f output/${name}_temp.mbtiles
    
    echo "✅ Terminado: output/${name}.pmtiles"
    echo ""
done

echo "Transformación Completa. Puedes subirlos a /006_cassini_hackathons/public/data/raster"
