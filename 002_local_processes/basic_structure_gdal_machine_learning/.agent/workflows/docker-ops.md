---
description: Manage Docker operations securely and efficiently, specifically handling CUDA, GDAL, and volume mounting for the antigravity-geo-ml project.
---

# Docker Operations Strategy

## Index
1. [Build Process](#1-build-process)
2. [Running the Container](#2-running-the-container)
3. [Environment Variables](#3-environment-variables)

---

## 1 Build Process
- ***Instruction***: Always use BuildKit to optimize caching. Use `docker compose` to manage the build process.
- ***Visuals***: None
- ***File References***: 
    - Verify [docker-compose.yml](../docker-compose.yml)

```bash
DOCKER_BUILDKIT=1 docker compose build
```
[←Index](#index)

## 2 Running the Container
- ***Instruction***: Always execute commands using `docker compose run --rm cli`.
- ***Visuals***: None
- ***File References***:
    - Use [run_project.sh](../run_project.sh) for initial setup.

```bash
docker compose run --rm cli --help
```
[←Index](#index)

## 3 Environment Variables
- ***Instruction***: Do NOT override `GDAL_DATA` or `PROJ_LIB` unless absolutely necessary, as they are hardcoded in the Dockerfile for the C++ bindings.
- ***Visuals***: None
- ***File References***: None

[←Index](#index)
