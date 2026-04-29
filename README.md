# Pixel Blue | CASSINI Hackathon

## Index

1. [Project Description](#1-project-description)
2. [Team](#2-team)
3. [Tech Stack](#3-tech-stack)
4. [Project Structure](#4-project-structure)
5. [Next steps](#5-next-steps)

---

## 1 Project Description

- ***Objective***: Monitor global water body health in real time using Copernicus (Sentinel) satellite data.
- ***Problem***: Eutrophication, lack of constant data updates, and absence of early warning systems.
- ***Solution***: Scalable monitoring (updated every 5 days), accessible data, and instant anomaly notifications (chlorophyll, turbidity, algae blooms).
- ***Challenge***: Challenge 3 - Water quality monitoring.
- ***Live Demo***: The production tool is available at [cassini.tonilogar.com](https://cassini.tonilogar.com/) (hosted on [tonilogar.com](https://tonilogar.com/)).
- ***File References***:
    - Open the presentation [BluePixel.pdf](./001_documentation/BluePixel.pdf)

[←Index](#index)

## 2 Team

- ***[Ivan Pantaleoni](https://www.linkedin.com/in/ivan-pcm/)***: Geologist & Earth Observation Expert.
- ***[Ameneh Alcalá](https://www.linkedin.com/in/ameneh-alcala/?skipRedirect=true)***: Urban Planner, Researcher & GIS Expert.
- ***[Antonio López](https://www.linkedin.com/in/tonilogar/)***: Full-Stack Developer, Data Science & GIS Expert.

[←Index](#index)

## 3 Tech Stack

- ***Local Lab (Geo-AI Processing)***:
    - Use Docker to isolate GDAL and PyTorch dependencies.
    - Implement windowed reading (512x512) for massive GeoTIFFs.
    - Execute strictly in WSL (Linux) environments.
- ***Production MVP***:
    - Orchestrate services using Docker Compose.
    - Deploy frontend with SvelteKit, Vite, MapLibre-GL-JS, and PMTiles.
    - Serve dynamic data (COGs) using Titiler.

[←Index](#index)

## 4 Project Structure

- ***File References***:
    - Read guides in [001_documentation/](./001_documentation/)
    - Process data in [002_local_processes/](./002_local_processes/)
    - Deploy infrastructure via [003_MVP/](./003_MVP/)
    - Edit the viewer at [sentinel-viewer/](./003_MVP/sentinel-viewer/)
    - Run automations with [dev_run.sh](./003_MVP/dev_run.sh)

[←Index](#index)

## 5 Next steps

- [000_tips](./001_documentation/000_tips.md)