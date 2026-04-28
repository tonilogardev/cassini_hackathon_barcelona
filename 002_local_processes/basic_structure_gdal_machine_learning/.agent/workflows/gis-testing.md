---
description: Guidelines for testing Geospatial capabilities efficiently without bloating the repository with large TIFF files.
---

# GIS Testing Standards

## Index
1. [Data Mocking](#1-data-mocking)
2. [Coordinate Reference Systems (CRS)](#2-coordinate-reference-systems-crs)

---

## 1 Data Mocking
- ***Instruction***: NEVER commit large `.tif` or satellite imagery binaries to the repository.
- ***Visuals***: None
- ***File References***:
    - Example in [tests/test_handler.py](../tests/test_handler.py) (to be created)

Use `rasterio.MemoryFile` and `numpy` arrays to simulate geodata during tests:
```python
import numpy as np
import rasterio
from rasterio.transform import from_origin

def create_mock_raster():
    transform = from_origin(0, 0, 10, 10)
    # create in-memory raster for testing...
```

[←Index](#index)

## 2 Coordinate Reference Systems (CRS)
- ***Instruction***: Every test involving the `SatelliteImageHandler` must explicitly verify that the output tensor or cropped raster strictly preserves the original `EPSG` code and `transform`.
- ***Visuals***: None
- ***File References***:
    - [src/data/handler.py](../src/data/handler.py)

[←Index](#index)
