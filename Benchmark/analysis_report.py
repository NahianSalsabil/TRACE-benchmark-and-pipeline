import os
import sys
import glob
import argparse


T_intersection = []
Four_Way_intersection = []
Not_an_intersection = []
others_road_topology = []
F_R = []
F_F = []
Angle = []
sideswipe_same_dir = []
sideswipe_oppos_dir = []
rear_to_side = []
rear_to_rear = []
others_type_of_collision = []
same_tway_same_dir = []
same_tway_oppos_dir = []
chang_tway_veh_turning = []
intersecting_paths = []
others_trajectories = []

def parse_report(file_path):
    """
    Parses a single crash report file to check:
    1. Intersection status (True if intersection, False if not)
    2. V1 and V2 movement info presence
    
    Returns a tuple: (is_intersection, has_v1_info, has_v2_info)
    """

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    found_place = False
    found_manner = False
    found_traj = False

    for line in lines:
        if "Collision Place:" in line and not found_place:
            place = line.split(":", 1)[1].strip().lower()
            if "not an intersection" in place:
                Not_an_intersection.append(os.path.basename(file_path))
            elif "t-intersection" in place:
                T_intersection.append(os.path.basename(file_path))
            elif "four-way intersection" in place:
                Four_Way_intersection.append(os.path.basename(file_path))
            else:
                others_road_topology.append(os.path.basename(file_path))
            found_place = True

        if "Manner of Collision:" in line and not found_manner:
            manner = line.split(":")[1].strip().lower()
            if "angle" in manner:
                Angle.append(os.path.basename(file_path))
            elif "front-to-front" in manner:
                F_F.append(os.path.basename(file_path))
            elif "front-to-rear" in manner:
                F_R.append(os.path.basename(file_path))
            elif "sideswipe - same direction" in manner:
                sideswipe_same_dir.append(os.path.basename(file_path))
            elif "sideswipe - opposite direction" in manner:
                sideswipe_oppos_dir.append(os.path.basename(file_path))
            elif "rear-to-side" in manner:
                rear_to_side.append(os.path.basename(file_path))
            elif "rear-to-rear" in manner:
                rear_to_rear.append(os.path.basename(file_path))
            else:
                others_type_of_collision.append(os.path.basename(file_path))
            found_manner = True
    
        if "Accident Type:" in line and not found_traj:
            trajectory = line.split(":")[1].strip().lower()
            if "same trafficway, same direction" in trajectory:
                same_tway_same_dir.append(os.path.basename(file_path))
            elif "same trafficway, opposite direction" in trajectory:
                same_tway_oppos_dir.append(os.path.basename(file_path))
            elif "changing trafficway, vehicle turning" in trajectory:
                chang_tway_veh_turning.append(os.path.basename(file_path))
            elif "intersecting paths" in trajectory:
                intersecting_paths.append(os.path.basename(file_path))
            else:
                others_trajectories.append(os.path.basename(file_path))
            found_traj = True


def main():
    # 1. Argument Parsing
    argparser = argparse.ArgumentParser(
        description=__doc__)
    argparser.add_argument(
        '-id', '--input-dir',
        metavar='report_dir',
    )
    args = argparser.parse_args()

    input_dir = args.input_dir

    if not os.path.isdir(input_dir):
        print(f"Error: Directory '{input_dir}' not found.")
        sys.exit(1)

    files = glob.glob(os.path.join(input_dir, "*.txt"))
    
    if not files:
        print("No .txt files found.")
        sys.exit(0)

    print(f"Processing {len(files)} files...")

    for file_path in files:
        print(file_path)
        parse_report(file_path)
        

    # Write Output
    output_filename = "crash_coverage_analysis.txt"
    
    with open(output_filename, "w") as out:
        out.write("CRASH COVERAGE ANALYSIS\n")
        out.write("=====================\n\n")
        
        # High Level Summary
        out.write("OVERALL SUMMARY\n")
        out.write(f"Total Reports: {len(files)}\n")


        out.write("\nRoad Topology:\n")
        out.write(f"\t\t Not an Intersection: {len(Not_an_intersection)}\n")
        out.write(f"\t\t T-Intersection: {len(T_intersection)}\n")
        out.write(f"\t\t Four-way Intersection: {len(Four_Way_intersection)}\n")
        out.write(f"\t\t Others: {len(others_road_topology)}\n")

        out.write("\nType of Collision:\n")
        out.write(f"\t\t Angle: {len(Angle)}\n")
        out.write(f"\t\t Front-to-Front: {len(F_F)}\n")
        out.write(f"\t\t Front-to-Rear: {len(F_R)}\n")
        out.write(f"\t\t Sideswipe, Same Direction: {len(sideswipe_same_dir)}\n")
        out.write(f"\t\t Sideswipe, Opposite Direction: {len(sideswipe_oppos_dir)}\n")
        out.write(f"\t\t Rear-to-Side: {len(rear_to_side)}\n")
        out.write(f"\t\t Rear-to-Rear: {len(rear_to_rear)}\n")
        out.write(f"\t\t Others: {len(others_type_of_collision)}\n")

        out.write("\nVehicle Trajectory:\n")
        out.write(f"\t\t Same Trafficway, Same Direction: {len(same_tway_same_dir)}\n")
        out.write(f"\t\t Same Trafficway, Opposite Direction: {len(same_tway_oppos_dir)}\n")
        out.write(f"\t\t Changing Trafficway, Vehicle Turning: {len(chang_tway_veh_turning)}\n")
        out.write(f"\t\t Intersecting Paths: {len(intersecting_paths)}\n")
        out.write(f"\t\t Others: {len(others_trajectories)}\n")



        out.write("\n" + "="*50 + "\n\n")
        
    print(f"Analysis complete. Results written to: {output_filename}")

if __name__ == "__main__":
    main()