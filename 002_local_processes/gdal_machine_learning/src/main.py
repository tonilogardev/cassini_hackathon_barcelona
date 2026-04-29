import os
import typer
import numpy as np
import matplotlib.pyplot as plt
import pyflwdir
from rasterio.crs import CRS
from rasterio.warp import Resampling

# Importamos nuestros módulos refactorizados para mantener main.py limpio
from utils.io import read_raster, write_raster, save_text
from core.terrain import align_to_dem, minmax_norm
from core.hydrology import scs_runoff

def process_flood(
    project: str = typer.Option(..., help="Nombre del proyecto (ej. badalona)"),
    input_dir: str = typer.Option("input", help="Directorio base de entrada"),
    out_dir: str = typer.Option("output", help="Directorio base de salida"),
    rain_mm: float = typer.Option(120.0, help="Escenario de lluvia a simular en milímetros")
):
    """
    Motor principal de procesamiento de inundaciones.
    Ejecuta el pipeline completo: Lectura -> Alineación -> Curve Number -> Runoff -> Flujo -> Flood Index
    """
    # Construimos las rutas de forma dinámica
    project_input = os.path.join(input_dir, project)
    out = os.path.join(out_dir, project)
    
    dem = os.path.join(project_input, "mdt_2m.tif")
    landuse = os.path.join(project_input, "land_use.tif")
    buildings = os.path.join(project_input, "buildings.tif")
    roads = os.path.join(project_input, "roads.tif")
    
    # 1. PREPARACIÓN BÁSICA
    # Creamos la carpeta de salida si no existe.
    os.makedirs(out, exist_ok=True)
    
    # Definimos el Sistema de Referencia de Coordenadas (CRS) por defecto (UTM 31N)
    # Es fundamental para que los rasters encajen sobre el mapa en el visor final.
    DEFAULT_CRS = CRS.from_epsg(25831)
    
    print("Verificando caminhos...")
    paths_to_check = [dem, landuse, buildings, roads]
    for p in paths_to_check:
        if not os.path.exists(p):
            raise FileNotFoundError(f"Não encontrado: {p}")
            
    # ==========================================
    # FASE 1: PROCESAMIENTO DEL MODELO DE TERRENO
    # ==========================================
    print(f"Leyendo DEM: {dem}")
    dem_arr, dem_profile, dem_transform, dem_crs, dem_nodata = read_raster(dem)
    dem_arr = dem_arr.astype("float32")
    
    # Si el MDT no tiene CRS (metadatos espaciales), se lo forzamos.
    if dem_crs is None:
        dem_crs = DEFAULT_CRS
        dem_profile["crs"] = dem_crs
        
    # Limpiamos valores nulos (NaN) usando una máscara booleana.
    dem_mask = np.isfinite(dem_arr)
    if dem_nodata is not None:
        dem_mask &= dem_arr != dem_nodata
    dem_arr[~dem_mask] = np.nan
    
    # Calculamos el tamaño real (en metros cuadrados) de cada pixel.
    # Esto es vital para calcular volúmenes de agua reales más adelante.
    pixel_width = abs(dem_transform.a)
    pixel_height = abs(dem_transform.e)
    cell_area_m2 = pixel_width * pixel_height
    
    # ==========================================
    # FASE 2: ALINEACIÓN ESPACIAL DE CAPAS
    # ==========================================
    # Para poder hacer matemáticas con las matrices de numpy, TODOS los rasters
    # deben tener exactamente la misma resolución (shape) y alineación que el MDT.
    print("Alineando capas de uso de suelo, carreteras y edificios...")
    
    # --- Alineación de Usos del Suelo ---
    landuse_arr, lu_profile, lu_transform, lu_crs, lu_nodata = read_raster(landuse)
    if lu_crs is None: lu_crs = DEFAULT_CRS
    
    # Usamos Nearest Neighbor (Resampling.nearest) porque son datos categóricos (clases 1, 2, 3...)
    # No podemos interpolar clases (ej: no existe la clase 1.5).
    aligned_landuse = align_to_dem(
        src_array=landuse_arr, src_transform=lu_transform, src_crs=lu_crs, src_nodata=lu_nodata,
        dem_shape=dem_arr.shape, dem_transform=dem_transform, dem_crs=dem_crs, fill_value=65535,
        resampling=Resampling.nearest, out_dtype=np.uint16
    ).astype("float32")
    
    aligned_landuse[aligned_landuse == 65535] = np.nan
    aligned_landuse[~dem_mask] = np.nan
    
    write_raster(os.path.join(out, "01_landuse_aligned_to_dem.tif"), np.where(np.isnan(aligned_landuse), -9999, aligned_landuse), dem_profile, nodata=-9999, dtype="float32")
    
    # Extraemos qué clases de uso existen realmente en nuestra zona de estudio
    unique_classes = np.unique(aligned_landuse[np.isfinite(aligned_landuse)]).astype(int)
    save_text(os.path.join(out, "classes_unicas_uso_solo.txt"), ["Classes únicas do raster de uso do solo alinhado ao MDT:", ", ".join(map(str, unique_classes.tolist()))])
    
    # --- Alineación de Edificios ---
    b_arr, b_profile, b_transform, b_crs, b_nodata = read_raster(buildings)
    if b_crs is None: b_crs = DEFAULT_CRS
    aligned_buildings = align_to_dem(
        src_array=b_arr, src_transform=b_transform, src_crs=b_crs, src_nodata=b_nodata,
        dem_shape=dem_arr.shape, dem_transform=dem_transform, dem_crs=dem_crs, fill_value=0,
        resampling=Resampling.nearest, out_dtype=np.uint8
    ).astype("uint8")
    aligned_buildings[~dem_mask] = 0
    buildings_mask = aligned_buildings == 1 # Máscara booleana: True donde hay un edificio
    write_raster(os.path.join(out, "02_buildings_aligned.tif"), aligned_buildings, dem_profile, nodata=0, dtype="uint8")
    
    # --- Alineación de Carreteras ---
    r_arr, r_profile, r_transform, r_crs, r_nodata = read_raster(roads)
    if r_crs is None: r_crs = DEFAULT_CRS
    aligned_roads = align_to_dem(
        src_array=r_arr, src_transform=r_transform, src_crs=r_crs, src_nodata=r_nodata,
        dem_shape=dem_arr.shape, dem_transform=dem_transform, dem_crs=dem_crs, fill_value=0,
        resampling=Resampling.nearest, out_dtype=np.uint8
    ).astype("uint8")
    aligned_roads[~dem_mask] = 0
    roads_mask = aligned_roads == 1 # Máscara booleana: True donde hay carretera
    write_raster(os.path.join(out, "03_roads_aligned.tif"), aligned_roads, dem_profile, nodata=0, dtype="uint8")
    
    # ==========================================
    # FASE 3: CURVE NUMBER (CAPACIDAD DE ABSORCIÓN)
    # ==========================================
    print("Calculando Curve Number...")
    # El Curve Number (CN) es un método empírico. A mayor número, más impermeable es el suelo.
    # CN cercano a 100 = asfalto (todo el agua corre). CN cercano a 60 = bosque (mucha agua se absorbe).
    CN_URBAN, CN_BARE_SOIL, CN_GREEN, CN_AGRI, CN_FOREST, CN_DEFAULT = 95.0, 88.0, 75.0, 80.0, 65.0, 85.0
    CN_ROADS, CN_BUILDINGS = 95.0, 98.0
    
    # Mapeo de las clases del raster original a categorías funcionales
    URBAN_CLASSES = [1, 2, 3, 4, 5, 7, 8, 9, 10, 11]
    BARE_SOIL_CLASSES = [13, 14, 15]
    GREEN_CLASSES = [16, 18, 19, 20, 21, 22, 23, 24]
    AGRI_CLASSES = [25, 26, 27, 28, 29, 30]
    FOREST_CLASSES = [31, 32, 34, 35]
    WATER_CLASSES = [39] # Al agua no se le calcula escurrimiento
    
    cn = np.full(dem_arr.shape, np.nan, dtype="float32")
    
    # Asignamos el valor CN correspondiente a cada píxel dependiendo de su clase
    cn[np.isin(aligned_landuse, URBAN_CLASSES)] = CN_URBAN
    cn[np.isin(aligned_landuse, BARE_SOIL_CLASSES)] = CN_BARE_SOIL
    cn[np.isin(aligned_landuse, GREEN_CLASSES)] = CN_GREEN
    cn[np.isin(aligned_landuse, AGRI_CLASSES)] = CN_AGRI
    cn[np.isin(aligned_landuse, FOREST_CLASSES)] = CN_FOREST
    cn[np.isin(aligned_landuse, WATER_CLASSES)] = np.nan
    
    # Las clases no mapeadas se les asigna el valor por defecto
    all_mapped = set(URBAN_CLASSES + BARE_SOIL_CLASSES + GREEN_CLASSES + AGRI_CLASSES + FOREST_CLASSES + WATER_CLASSES)
    unmapped_classes = [c for c in unique_classes if c not in all_mapped]
    for c in unmapped_classes:
        cn[aligned_landuse == c] = CN_DEFAULT
        
    # Las carreteras y edificios "aplastan" cualquier uso del suelo que hubiera debajo,
    # forzando un CN altísimo (superficie hiper-impermeable).
    cn[roads_mask] = CN_ROADS
    cn[buildings_mask] = CN_BUILDINGS
    cn[~dem_mask] = np.nan
    
    write_raster(os.path.join(out, "04_curve_number_cn.tif"), np.where(np.isnan(cn), -9999, cn), dem_profile, nodata=-9999, dtype="float32")
    
    # Generamos un pequeño log en texto para auditar la clasificación
    report_lines = ["Resumo de classes e atribuição de CN:"]
    for c in unique_classes:
        if c in WATER_CLASSES: cn_info = "EXCLUÍDA (água)"
        elif c in URBAN_CLASSES: cn_info = f"{CN_URBAN}"
        elif c in BARE_SOIL_CLASSES: cn_info = f"{CN_BARE_SOIL}"
        elif c in GREEN_CLASSES: cn_info = f"{CN_GREEN}"
        elif c in AGRI_CLASSES: cn_info = f"{CN_AGRI}"
        elif c in FOREST_CLASSES: cn_info = f"{CN_FOREST}"
        else: cn_info = f"{CN_DEFAULT} (default)"
        pixels = int(np.sum(aligned_landuse == c))
        report_lines.append(f"Classe {c}: CN base = {cn_info}; pixels = {pixels}")
    report_lines.append("")
    report_lines.append(f"Pixels roads = {int(np.sum(roads_mask))}; CN roads = {CN_ROADS}")
    report_lines.append(f"Pixels buildings = {int(np.sum(buildings_mask))}; CN buildings = {CN_BUILDINGS}")
    save_text(os.path.join(out, "resumo_classes_cn.txt"), report_lines)
    
    # Creamos un raster que simplemente indica con 1s qué está pavimentado
    impervious_mask = np.zeros(dem_arr.shape, dtype="uint8")
    impervious_mask[roads_mask] = 1
    impervious_mask[buildings_mask] = 1
    write_raster(os.path.join(out, "05_impervious_mask_buildings_roads.tif"), impervious_mask, dem_profile, nodata=0, dtype="uint8")
    
    # ==========================================
    # FASE 4: RUTEO DE FLUJO (ACUMULACIÓN)
    # ==========================================
    print("Calculando Flow Direction y Acumulacion...")
    
    # PyFlwdir calcula hacia dónde cae el agua en cada pixel fijándose en sus 8 vecinos (topografía)
    flw = pyflwdir.from_dem(data=dem_arr, nodata=np.nan, transform=dem_transform, latlon=False)
    
    # Calculamos el escurrimiento local (runoff): ¿Cuánta lluvia NO se absorbió en este pixel?
    runoff_local_mm = scs_runoff(rain_mm, cn)
    runoff_local_mm[~dem_mask] = np.nan
    
    # Pasamos los mm de lluvia a metros cúbicos de agua basándonos en el tamaño del pixel
    runoff_local_m = runoff_local_mm / 1000.0
    local_volume_m3 = runoff_local_m * cell_area_m2
    local_volume_m3[~dem_mask] = np.nan
    
    write_raster(os.path.join(out, "06_runoff_local_mm.tif"), np.where(np.isnan(runoff_local_mm), -9999, runoff_local_mm), dem_profile, nodata=-9999, dtype="float32")
    write_raster(os.path.join(out, "07_local_volume_m3.tif"), np.where(np.isnan(local_volume_m3), -9999, local_volume_m3), dem_profile, nodata=-9999, dtype="float32")
    
    # El paso más complejo: Hacemos rodar todo el volumen de agua topografía abajo.
    # Suma el volumen local + el volumen de todos los píxeles aguas arriba que desembocan aquí.
    accum_input = np.nan_to_num(local_volume_m3, nan=0.0).astype("float32")
    accum_volume_m3 = flw.accuflux(accum_input).astype("float32")
    accum_volume_m3[~dem_mask] = np.nan
    
    # También calculamos el área total de la cuenca que drena hacia este pixel
    uparea_km2 = flw.upstream_area(unit="km2").astype("float32")
    uparea_km2[~dem_mask] = np.nan
    
    write_raster(os.path.join(out, "08_accumulated_volume_m3.tif"), np.where(np.isnan(accum_volume_m3), -9999, accum_volume_m3), dem_profile, nodata=-9999, dtype="float32")
    write_raster(os.path.join(out, "09_upstream_area_km2.tif"), np.where(np.isnan(uparea_km2), -9999, uparea_km2), dem_profile, nodata=-9999, dtype="float32")
    
    # ==========================================
    # FASE 5: FLOOD INDEX (CÁLCULO DEL RIESGO)
    # ==========================================
    print("Calculando Flood Index y Hotspots...")
    mask_idx = np.isfinite(runoff_local_mm) & np.isfinite(accum_volume_m3) & np.isfinite(cn) & np.isfinite(dem_arr)
    
    # Normalizamos todas las variables de 0 a 1 para poder combinarlas justamente
    runoff_n = minmax_norm(runoff_local_mm, mask_idx)
    accum_n = minmax_norm(accum_volume_m3, mask_idx)
    elev_n  = minmax_norm(dem_arr, mask_idx)
    
    # Zonas bajas: 1.0 (máximo riesgo, cota baja) a 0.0 (montaña alta)
    lowland = np.full(dem_arr.shape, np.nan, dtype="float32")
    lowland[mask_idx] = 1.0 - elev_n[mask_idx]
    
    # --- LA FÓRMULA MÁGICA ---
    # Un índice ponderado donde pesa muchísimo la cantidad de agua acumulada topográficamente (70%)
    weight_accum = 0.7
    weight_lowland = 0.2
    weight_runoff = 0.1
    flood_index = np.full(dem_arr.shape, np.nan, dtype="float32")
    flood_index[mask_idx] = (weight_accum * accum_n[mask_idx] + weight_lowland * lowland[mask_idx] + weight_runoff * runoff_n[mask_idx])
    
    write_raster(os.path.join(out, "10_flood_index.tif"), np.where(np.isnan(flood_index), -9999, flood_index), dem_profile, nodata=-9999, dtype="float32")
    
    # ==========================================
    # FASE 6: EXPORTACIÓN Y LOGS
    # ==========================================
    # Definimos como "Hotspot" (zona crítica) a los píxeles cuyo índice es superior a 0.95 (95%)
    thr = 0.95
    hotspots = np.zeros(dem_arr.shape, dtype="uint8")
    hotspots[(flood_index >= thr) & mask_idx] = 1
    hotspots[~mask_idx] = 255
    write_raster(os.path.join(out, "11_flood_hotspots.tif"), hotspots, dem_profile, nodata=255, dtype="uint8")
    
    # Generamos el informe final
    stats_lines = [
        "MODELO DE INUNDAÇÃO SIMPLIFICADO COM BUILDINGS + ROADS",
        "======================================================",
        "",
        f"Chuva do cenário: {rain_mm} mm",
        f"Área do pixel: {cell_area_m2:.2f} m²",
        f"Pixels válidos: {np.sum(mask_idx)}",
        f"Pixels roads: {int(np.sum(roads_mask))}",
        f"Pixels buildings: {int(np.sum(buildings_mask))}",
        f"Pixels impermeáveis (roads + buildings): {int(np.sum(impervious_mask == 1))}",
        "",
        "Parâmetros do flood index:",
        f"Peso acumulação = {weight_accum}",
        f"Peso runoff = {weight_runoff}",
        f"Threshold hotspot absoluto = {thr}",
        "",
        "CN utilizados:",
        f"CN roads = {CN_ROADS}",
        f"CN buildings = {CN_BUILDINGS}",
        "",
        "Runoff local (mm):",
        f"  mín: {np.nanmin(runoff_local_mm):.3f}",
        f"  máx: {np.nanmax(runoff_local_mm):.3f}",
        f"  média: {np.nanmean(runoff_local_mm):.3f}",
        "",
        "Volume acumulado (m³):",
        f"  mín: {np.nanmin(accum_volume_m3):.3f}",
        f"  máx: {np.nanmax(accum_volume_m3):.3f}",
        f"  média: {np.nanmean(accum_volume_m3):.3f}",
        "",
        "Flood Index:",
        f"  mín: {np.nanmin(flood_index):.3f}",
        f"  máx: {np.nanmax(flood_index):.3f}",
        f"  média: {np.nanmean(flood_index):.3f}",
        f"Threshold hotspot: {thr:.4f}",
    ]
    save_text(os.path.join(out, "estatisticas_modelo.txt"), stats_lines)
    
    # Generamos una imagen "Quicklook" para previsualizar todos los rasters a vista de pájaro
    fig, axes = plt.subplots(2, 4, figsize=(22, 11))
    
    im0 = axes[0, 0].imshow(dem_arr, cmap="terrain")
    axes[0, 0].set_title("MDT")
    plt.colorbar(im0, ax=axes[0, 0], shrink=0.8)
    
    im1 = axes[0, 1].imshow(aligned_landuse, cmap="tab20")
    axes[0, 1].set_title("Uso do solo alinhado")
    plt.colorbar(im1, ax=axes[0, 1], shrink=0.8)
    
    im2 = axes[0, 2].imshow(aligned_roads, cmap="Greys")
    axes[0, 2].set_title("Roads")
    plt.colorbar(im2, ax=axes[0, 2], shrink=0.8)
    
    im3 = axes[0, 3].imshow(aligned_buildings, cmap="Greys")
    axes[0, 3].set_title("Buildings")
    plt.colorbar(im3, ax=axes[0, 3], shrink=0.8)
    
    im4 = axes[1, 0].imshow(cn, cmap="viridis", vmin=60, vmax=100)
    axes[1, 0].set_title("Curve Number (CN)")
    plt.colorbar(im4, ax=axes[1, 0], shrink=0.8)
    
    im5 = axes[1, 1].imshow(runoff_local_mm, cmap="Blues")
    axes[1, 1].set_title("Runoff local (mm)")
    plt.colorbar(im5, ax=axes[1, 1], shrink=0.8)
    
    vmin = np.nanpercentile(accum_volume_m3, 5)
    vmax = np.nanpercentile(accum_volume_m3, 98)
    im6 = axes[1, 2].imshow(accum_volume_m3, cmap="magma", vmin=vmin, vmax=vmax)
    axes[1, 2].set_title("Volume acumulado (m³)")
    plt.colorbar(im6, ax=axes[1, 2], shrink=0.8)
    
    im7 = axes[1, 3].imshow(flood_index, cmap="Reds")
    axes[1, 3].set_title("Flood Index")
    plt.colorbar(im7, ax=axes[1, 3], shrink=0.8)
    
    for ax in axes.ravel(): ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(os.path.join(out, "quicklook_modelo_inundacao.png"), dpi=200, bbox_inches="tight")
    
    print(f"Pipeline completado. Resultados en {out}")

if __name__ == "__main__":
    # Typer detecta automáticamente los argumentos de la función 'process_flood' 
    # y genera una CLI profesional.
    typer.run(process_flood)
