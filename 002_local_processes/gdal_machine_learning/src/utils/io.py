import rasterio

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

def save_text(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(str(line) + "\n")
