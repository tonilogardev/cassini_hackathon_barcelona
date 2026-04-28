# Geospatial-AI CLI (antigravity-geo-ml)

## Index

1. [Project Overview](#1-project-overview)
2. [Quickstart](#2-quickstart)
3. [Architecture and Standards](#3-architecture-and-standards)
4. [Next steps](#4-next-steps)

---

## 1 Project Overview

- ***Instruction***: Build a robust, memory-efficient Python CLI for satellite imagery inference.
- ***Visuals***: None
- ***File References***:
    - Review internal AI blueprint [context.md](.antigravity/context.md)

[←Index](#index)

## 2 Quickstart

- ***Instruction***: You MUST use a Linux console (WSL Ubuntu on Windows, native Linux, or macOS terminal). Command Prompt or PowerShell are not supported for this workflow.
- ***Visuals***: None
- ***File References***:
    - Execute [run_project.sh](./run_project.sh) to build and verify.
    - Check [docker-ops.md](.agent/workflows/docker-ops.md) for full Docker guidelines.

```bash
./run_project.sh
```

- ***Instruction***: Run CLI commands using Docker Compose.

```bash
docker compose run --rm cli process data/in.tif data/out.tif
```

[←Index](#index)

## 3 Architecture and Standards

- ***Instruction***: Adhere strictly to the defined project architecture and workflows.
- ***Visuals***: None
- ***File References***:
    - **Models:** Configure inference in [src/models/engine.py](./src/models/engine.py). Follow standard tracking in [mlops-workflow.md](.agent/workflows/mlops-workflow.md).
    - **Data Handling:** Implement windowed CRS-aware reading in [src/data/handler.py](./src/data/handler.py). Refer to [gis-testing.md](.agent/workflows/gis-testing.md) for GeoTIFF testing rules.
    - **CLI Commands:** Add Typer commands in [src/api/cli.py](./src/api/cli.py). 

[←Index](#index)

## 4 Next steps

- [src/main.py](./src/main.py)
