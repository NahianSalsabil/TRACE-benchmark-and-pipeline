""" Convert OpenStreetMap file to OpenDRIVE file. """

import argparse
import glob
import os
import sys

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla


def convert(args, osm_file, xodr_file, header_file):
    print("in")
    # Read the .osm data
    with open(osm_file, mode="r", encoding="utf-8") as osmFile:
        osm_data = osmFile.read()

    # Define the desired settings
    settings = carla.Osm2OdrSettings()

    # Set OSM road types to export to OpenDRIVE
    settings.set_osm_way_types([
        "motorway",
        "motorway_link",
        "trunk",
        "trunk_link",
        "primary",
        "primary_link",
        "secondary",
        "secondary_link",
        "tertiary",
        "tertiary_link",
        "unclassified",
        "residential"
    ])
    settings.default_lane_width = args.lane_width
    settings.generate_traffic_lights = args.traffic_lights
    settings.all_junctions_with_traffic_lights = args.all_junctions_lights
    settings.center_map = args.center_map

    # Convert to .xodr
    xodr_data = carla.Osm2Odr.convert(osm_data, settings)

    with open(header_file, "r", encoding="utf-8") as hfile:
        header = hfile.read()

    start_index = xodr_data.find("<header")
    end_index = xodr_data.find("</header>") + len("</header>")
 
    if start_index != -1 and end_index != -1:
        new_xodr_data = xodr_data[:start_index] + header + xodr_data[end_index:]   

    with open(xodr_file, "w", encoding="utf-8") as xodrFile:
        xodrFile.write(new_xodr_data)
        print(f"content written to {xodrFile}")


# ==============================================================================
# -- main() --------------------------------------------------------------------
# ==============================================================================


def main():
    argparser = argparse.ArgumentParser(
        description=__doc__)
    argparser.add_argument(
        '-id', '--input-dir',
        metavar='osm_file_dir',
    )
    argparser.add_argument(
        '-od', '--output-dir',
        metavar='xodr_file_dir',
    )
    argparser.add_argument(
        '-hd', '--header-dir',
        metavar='header_file_dir',
    )
    argparser.add_argument(
        '-i', '--input-path',
        metavar='OSM_FILE_DIR',
        help='set the input OSM file path')
    argparser.add_argument(
        '-o', '--output-path',
        metavar='XODR_FILE_DIR',
        help='set the output XODR file path')
    argparser.add_argument(
        '-hr', '--header-path',
        metavar='Header_FILE_DIR',
        help='set the header file path')
    argparser.add_argument(
        '--lane-width',
        default=6.0,
        help='width of each road lane in meters')
    argparser.add_argument(
        '--traffic-lights',
        action='store_true',
        help='enable traffic light generation from OSM data')
    argparser.add_argument(
        '--all-junctions-lights',
        action='store_true',
        help='set traffic lights for all junctions')
    argparser.add_argument(
        '--center-map',
        action='store_true',
        help='set center of map to the origin coordinates')


    if len(sys.argv) < 2:
        argparser.print_help()
        return

    args = argparser.parse_args()


    osm_dir = args.input_dir
    xodr_dir = args.output_dir
    header_dir = args.header_dir

    os.makedirs(xodr_dir, exist_ok=True)

    for filename in os.listdir(osm_dir):
        if filename == "map_510070_edited.osm":
            try:
                print(f"{filename} started conversion\n")
                osm_path = os.path.join(osm_dir, filename)
                xodr_file = filename.replace("_edited.osm", ".xodr")
                xodr_path = os.path.join(xodr_dir, xodr_file)
                header_file = filename.replace("_edited.osm", "_header.txt")
                header_path = os.path.join(header_dir, header_file)
                convert(args, osm_path, xodr_path, header_path)
                
            except Exception as e:
                print('\nAn error has occurred in conversion.', e)

if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')
    except RuntimeError as e:
        print(e)
