import os
import ns_SV_nonjunction
import ns_SV_junction


def spawn_vehicle():

    crash_id = 510164
    xodr_dir = "ns-maps/clipped_merged_xodr"
    points_dir = 'points/scene_points'
    summary_dir = 'crashes/summary'
    final_scene_dir = 'Simulations'

    xodr_path = os.path.join(xodr_dir, f"map_{crash_id}.xodr")
    points_path = os.path.join(points_dir, f"scenepoints_{crash_id}.json")
    summary_path = os.path.join(summary_dir, f"summary_{crash_id}.txt")
    simulation_path = os.path.join(final_scene_dir, f"simulation_{crash_id}.json")

    with open(summary_path, "r") as file:
        lines = file.readlines()

    intersection =  True

    for line in lines:
        if  "Collision Place" in line:
            if line.split(":")[-1].strip().lower() == "not an intersection":
                intersection = False
    
    if intersection:
        route_dir = "points/routes"
        route_path = os.path.join(route_dir, f"route_{crash_id}.json")
        ns_SV_junction.spawn_vehicle(xodr_path, points_path, route_path, summary_path, simulation_path)
    else:
        ns_SV_nonjunction.spawn_vehicle(xodr_path, points_path, summary_path, simulation_path)


if __name__ == '__main__':
    spawn_vehicle()
   
    