## Directory Structure

*   `reports/`: Contains XML files of the crash reports downloaded from [NHTSA Crash Viewer](https://crashviewer.nhtsa.dot.gov/CrashAPI).

*   `summary/`: Contains text files summarizing the reports with all the relevant information needed to reconstruct the crash incident.

*   `maps/`: Contains the OpenDRIVE map files (`.xodr`) used in the simulations.

*   `simulations/`: Contains JSON files that define the simulation scenarios with vehicles' starting position, direction, speed and the trajectory waypoints.

## Use the Benchmark
To work with these benchmarks, you need to copy this folder into `your_carla_route/PythonAPI/util/` along with all the scripts of the `Reconstruction-Pipeline/scripts`.

After copying, navigate to the `util` directory and run the bash script `run_scenario.sh`.

If you wish to change the agent to one of your custom agents, you will need to:
1. Import your agent's class into `ns_SV_junction.py` and `ns_SV_nonjunction.py`.
2. Initialize your agent's class within these files.