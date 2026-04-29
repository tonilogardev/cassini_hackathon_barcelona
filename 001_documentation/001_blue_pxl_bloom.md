# Blue Pixel Bloom Analysis

## Index

1. [Overview](#1-overview)
2. [Configuration](#2-configuration)
3. [Execution](#3-execution)
4. [Outputs](#4-outputs)

---

## 1 Overview

- ***Purpose***: Process Sentinel-2 imagery to detect water quality anomalies (Chlorophyll, Turbidity, Algae Blooms) and classify water bodies.
- ***File References***:
    - View script [blue_pxl_bloom.py](../002_local_processes/scripts/blue_pxl_bloom.py)

[←Index](#index)

## 2 Configuration

- ***Instruction***: Edit the input variables inside the script before running.
- ***Variables to Edit***:
    - `BASE_FOLDER`: Path to the project folder containing the data.
    - `PREFIX`: Sentinel-2 image prefix (e.g., `T30SYJ_20191227T105349`).
    - `FORCED_CRS`: Target coordinate system (default: EPSG:32631).

[←Index](#index)

## 3 Execution

- ***Instruction***: Run the script within the Docker machine learning environment.
- ***File References***:
    - Open environment [gdal_machine_learning/](../002_local_processes/gdal_machine_learning/)
    - Run: `python scripts/blue_pxl_bloom.py`

[←Index](#index)

## 4 Outputs

- ***Description***: The script generates two primary GeoTIFF files in the `OUTPUT` directory.
- ***Generated Files***:
    - `classification.tif`: Classified raster (1: Water, 2: Turbidity, 3: Chlorophyll, 4: Algae, 5: Multiple Anomalies).
    - `rgb_composite.tif`: RGB visualization (Red=Turbidity, Green=Chlorophyll, Blue=Algae).

[←Index](#index)

## Next steps
- [002_local_processes.md](./002_local_processes.md)