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
    
    # 1. GDAL traduce TIF a MBTILES (Formato intermedio SQLite) a nivel base (Zoom 14)
    echo "   [1/4] GDAL -> Generando nivel base (MBTiles Z14)..."
    docker compose run --rm gdal "gdal_translate -of MBTILES -co MAXZOOM=14 input/${filename} output/${name}_temp.mbtiles"
    
    # 2. GDAL añade las pirámides (Overviews) para zooms menores (13, 12, 11, 10, 9...)
    # Los factores 2 4 8 16 32 dividen la resolución a la mitad en cada paso.
    echo "   [2/4] GDAL -> Construyendo pirámides (Overviews) para zooms lejanos..."
    docker compose run --rm gdal "gdaladdo -r nearest output/${name}_temp.mbtiles 2 4 8 16 32"

    # 3. Protomaps PMTiles convierte el MBTiles en PMTiles optimizado
    echo "   [3/4] Protomaps (go-pmtiles) -> Convirtiendo a PMTiles crudo..."
    docker compose run --rm pmtiles convert "output/${name}_temp.mbtiles" "output/${name}.pmtiles"
    
    # 4. Limpieza de rastros pesados
    echo "   [4/4] Limpiando base de datos intermedia (MBTiles)..."
    rm -f output/${name}_temp.mbtiles
    
    echo "✅ Terminado: output/${name}.pmtiles"
    echo ""
done

echo "Transformación Completa. Puedes subirlos a /006_cassini_hackathons/public/data/raster"