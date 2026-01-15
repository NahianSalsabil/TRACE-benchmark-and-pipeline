import carla
import os
from settings import SEGMENTS_DIR

client = carla.Client('localhost', 2000)
world = client.get_world()

#take input from a file with multiple x,y pairs
with open(os.path.join(SEGMENTS_DIR, f"segments_{510009}.txt"), 'r') as f:
    lines = f.readlines()

for i in range(len(lines)):
    
    x_point = float(lines[i].strip().split(',')[0])
    y_point = float(lines[i].strip().split(',')[1])


    world.debug.draw_box(
        carla.BoundingBox(carla.Location(x=x_point, y=y_point, z=0.5), carla.Vector3D(0.5, 0.5, 5.0)),
        carla.Rotation(0, 0, 0),
        0.1,  # Line thickness
        carla.Color(255, 0, 0, 255), 
        120.0 # Life time in seconds
    )

    world.debug.draw_string(
        # Location: Use the same location as the box (or slightly offset it)
        location=carla.Location(x=x_point, y=y_point, z=0.5 + 5.5), 
        text=str(i+1), 
        draw_shadow=True, 
        color=carla.Color(0, 255, 0, 255), 
        life_time=120.0
    )


print("Marker is now at the given point.")
