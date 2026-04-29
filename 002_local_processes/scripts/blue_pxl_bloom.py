import os
from pathlib import Path

# ============================================================
# PROJ / RASTERIO FIX
# (needed in some QGIS / Windows environments)
# if your environment works fine, you can ignore this
# ============================================================

proj_path = Path.home() / r"AppData\Roaming\Python\Python312\site-packages\rasterio\proj_data"
os.environ["PROJ_LIB"] = str(proj_path)
os.environ["PROJ_DATA"] = str(proj_path)

import rasterio
import numpy as np
from rasterio.warp import reproject, Resampling
from rasterio.crs import CRS

# ============================================================
# USER INPUT (EDIT THESE PATHS)
# ============================================================

BASE_FOLDER = r"C:\YOUR_PROJECT_FOLDER"

path_10m = BASE_FOLDER + r"\R10m"
path_20m = BASE_FOLDER + r"\R20m"

output_dir = BASE_FOLDER + r"\OUTPUT"
os.makedirs(output_dir, exist_ok=True)

# Sentinel-2 prefix (example: T30SYJ_20191227T105349)
PREFIX = "YOUR_IMAGE_PREFIX"

# Example file structure (Sentinel-2 naming)
B02 = path_10m + fr"\{PREFIX}_B02_10m.jp2"
B03 = path_10m + fr"\{PREFIX}_B03_10m.jp2"
B04 = path_10m + fr"\{PREFIX}_B04_10m.jp2"
B08 = path_10m + fr"\{PREFIX}_B08_10m.jp2"

B05 = path_20m + fr"\{PREFIX}_B05_20m.jp2"
B06 = path_20m + fr"\{PREFIX}_B06_20m.jp2"
B8A = path_20m + fr"\{PREFIX}_B8A_20m.jp2"
B11 = path_20m + fr"\{PREFIX}_B11_20m.jp2"
SCL = path_20m + fr"\{PREFIX}_SCL_20m.jp2"

FORCED_CRS = CRS.from_epsg(32631)  # adjust if needed

# ============================================================
# FUNCTIONS
# ============================================================

def read_band(path, forced_crs=FORCED_CRS):
    with rasterio.open(path) as src:
        arr = src.read(1).astype("float32")
        profile = src.profile.copy()

        if profile.get("crs") is None:
            profile["crs"] = forced_crs

        return arr, profile


def resample_to_match(src_array, src_profile, target_profile, method="bilinear"):
    dst = np.empty(
        (target_profile["height"], target_profile["width"]),
        dtype=np.float32
    )

    src_crs = src_profile.get("crs") or FORCED_CRS
    dst_crs = target_profile.get("crs") or FORCED_CRS

    resampling = Resampling.nearest if method == "nearest" else Resampling.bilinear

    reproject(
        source=src_array,
        destination=dst,
        src_transform=src_profile["transform"],
        src_crs=src_crs,
        dst_transform=target_profile["transform"],
        dst_crs=dst_crs,
        resampling=resampling
    )

    return dst


def safe_div(a, b):
    return np.where(np.abs(b) < 1e-6, 0, a / b)


def normalize_percentile(arr, mask, pmin=2, pmax=98):
    out = np.zeros_like(arr, dtype=np.float32)
    valid = mask & np.isfinite(arr)

    if np.sum(valid) == 0:
        return out

    vmin = np.nanpercentile(arr[valid], pmin)
    vmax = np.nanpercentile(arr[valid], pmax)

    if vmax == vmin:
        return out

    out[valid] = (arr[valid] - vmin) / (vmax - vmin)
    return np.clip(out, 0, 1)


def percentile_threshold(arr, mask, p):
    valid = mask & np.isfinite(arr)
    if np.sum(valid) == 0:
        return 9999
    return np.nanpercentile(arr[valid], p)


def save_byte(array, profile, output_path, nodata=0):
    profile_out = profile.copy()
    profile_out.update(
        driver="GTiff",
        count=1,
        dtype="uint8",
        nodata=nodata,
        compress="lzw"
    )

    with rasterio.open(output_path, "w", **profile_out) as dst:
        dst.write(array.astype("uint8"), 1)


