import numpy as np
from rasterio.warp import reproject, Resampling

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
