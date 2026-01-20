# CARLA Scenario Generation Pipeline

This document provides instructions on how to set up and run the CARLA Scenario Generation Pipeline using the provided Docker environment.

## Overview

The project is designed to generate, run, and validate driving scenarios in the [CARLA Simulator](https://carla.org/). It uses a containerized environment to ensure all dependencies and configurations are consistent. The pipeline includes various scripts for processing map data (from OpenStreetMap), generating scenes, managing scenarios, and interacting with the CARLA simulator.

## Prerequisites

Before you begin, ensure you have the following installed and configured on your host machine:

1.  **Docker Engine:** [Installation Guide](https://docs.docker.com/engine/install/)
2.  **NVIDIA GPU:** A dedicated NVIDIA graphics card is required.
3.  **NVIDIA Graphics Drivers:** Ensure you have the latest proprietary NVIDIA drivers for your GPU.
4.  **NVIDIA Container Toolkit:** This is necessary to provide the Docker container with access to the host's GPU. [Installation Guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
5.  **An X11 Server:** The container forwards a GUI, so you must be running on a system with an X server.

## Installation

The Docker image contains all the necessary dependencies, including Python, `osmium-tool`, and the required Python packages.

To build the Docker image, run the provided shell script. This will create an image tagged as `carlatest:latest`.

```bash
# Make the script executable
chmod +x build_docker.sh

# Run the build script
./build_docker.sh
```

## Run Docker

The `run_docker.sh` script is configured to launch the container with the necessary settings for GPU access, network configuration, and GUI forwarding.

**Note:** The script forwards your `GEMINI_API_KEY` environment variable into the container. Ensure it is set on your host machine before running the script.

```bash
# Make the script executable
chmod +x run_docker.sh

# Run the launch script
./run_docker.sh
```

This will drop you into an interactive `bash` shell inside the container, in the `/home/carla` directory.

### Understanding the Run Script

The `run_docker.sh` script includes several important flags:

-   `--gpus all`: Provides the container with access to all available host GPUs.
-   `--net=host`: Shares the host's network stack with the container. This is required for the CARLA server and clients to communicate.
-   `-e DISPLAY=$DISPLAY` & `-v /tmp/.X11-unix...`: Forwards the host's display, allowing you to view GUI applications running inside the container (e.g., the CARLA spectator view).
-   `-e GEMINI_API_KEY="..."`: Passes the Gemini API key to the container.
-   Other flags (`--privileged`, `-e NVIDIA_DRIVER_CAPABILITIES`, etc.) are set to ensure proper functioning of the graphics drivers within the container.

## Run the Pipeline

Once inside the container's shell, you can execute the various pipeline scripts. To run the pipeline, move to `/home/carla/PythonAPI/util/` within the container.

```bash
# Navigate to the directory containing the scripts
cd /home/carla/PythonAPI/util/
```

To run the pipeline from the crash reports, You need to download the reports first from Get Crash Details API of [NHTSA Crash Viewer](https://crashviewer.nhtsa.dot.gov/CrashAPI)

The sample API is: 

https://crashviewer.nhtsa.dot.gov/CrashAPI/crashes/GetCaseDetails?stateCase=510003&caseYear=2023&state=51&format=xml

You need to provide the `stateCase` Number, `caseYear` and the `state` number in the designated place to view that specific crash case.
Before working with the NHTSA Crash Viewer, I would suggest to give some time to understand how the APIs work.

After downloading the reports, put all the crash reports in the `/home/carla/PythonAPI/util/data/reports` directory. When putting the reports in this directory, you must follow the naming convension "crash_<crash_number>.xml". Some sample reports have alrady been provided in this directory so that you can directly run the pipeline without downloading the reports.

A bash file is already created to run the whole pipeline. Once you are in `/home/carla/PythonAPI/util/`, run

```bash
# Generates the maps and invokes the LLM to get the vehicles' initial state for all the reports provided in the `/home/carla/PythonAPI/util/data/reports` directory
./generate_map.sh
```

Once you are done with this step, you can run the following command with the specific crash id to run the simulation in carla.

```bash
# Generates the scene, opens CARLA Engine, load the map and simulate the vehicles. Also saves the trajectory and vehicles' state for future use.
./generate_scene.sh <crash_id>
```

If you want to simulate the already created scene again, run
```bash
# loads the previously created scene and run in carla simulator.
./run_scenario.sh <crash_id>
```

If you like, please refer to the bash scripts to understand the execution order of the scripts.


## Working with the Pipeline without Docker

If you do not want to use the docker and use the scripts in your own CARLA repository, you need to put all the `.py` scripts in `your_carla_root/PythonAPI/util` and you are good to go.