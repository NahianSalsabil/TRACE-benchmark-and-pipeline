To work with these benchmarks, you need to copy this folder into `your_carla_route/PythonAPI/util/` along with all the scripts of the pipeline.

After copying, navigate to the `util` directory and run the bash script `run_scenario.sh`.

If you wish to change the agent to one of your custom agents, you will need to:
1. Import your agent's class into `ns_SV_junction.py` and `ns_SV_nonjunction.py`.
2. Initialize your agent's class within these files.