import os

osm_dir = "ns-maps/mv_elevation_passed"
bbox_dir = "ns-maps/bbox"

command_file = "ns-maps/command_osmium.txt"


with open(command_file, "w", encoding="UTF-8") as c_file:
    file_count = 0
    for filename in os.listdir(osm_dir):
        try:
            print(f"Processing {filename}.")
            crash_id = filename.split('_')[1].split(".")[0]
            with open(os.path.join(bbox_dir, f"bbox_{crash_id}.txt")) as file:
                    max_lat = file.readline().split(':')[1].strip()
                    max_lon = file.readline().split(':')[1].strip()
                    min_lat = file.readline().split(':')[1].strip()
                    min_lon = file.readline().split(':')[1].strip()

                    command = "osmium extract -b " + min_lon + "," + min_lat + "," + max_lon + "," + max_lat
                    command += " ns-maps/osm/map_" + crash_id + ".osm -o ns-maps/clipped_osm/map_" + crash_id + ".osm" 
                    c_file.write(crash_id)
                    c_file.write("\n")
                    c_file.write(command)
                    c_file.write("\n\n")
            file_count += 1
        except Exception as e:
             print(e)
print(f"Processed {file_count} files.")