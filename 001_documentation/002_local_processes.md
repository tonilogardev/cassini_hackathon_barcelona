# Local Processes Documentation

## Index

1. [Overview](#1-overview)
2. [Data Processing Environment](#2-data-processing-environment)
3. [Format Transformation](#3-format-transformation)
4. [Machine Learning Environment](#4-machine-learning-environment)

---

## 1 Overview

- ***Purpose***: Test solutions, transform geospatial formats (GDAL/PMTiles), and process satellite data locally.
- ***References***: Based on [basic_structure_gdal_machine_learning](https://github.com/tonilogardev/basic_structure_gdal_machine_learning) and [format_transformation](https://github.com/tonilogardev/web_basic_project/tree/main/007_format_transformation).

[←Index](#index)

## 2 Data Processing Environment

- ***Instruction***: Run Docker to process inputs into outputs without installing local dependencies.
- ***File References***:
    - Edit [docker-compose.yml](../002_local_processes/docker-compose.yml) (Contains `tippecanoe`, `gdal`, `pmtiles`).
    - Place raw data in [input/](../002_local_processes/input/)
    - Retrieve results from [output/](../002_local_processes/output/)

[←Index](#index)

## 3 Format Transformation

- ***Instruction***: Use predefined shell scripts to convert raster and vector data into PMTiles for the frontend viewer.
- ***File References***:
    - Run [raster2pmtiles_001.sh](../002_local_processes/scripts/raster2pmtiles_001.sh)
    - Run [vector_shp_2_pmtiles.sh](../002_local_processes/scripts/vector_shp_2_pmtiles.sh)
    - Download Copernicus data using [connect_CDSE.py](../002_local_processes/scripts/connect_CDSE.py)

[←Index](#index)

## 4 Machine Learning Environment

- ***Instruction***: Use the isolated environment for training and inference with PyTorch and GDAL.
- ***File References***:
    - Open [gdal_machine_learning/](../002_local_processes/gdal_machine_learning/)
    - Build with [Dockerfile](../002_local_processes/gdal_machine_learning/Dockerfile)
    - Check dependencies in [requirements.txt](../002_local_processes/gdal_machine_learning/requirements.txt)

[←Index](#index)

## Next steps
- [003_MVP.md](./003_MVP.md)