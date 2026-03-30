| | | |
|:---:|:---:|:---:|
| ![crash_510002](samples/crash_510002.gif) | ![crash_510352](samples/crash_510352.gif) | ![crash_510003](samples/crash_510003.gif) |
| ![crash_510121](samples/crash_510121.gif) | ![crash_510099](samples/crash_510099.gif) | ![crash_510294](samples/crash_510294.gif) |

# CARLA Crash Scenario Reconstruction and Benchmark

This project provides a complete pipeline for reconstructing real-world traffic crash scenarios from the [NHTSA Crash Viewer](https://crashviewer.nhtsa.dot.gov/CrashAPI) and simulating them in the [CARLA Simulator](https://carla.org/). It includes tools for processing crash reports, generating maps, creating simulation scenarios, and running the resulting benchmarks.


## Project Structure

The repository is divided into two main components:

*   **`Reconstruction-Pipeline/`**: A Dockerized environment containing all the scripts and tools necessary to process raw crash data (in XML format) and convert it into a runnable CARLA scenario. This pipeline:
    *   Parses NHTSA crash reports.
    *   Generates CARLA-compatible maps (`.xodr`) from OpenStreetMap data corresponding to the crash location.
    *   Leverages a Large Language Model (Google Gemini) to interpret the crash summary and determine initial vehicle states (position, speed, direction).
    *   Outputs simulation files (`.json`) that define the scenario.

*   **`Benchmark/`**: Contains the pre-generated outputs of the `Reconstruction-Pipeline`. This directory serves as a collection of ready-to-run crash scenarios. It is structured as follows:
    *   `reports/`: The original XML crash reports from NHTSA.
    *   `summary/`: Text summaries of the crash reports.
    *   `maps/`: The `.xodr` map files for each scenario.
    *   `simulations/`: The `.json` files defining the vehicle trajectories and events for the simulation.

*   **`Prompt/`**: Contains the prompt engineering artifacts and directive files used by the reconstruction pipeline's LLM stage. It consists of four files:
    *   `directives.txt`: Master instructions and critical traffic rules (e.g., region, right-hand traffic) used to constrain LLM outputs.
    *   `input_data.txt`: Structured input template describing how crash report summaries and road topologies are fed into the LLM, including the fields and format expected.
    *   `reasoning_steps.txt`: Step-by-step reasoning instructions that guide the LLM through interpreting crash summaries and determining vehicle states.
    *   `output_format.txt`: Defines the expected JSON output schema for the LLM response, ensuring simulation-ready structured output.

The `Prompt/` directory is not required to run pre-generated benchmarks in `Benchmark/`, but it documents the prompts used to create the benchmark and provides the templates needed to reconstruct more scenarios using the TRACE pipeline.

## Getting Started

### Prerequisites

Before you begin, ensure your host machine meets the following requirements:

1.  **Docker Engine:** [Installation Guide](https://docs.docker.com/engine/install/)
2.  **NVIDIA GPU:** A dedicated NVIDIA graphics card is required for running the CARLA simulator.
3.  **NVIDIA Graphics Drivers:** The latest proprietary NVIDIA drivers for your GPU.
4.  **NVIDIA Container Toolkit:** To enable GPU access within Docker. [Installation Guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
5.  **X11 Server:** To display the CARLA simulator GUI from within the container.
6.  **Google Gemini API Key:** Required for the reconstruction pipeline to generate scenarios.

### Installation

Clone the repository to your local machine:
```sh
git clone https://github.com/NahianSalsabil/carla-benchmark.git
cd carla-benchmark
```

## How to Run a Benchmark Demo

The `Benchmark/` directory contains scenarios that are ready to be simulated. For detailed instructions on how to set up the environment and run a pre-existing scenario, please refer to the [`Benchmark/README.md`](Benchmark/README.md).

## How to Use the Reconstruction Pipeline

The `Reconstruction-Pipeline/` contains all the tools to generate new scenarios from raw NHTSA crash reports. For detailed instructions on building the required Docker environment and using the scripts to generate a new scenario, please see the [`Reconstruction-Pipeline/README.md`](Reconstruction-Pipeline/README.md).

## Dependencies

The core dependencies are managed within the Dockerfile. Key components include:

*   **CARLA Simulator:** Version 0.9.15
*   **Python:** Version 3.8
*   **Python Libraries:** `numpy`, `pandas`, `pyproj`, `shapely`, `carla`, `google-generativeai`, `lxml`, and more listed in `Reconstruction-Pipeline/requirements.txt`.

## Comparison of Recent Crash Reconstruction Frameworks

| Comparison Factor | **TRACE** (Ours) | CrashAgent | SAFE | AC3R | AccidentSim | SoVAR |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Open Source** | **Yes** | No | Yes | Yes | No | Yes |
| **Crash Data Sources** | NHTSA Crash Data (XML) | NHTSA CISS | NHTSA CIREN | NHTSA Police Reports | NHTSA physical parameters | NHTSA Crash reports |
| **Input Processed** | External map data via report coordinates | Report diagrams (sketches) and text | Report diagrams (sketches) and summaries | Textual only (narrative) | Physical clues and contextual info | Textual only (narrative) |
| **Realism of Road Topology** | **High**: Site-specific OpenStreetMap data | **Moderate**: Reconstructs layouts from sketches | **Moderate**: Custom DSL generates layouts | **Low**: Abstract geometries or generic matching | **High**: High-fidelity 3D models via RoadRunner | **Moderate**: Generalizable scenarios for various maps |
| **Supported Topologies** | Straight, Curve, T-intersection, 4-way | Single roads, Intersections, Interchanges | Straight, Curve, Intersection, T-intersection, Merging | Straight, Curvy, 2-way, T-junction | Intersection, T-junction, Circular, Y-junction, Inclines | Straight, T-junction, Intersection |
| **Reconstruction Methodology** | LLM state estimation + OSM pipeline | Multi-modal VLM agents | RAG + DSL + CoT reasoning | Traditional NLP + Ontology + Kinetics | Fine-tuned LLM + Physical Constraints + NeRF | LLM extraction + Z3 Constraint Solver |
| **Collision Types** | Angle, Front-to-Front, Front-to-Rear, Sideswipe | Angle, Front-to-rear, Sideswipe, Head-on, etc. | Crossing traffic, merging, intersection turns | Frontal, Sideswipe, Straight Path, Turn into path | Head-on, Front/Rear-left/right | Rear-End, Frontal, Front-to-side |
| **Vehicle Maneuvers** | Straight, turn left/right, stop | 42 elements (lane/speed change, U-turn, etc.) | Move Forward, Turn Left, Turn Right | Basic pre-crash actions from ontology | Pre-collision planning + post-collision prediction | Regular (U-turn, lane change) & Abnormal (retrograde) |
| **Collision Validation** | Matches impact points, maneuvers, and location | Optimizes elements to match crash descriptions | User study alignment + self-validation | Checks simulator damaged components vs. report | Fine-tunes LLM for post-collision trajectories | Generates trajectories to meet collision area constraints |
| **Primary Simulator(s)** | **CARLA** | **CARLA** | **MetaDrive, BeamNG** | **BeamNG.research** | **CARLA** | **LGSVL** |

### Table Highlights
*   **TRACE** is fully open-source, unlike CrashAgent and AccidentSim. This makes it one of the high-topology-fidelity frameworks that the research community can freely use, inspect, and extend.
*   **TRACE** automatically retrieves **real-world OpenStreetMap data** for the exact crash coordinates, guaranteeing that the simulated road geometry matches the actual accident site. AccidentSim achieves comparable visual fidelity but requires expensive, manual RoadRunner 3D modelling for every scenario — making it impractical at scale.
*   Unlike AC3R and SoVAR, that work purely from text narratives, or CrashAgent and SAFE, which depend on hand-drawn sketch diagrams, **TRACE** derives spatial context programmatically from **GPS coordinates embedded in the crash report** — removing the need for any manual map construction or diagram interpretation.
*   **TRACE** combines **LLM-based state estimation** with a fully automated **OSM map pipeline**, a methodology not replicated by any other framework. This allows the LLM to reason about vehicle behavior within a geospatially accurate environment rather than an abstract or sketch-derived one.
*   **TRACE** validates reconstructions by simultaneously checking **impact points, vehicle maneuvers, and crash location**, making its ground-truth alignment more comprehensive than frameworks that check only component damage (AC3R), optimize textual descriptions (CrashAgent), or constrain collision areas geometrically (SoVAR).
*   **TRACE** targets **CARLA**, the most widely adopted open autonomous-driving simulator, ensuring broad hardware compatibility and access to a large existing ecosystem of sensors, agents, and evaluation tools — an advantage over frameworks using BeamNG, MetaDrive, or the discontinued LGSVL.