def save_rgb(r, g, b, profile, output_path):
    rgb = np.stack([
        (r * 255).astype("uint8"),
        (g * 255).astype("uint8"),
        (b * 255).astype("uint8")
    ])

    profile_out = profile.copy()
    profile_out.update(
        driver="GTiff",
        count=3,
        dtype="uint8",
        nodata=0,
        compress="lzw",
        photometric="RGB"
    )

    with rasterio.open(output_path, "w", **profile_out) as dst:
        dst.write(rgb)

# ============================================================
# LOAD DATA
# ============================================================

print("Reading 10m bands...")

b02, profile = read_band(B02)
b03, _ = read_band(B03)
b04, _ = read_band(B04)
b08, _ = read_band(B08)

profile["crs"] = profile.get("crs") or FORCED_CRS

print("Reading 20m bands...")

b05_20, prof20 = read_band(B05)
b06_20, _ = read_band(B06)
b8a_20, _ = read_band(B8A)
b11_20, _ = read_band(B11)
scl_20, _ = read_band(SCL)

print("Resampling 20m → 10m...")

b05 = resample_to_match(b05_20, prof20, profile)
b06 = resample_to_match(b06_20, prof20, profile)
b8a = resample_to_match(b8a_20, prof20, profile)
b11 = resample_to_match(b11_20, prof20, profile)
scl = resample_to_match(scl_20, prof20, profile, method="nearest")

# ============================================================
# SCALE (Sentinel-2 reflectance)
# ============================================================

b02 /= 10000.0
b03 /= 10000.0
b04 /= 10000.0
b05 /= 10000.0
b06 /= 10000.0
b08 /= 10000.0
b8a /= 10000.0
b11 /= 10000.0

# ============================================================
# INDICES
# ============================================================

print("Computing indices...")

NDWI = safe_div((b03 - b08), (b03 + b08))
MNDWI = safe_div((b03 - b11), (b03 + b11))

water_mask = (NDWI > 0.05) | (MNDWI > 0.10)

cloud_mask = np.isin(scl.astype(np.int16), [3, 8, 9, 10, 11])
valid_water = water_mask & (~cloud_mask)

# Floating algae (FAI)
NIR2 = b04 + (b11 - b04) * ((832.8 - 664.6) / (1613.7 - 664.6))
FAI = b08 - NIR2

# Chlorophyll
NDCI = safe_div((b05 - b04), (b05 + b04))

# Turbidity
NDTI = safe_div((b04 - b03), (b04 + b03))

# Red anomaly
RED_EXCESS = b04 - b03

# ============================================================
# NORMALIZATION (for visualization)
# ============================================================

turb_norm = normalize_percentile(NDTI, valid_water)
chl_norm = normalize_percentile(NDCI, valid_water)
algae_norm = normalize_percentile(FAI, valid_water)

# ============================================================
# ADAPTIVE THRESHOLDS
# ============================================================

thr_algae = percentile_threshold(FAI, valid_water, 95)
thr_chl = percentile_threshold(NDCI, valid_water, 85)
thr_turb = percentile_threshold(NDTI, valid_water, 85)
thr_red = percentile_threshold(RED_EXCESS, valid_water, 85)

# ============================================================
# CLASSIFICATION
# ============================================================

classification = np.zeros_like(b03, dtype=np.uint8)

classification[valid_water] = 1
classification[(NDTI > thr_turb)] = 2
classification[(NDCI > thr_chl)] = 3
classification[(FAI > thr_algae)] = 4

# anomaly
mask_anomaly = (
    valid_water &
    (NDTI > thr_turb) &
    (RED_EXCESS > thr_red) &
    (NDCI < thr_chl)
)

classification[mask_anomaly] = 5

# ============================================================
# EXPORT
# ============================================================

print("Saving outputs...")

save_byte(classification, profile, os.path.join(output_dir, "classification.tif"))

save_rgb(
    np.where(valid_water, turb_norm, 0),
    np.where(valid_water, chl_norm, 0),
    np.where(valid_water, algae_norm, 0),
    profile,
    os.path.join(output_dir, "rgb_composite.tif")
)

print("\nDone.")
print("Output folder:", output_dir)