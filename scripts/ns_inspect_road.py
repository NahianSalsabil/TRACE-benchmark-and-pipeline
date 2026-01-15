import carla
import time

def live_inspector():
    # 1. Connect to CARLA
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()
    carla_map = world.get_map()
    spectator = world.get_spectator()

    print("Live Inspector Started. Fly around the map to see Road IDs.")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            # 2. Get where the camera is looking
            # We project a point 10 meters in front of the camera
            transform = spectator.get_transform()
            location = transform.location
            forward_vec = transform.get_forward_vector()
            
            target_loc = location + (forward_vec * 10) # Look 10m ahead
            
            # 3. Ask the map: "What lane is here?"
            # project_to_road=True snaps the point to the nearest drivable lane
            waypoint = carla_map.get_waypoint(target_loc, project_to_road=True, lane_type=carla.LaneType.Any)

            if waypoint:
                # 4. Extract Data
                r_id = waypoint.road_id
                l_id = waypoint.lane_id
                s_val = waypoint.s
                
                # 5. Draw it on the screen (in the 3D world)
                # Draw a text string at the waypoint location
                debug_text = f"Road: {r_id} | Lane: {l_id}"
                text_location = waypoint.transform.location + carla.Location(z=2.0)
                
                # Draw Red Text
                world.debug.draw_string(
                    location = text_location, 
                    text = debug_text, 
                    draw_shadow=True,
                    color=carla.Color(r=255, g=255, b=255),
                    life_time=0.1,
                    persistent_lines=True
                )
                
                # Draw a point on the road so you know exactly which lane is picked
                world.debug.draw_point(
                    waypoint.transform.location, 
                    size=0.1, 
                    color=carla.Color(0, 255, 0), 
                    life_time=0.1
                )

            time.sleep(0.05) # Update 20 times per second

    except KeyboardInterrupt:
        print("\nInspector stopped.")

if __name__ == '__main__':
    live_inspector()