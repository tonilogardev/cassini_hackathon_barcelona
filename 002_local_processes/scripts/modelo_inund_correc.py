import os
import sys
import site
from pathlib import Path

# ============================================================
# 0. FORÇAR O PROJ DO RASTERIO INSTALADO NO USUÁRIO
# ============================================================
def configure_proj_from_user_site():
    candidates = []

    try:
        user_site = site.getusersitepackages()
        if user_site:
            candidates.append(Path(user_site) / "rasterio" / "proj_data")
    except Exception:
        pass

    for p in sys.path:
        try:
            rp = Path(p) / "rasterio" / "proj_data"
            candidates.append(rp)
        except Exception:
            pass

    for c in candidates:
        if c.exists():
            os.environ["PROJ_DATA"] = str(c)
            os.environ["PROJ_LIB"] = str(c)
            print(f"Usando PROJ_DATA de: {c}")
            return str(c)

    raise RuntimeError(
        "Não encontrei a pasta rasterio/proj_data. "
        "Verifique se o rasterio foi instalado com pip --user."
    )

configure_proj_from_user_site()

# ============================================================
# 1. IMPORTS
# ============================================================
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.crs import CRS
import matplotlib.pyplot as plt
import pyflwdir

# ============================================================
# 2. CAMINHOS
# ============================================================
dem_path = r"C:\Users\becari.i.campos\OneDrive - Institut Cartogràfic i Geològic de Catalunya\proyecte 2nd\Dades\2_intento\input\MDT_2M.tif"

landuse_path = r"C:\Users\becari.i.campos\OneDrive - Institut Cartogràfic i Geològic de Catalunya\proyecte 2nd\Dades\COBERTAS\FME_46302427_1774629520147_23560\mcsctif1774629520019.tif"

rasters_dir = r"C:\Users\becari.i.campos\OneDrive - Institut Cartogràfic i Geològic de Catalunya\proyecte 2nd\Dades\2_intento\rasters_building_road"

buildings_path = os.path.join(rasters_dir, "buildings.tif")
roads_path = os.path.join(rasters_dir, "roads.tif")

out_dir = r"C:\Users\becari.i.campos\OneDrive - Institut Cartogràfic i Geològic de Catalunya\proyecte 2nd\Dades\2_intento\Output_3_edif_road"

os.makedirs(out_dir, exist_ok=True)

# ============================================================
# 3. PARÂMETROS
# ============================================================
DEFAULT_CRS = CRS.from_epsg(25831)   # ETRS89 / UTM 31N
rain_mm = 120.0
hotspot_quantile = 0.99

# pesos do índice final
weight_accum = 0.85
weight_runoff = 0.15

# CN específicos
CN_URBAN = 95.0
CN_BARE_SOIL = 88.0
CN_GREEN = 75.0
CN_AGRI = 80.0
CN_FOREST = 65.0
CN_DEFAULT = 85.0

CN_ROADS = 95.0
CN_BUILDINGS = 98.0

# ============================================================
# 4. AGRUPAMENTO DAS CLASSES DE USO DO SOLO
# AJUSTAR SE NECESSÁRIO APÓS VALIDAR A LEGENDA
# ============================================================
URBAN_CLASSES = [1, 2, 3, 4, 5, 7, 8, 9, 10, 11]
BARE_SOIL_CLASSES = [13, 14, 15]
GREEN_CLASSES = [16, 18, 19, 20, 21, 22, 23, 24]
AGRI_CLASSES = [25, 26, 27, 28, 29, 30]
FOREST_CLASSES = [31, 32, 34, 35]
WATER_CLASSES = [39]

# ============================================================
# 5. FUNÇÕES AUXILIARES
# ============================================================
def read_raster(path):
    with rasterio.open(path) as src:
        arr = src.read(1)
        profile = src.profile.copy()
        transform = src.transform
        crs = src.crs
        nodata = src.nodata
    return arr, profile, transform, crs, nodata

def write_raster(path, arr, profile, nodata=None, dtype=None):
    prof = profile.copy()
    if dtype is None:
        dtype = str(arr.dtype)

    prof.update(
        driver="GTiff",
        dtype=dtype,
        count=1,
        compress="lzw"
    )

    if nodata is not None:
        prof.update(nodata=nodata)

    with rasterio.open(path, "w", **prof) as dst:
        dst.write(arr.astype(dtype), 1)

