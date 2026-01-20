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

## How to Run

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

## Usage

Once inside the container's shell, you can execute the various pipeline scripts. The project's scripts from the `scripts` directory have been moved to `/home/carla/PythonAPI/util/` within the container.

You can run the scripts as needed. For example:

```bash
# Navigate to the directory containing the scripts
cd /home/carla/PythonAPI/util/

# Example of running a script
python3.8 ns_check_points.py [arguments]
```

Please refer to the individual scripts and the project documentation for the specific order of execution and required arguments.
