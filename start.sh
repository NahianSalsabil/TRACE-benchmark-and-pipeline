#!/bin/bash

HOME="/home/carla"
DATA_DIR="/home/carla/app/data"

echo "Starting Carla Engine..."
./CarlaUE4.sh &

echo "Loading Map..."
python3.8 PythonAPI/util/config.py -x="$DATA_DIR/maps/clipped_merged_xodr/map_510002.xodr"

echo "Generating Scenario..."
python3.8 "$HOME/PythonAPI/util/ns_spawn_vehicle.py"