def minmax_norm(arr, mask):
    out = np.full(arr.shape, np.nan, dtype="float32")
    vals = arr[mask]
    if vals.size == 0:
        return out
    vmin = np.nanmin(vals)
    vmax = np.nanmax(vals)
    if np.isclose(vmin, vmax):
        out[mask] = 0
    else:
        out[mask] = (arr[mask] - vmin) / (vmax - vmin)
    return out

def scs_runoff(P, CN):
    CN = CN.astype("float32")
    valid = np.isfinite(CN)

    out = np.full(CN.shape, np.nan, dtype="float32")
    if not np.any(valid):
        return out

    CN_clip = np.clip(CN[valid], 1, 100)
    S = (25400.0 / CN_clip) - 254.0
    Ia = 0.2 * S

    Q = np.zeros(CN_clip.shape, dtype="float32")
    runoff_mask = P > Ia
    Q[runoff_mask] = ((P - Ia[runoff_mask]) ** 2) / (P + 0.8 * S[runoff_mask])

    out[valid] = Q
    return out

def save_text(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(str(line) + "\n")

def align_to_dem(src_array, src_transform, src_crs, src_nodata, dem_shape, dem_transform, dem_crs, fill_value, resampling=Resampling.nearest, out_dtype=np.float32):
    aligned = np.full(dem_shape, fill_value, dtype=out_dtype)
    reproject(
        source=src_array,
        destination=aligned,
        src_transform=src_transform,
        src_crs=src_crs,
        src_nodata=src_nodata,
        dst_transform=dem_transform,
        dst_crs=dem_crs,
        dst_nodata=fill_value,
        resampling=resampling
    )
    return aligned

# ============================================================
# 6. VERIFICAÇÃO DE CAMINHOS
# ============================================================
print("Verificando caminhos...")
paths_to_check = {
    "DEM": dem_path,
    "Uso do solo": landuse_path,
    "Buildings": buildings_path,
    "Roads": roads_path,
}

for name, p in paths_to_check.items():
    print(f"{name} existe? {os.path.exists(p)} -> {p}")
    if not os.path.exists(p):
        raise FileNotFoundError(f"{name} não encontrado: {p}")

# ============================================================
# 7. LER MDT
# ============================================================
dem, dem_profile, dem_transform, dem_crs, dem_nodata = read_raster(dem_path)
dem = dem.astype("float32")

if dem_crs is None:
    print("MDT sem CRS no arquivo. Forçando EPSG:25831.")
    dem_crs = DEFAULT_CRS
    dem_profile["crs"] = dem_crs

dem_mask = np.isfinite(dem)
if dem_nodata is not None:
    dem_mask &= dem != dem_nodata

dem[~dem_mask] = np.nan

print("\nMDT carregado:")
print(" - shape:", dem.shape)
print(" - CRS:", dem_crs)
print(" - resolução:", dem_transform.a, "x", abs(dem_transform.e))

# área do pixel
pixel_width = abs(dem_transform.a)
pixel_height = abs(dem_transform.e)
cell_area_m2 = pixel_width * pixel_height

# ============================================================
# 8. LER E ALINHAR USO DO SOLO AO MDT
# ============================================================
landuse, lu_profile, lu_transform, lu_crs, lu_nodata = read_raster(landuse_path)

if lu_crs is None:
    print("Uso do solo sem CRS no arquivo. Forçando EPSG:25831.")
    lu_crs = DEFAULT_CRS
    lu_profile["crs"] = lu_crs

print("\nUso do solo carregado:")
print(" - shape:", landuse.shape)
print(" - CRS:", lu_crs)
print(" - resolução:", lu_transform.a, "x", abs(lu_transform.e))

aligned_landuse = align_to_dem(
    src_array=landuse,
    src_transform=lu_transform,
    src_crs=lu_crs,
    src_nodata=lu_nodata,
    dem_shape=dem.shape,
    dem_transform=dem_transform,
    dem_crs=dem_crs,
    fill_value=65535,
    resampling=Resampling.nearest,
    out_dtype=np.uint16
).astype("float32")

aligned_landuse[aligned_landuse == 65535] = np.nan
aligned_landuse[~dem_mask] = np.nan

write_raster(
    os.path.join(out_dir, "01_landuse_aligned_to_dem.tif"),
    np.where(np.isnan(aligned_landuse), -9999, aligned_landuse),
    dem_profile,
    nodata=-9999,
    dtype="float32"
)

unique_classes = np.unique(aligned_landuse[np.isfinite(aligned_landuse)]).astype(int)

print("\nClasses únicas do uso do solo alinhado:")
print(unique_classes.tolist())

save_text(
    os.path.join(out_dir, "classes_unicas_uso_solo.txt"),
    [
        "Classes únicas do raster de uso do solo alinhado ao MDT:",
        ", ".join(map(str, unique_classes.tolist()))
    ]
)

# ============================================================
# 9. LER E ALINHAR BUILDINGS
# ============================================================
buildings, b_profile, b_transform, b_crs, b_nodata = read_raster(buildings_path)

if b_crs is None:
    print("Buildings sem CRS no arquivo. Forçando EPSG:25831.")
    b_crs = DEFAULT_CRS
    b_profile["crs"] = b_crs

print("\nBuildings carregado:")
print(" - shape:", buildings.shape)
print(" - CRS:", b_crs)
print(" - resolução:", b_transform.a, "x", abs(b_transform.e))

aligned_buildings = align_to_dem(
    src_array=buildings,
    src_transform=b_transform,
    src_crs=b_crs,
    src_nodata=b_nodata,
    dem_shape=dem.shape,
    dem_transform=dem_transform,
    dem_crs=dem_crs,
    fill_value=0,
    resampling=Resampling.nearest,
    out_dtype=np.uint8
).astype("uint8")

aligned_buildings[~dem_mask] = 0
buildings_mask = aligned_buildings == 1

write_raster(
    os.path.join(out_dir, "02_buildings_aligned.tif"),
    aligned_buildings,
    dem_profile,
    nodata=0,
    dtype="uint8"
)

# ============================================================
# 10. LER E ALINHAR ROADS
# ============================================================
roads, r_profile, r_transform, r_crs, r_nodata = read_raster(roads_path)

if r_crs is None:
    print("Roads sem CRS no arquivo. Forçando EPSG:25831.")
    r_crs = DEFAULT_CRS
    r_profile["crs"] = r_crs

print("\nRoads carregado:")
print(" - shape:", roads.shape)
print(" - CRS:", r_crs)
print(" - resolução:", r_transform.a, "x", abs(r_transform.e))

aligned_roads = align_to_dem(
    src_array=roads,
    src_transform=r_transform,
    src_crs=r_crs,
    src_nodata=r_nodata,
    dem_shape=dem.shape,
    dem_transform=dem_transform,
    dem_crs=dem_crs,
    fill_value=0,
    resampling=Resampling.nearest,
    out_dtype=np.uint8
).astype("uint8")

aligned_roads[~dem_mask] = 0
roads_mask = aligned_roads == 1

write_raster(
    os.path.join(out_dir, "03_roads_aligned.tif"),
    aligned_roads,
    dem_profile,
    nodata=0,
    dtype="uint8"
)

# ============================================================
# 11. CRIAÇÃO DO RASTER CN
# ============================================================
cn = np.full(dem.shape, np.nan, dtype="float32")

# base pelo uso do solo
cn[np.isin(aligned_landuse, URBAN_CLASSES)] = CN_URBAN
cn[np.isin(aligned_landuse, BARE_SOIL_CLASSES)] = CN_BARE_SOIL
cn[np.isin(aligned_landuse, GREEN_CLASSES)] = CN_GREEN
cn[np.isin(aligned_landuse, AGRI_CLASSES)] = CN_AGRI
cn[np.isin(aligned_landuse, FOREST_CLASSES)] = CN_FOREST

# água fora do cálculo
cn[np.isin(aligned_landuse, WATER_CLASSES)] = np.nan

all_mapped = set(
    URBAN_CLASSES
    + BARE_SOIL_CLASSES
    + GREEN_CLASSES
    + AGRI_CLASSES
    + FOREST_CLASSES
    + WATER_CLASSES
)

unmapped_classes = [c for c in unique_classes if c not in all_mapped]
for c in unmapped_classes:
    cn[aligned_landuse == c] = CN_DEFAULT

# sobrescrever com roads e buildings
cn[roads_mask] = CN_ROADS
cn[buildings_mask] = CN_BUILDINGS

cn[~dem_mask] = np.nan

write_raster(
    os.path.join(out_dir, "04_curve_number_cn.tif"),
    np.where(np.isnan(cn), -9999, cn),
    dem_profile,
    nodata=-9999,
    dtype="float32"
)

# relatório de classes
report_lines = ["Resumo de classes e atribuição de CN:"]
for c in unique_classes:
    if c in WATER_CLASSES:
        cn_info = "EXCLUÍDA (água)"
    elif c in URBAN_CLASSES:
        cn_info = f"{CN_URBAN}"
    elif c in BARE_SOIL_CLASSES:
        cn_info = f"{CN_BARE_SOIL}"
    elif c in GREEN_CLASSES:
        cn_info = f"{CN_GREEN}"
    elif c in AGRI_CLASSES:
        cn_info = f"{CN_AGRI}"
    elif c in FOREST_CLASSES:
        cn_info = f"{CN_FOREST}"
    else:
        cn_info = f"{CN_DEFAULT} (default)"
    pixels = int(np.sum(aligned_landuse == c))
    report_lines.append(f"Classe {c}: CN base = {cn_info}; pixels = {pixels}")

report_lines.append("")
report_lines.append(f"Pixels roads = {int(np.sum(roads_mask))}; CN roads = {CN_ROADS}")
report_lines.append(f"Pixels buildings = {int(np.sum(buildings_mask))}; CN buildings = {CN_BUILDINGS}")

save_text(os.path.join(out_dir, "resumo_classes_cn.txt"), report_lines)

# máscara impermeável combinada
impervious_mask = np.zeros(dem.shape, dtype="uint8")
impervious_mask[roads_mask] = 1
impervious_mask[buildings_mask] = 1

write_raster(
    os.path.join(out_dir, "05_impervious_mask_buildings_roads.tif"),
    impervious_mask,
    dem_profile,
    nodata=0,
    dtype="uint8"
)

print("\nRaster CN criado com roads + buildings.")
if unmapped_classes:
    print("Classes sem grupo definido, usando CN_DEFAULT =", CN_DEFAULT)
    print("Classes:", unmapped_classes)

# ============================================================
# 12. DIREÇÃO DE FLUXO A PARTIR DO MDT
# ============================================================
print("\nGerando flow directions com pyflwdir...")
flw = pyflwdir.from_dem(
    data=dem,
    nodata=np.nan,
    transform=dem_transform,
    latlon=False
)

print("Área do pixel:", cell_area_m2, "m²")

# ============================================================
# 13. RUNOFF LOCAL
# ============================================================
runoff_local_mm = scs_runoff(rain_mm, cn)
runoff_local_mm[~dem_mask] = np.nan

runoff_local_m = runoff_local_mm / 1000.0
local_volume_m3 = runoff_local_m * cell_area_m2
local_volume_m3[~dem_mask] = np.nan

write_raster(
    os.path.join(out_dir, "06_runoff_local_mm.tif"),
    np.where(np.isnan(runoff_local_mm), -9999, runoff_local_mm),
    dem_profile,
    nodata=-9999,
    dtype="float32"
)

write_raster(
    os.path.join(out_dir, "07_local_volume_m3.tif"),
    np.where(np.isnan(local_volume_m3), -9999, local_volume_m3),
    dem_profile,
    nodata=-9999,
    dtype="float32"
)

print("Runoff local calculado.")

# ============================================================
# 14. ACUMULAÇÃO DO ESCOAMENTO
# ============================================================
print("\nAcumulando fluxo...")
accum_input = np.nan_to_num(local_volume_m3, nan=0.0).astype("float32")
accum_volume_m3 = flw.accuflux(accum_input).astype("float32")
accum_volume_m3[~dem_mask] = np.nan

uparea_km2 = flw.upstream_area(unit="km2").astype("float32")
uparea_km2[~dem_mask] = np.nan

write_raster(
    os.path.join(out_dir, "08_accumulated_volume_m3.tif"),
    np.where(np.isnan(accum_volume_m3), -9999, accum_volume_m3),
    dem_profile,
    nodata=-9999,
    dtype="float32"
)

write_raster(
    os.path.join(out_dir, "09_upstream_area_km2.tif"),
    np.where(np.isnan(uparea_km2), -9999, uparea_km2),
    dem_profile,
    nodata=-9999,
    dtype="float32"
)

print("Acumulação concluída.")

# ============================================================
# 15. FLOOD INDEX (CORRIGIDO COM TOPOGRAFIA)
# ============================================================

mask_idx = (
    np.isfinite(runoff_local_mm)
    & np.isfinite(accum_volume_m3)
    & np.isfinite(cn)
    & np.isfinite(dem)
)

# ------------------------------------------------------------
# NORMALIZAÇÕES
# ------------------------------------------------------------
runoff_n = minmax_norm(runoff_local_mm, mask_idx)
accum_n = minmax_norm(accum_volume_m3, mask_idx)
elev_n  = minmax_norm(dem, mask_idx)

# ------------------------------------------------------------
# BAIXAS COTAS (LOWLAND)
# ------------------------------------------------------------
lowland = np.full(dem.shape, np.nan, dtype="float32")
lowland[mask_idx] = 1.0 - elev_n[mask_idx]

# ------------------------------------------------------------
# NOVO FLOOD INDEX
# (ênfase em acumulação + posição topográfica)
# ------------------------------------------------------------
weight_accum = 0.7
weight_lowland = 0.2
weight_runoff = 0.1

flood_index = np.full(dem.shape, np.nan, dtype="float32")

flood_index[mask_idx] = (
    weight_accum   * accum_n[mask_idx] +
    weight_lowland * lowland[mask_idx] +
    weight_runoff  * runoff_n[mask_idx]
)

# ------------------------------------------------------------
# SALVAR FLOOD INDEX
# ------------------------------------------------------------
write_raster(
    os.path.join(out_dir, "10_flood_index.tif"),
    np.where(np.isnan(flood_index), -9999, flood_index),
    dem_profile,
    nodata=-9999,
    dtype="float32"
)

# ------------------------------------------------------------
# HOTSPOTS (threshold ajustável)
# ------------------------------------------------------------
thr = 0.95   # <- valor inicial recomendado

hotspots = np.zeros(dem.shape, dtype="uint8")
hotspots[(flood_index >= thr) & mask_idx] = 1
hotspots[~mask_idx] = 255

write_raster(
    os.path.join(out_dir, "11_flood_hotspots.tif"),
    hotspots,
    dem_profile,
    nodata=255,
    dtype="uint8"
)

# ------------------------------------------------------------
# DEBUG / LOG
# ------------------------------------------------------------
print("Flood index corrigido gerado.")
print("Pesos usados:")
print(f"  accum = {weight_accum}")
print(f"  lowland = {weight_lowland}")
print(f"  runoff = {weight_runoff}")

print(f"Threshold hotspot = {thr}")

print("Estatísticas flood index:")
print("  min =", np.nanmin(flood_index))
print("  max =", np.nanmax(flood_index))
print("  p90 =", np.nanpercentile(flood_index, 90))
print("  p95 =", np.nanpercentile(flood_index, 95))
print("  p98 =", np.nanpercentile(flood_index, 98))
print("  p99 =", np.nanpercentile(flood_index, 99))

print("Valores únicos hotspot:", np.unique(hotspots))

# ============================================================
# 16. ESTATÍSTICAS
# ============================================================
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

save_text(os.path.join(out_dir, "estatisticas_modelo.txt"), stats_lines)

# ============================================================
# 17. QUICKLOOK
# ============================================================
fig, axes = plt.subplots(2, 4, figsize=(22, 11))

im0 = axes[0, 0].imshow(dem, cmap="terrain")
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

for ax in axes.ravel():
    ax.set_axis_off()

plt.tight_layout()
plt.savefig(os.path.join(out_dir, "quicklook_modelo_inundacao.png"), dpi=200, bbox_inches="tight")
plt.show()

print("\nConcluído.")
print("Saídas em:", out_dir)