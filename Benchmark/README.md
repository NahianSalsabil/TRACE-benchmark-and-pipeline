To work with these benchmarks, you need to copy this folder into `your_carla_route/PythonAPI/util/` along with all the scripts of the pipeline.

After copying, navigate to the `util` directory and run the bash script `run_scenario.sh`.

If you wish to change the agent to one of your custom agents, you will need to:
1. Import your agent's class into `ns_SV_junction.py` and `ns_SV_nonjunction.py`.
2. Initialize your agent's class within these files.

## Directory Structure

*   `maps/`: Contains the OpenDRIVE map files (`.xodr`) used in the simulations.
*   `reports/`: Contains XML files with detailed reports of any crashes that occurred during the simulations.
*   `simulations/`: Contains JSON files that define the simulation scenarios.
*   `summary/`: Contains text files summarizing the results of each simulation run.