import carla
import datetime
import pytz
from pysolar import solar
import time
import pandas as pd
import pvlib

def set_sun_position(year, month, day, hour, minute, second, latitude, longitude, 
    timezone_name = 'UTC',
    carla_host = 'localhost', 
    carla_port= 2000
):
   
    print("--- Starting Sun Position Script ---")
    
    try:
        # Get the timezone object
        local_tz = pytz.timezone(timezone_name)
        
        # Create a naive datetime object
        naive_dt = datetime.datetime(year, month, day, hour, minute, second)
        
        # Make the datetime object timezone-aware
        t_aware = local_tz.localize(naive_dt)
        
        # Pysolar expects UTC, so convert the timezone-aware time to UTC
        t_utc = t_aware.astimezone(pytz.utc)
        
        print(f"Time to use for calculation (UTC): {t_utc}")
        
        
    except pytz.UnknownTimeZoneError:
        print(f"Error: Unknown timezone name '{timezone_name}'. Using UTC instead.")
        t_utc = datetime.datetime(year, month, day, hour, minute, second, tzinfo=pytz.utc)
    except ValueError as e:
        print(f"Error creating datetime object: {e}")
        return

    # --- 2. Calculate Solar Position (Altitude and Azimuth) ---
    try:
        # Altitude: The angle above the horizon. CARLA uses this directly.
        altitude_deg = solar.get_altitude(latitude, longitude, t_utc)
        
        azimuth_deg = solar.get_azimuth(latitude, longitude, t_utc)
        
        print(f"Calculated Sun Altitude: {altitude_deg:.2f}°")
        print(f"Calculated Sun Azimuth (from North): {azimuth_deg:.2f}°")
        
    except Exception as e:
        print(f"Error during solar calculation: {e}")
        return

    # --- 3. Connect to CARLA and Apply Settings ---
    try:
        client = carla.Client(carla_host, carla_port)
        client.set_timeout(10.0)
        world = client.get_world()
        
        # Get current weather to keep other settings consistent (like cloudiness)
        current_weather = world.get_weather()

        # Create new weather parameters
        custom_weather = carla.WeatherParameters(
            cloudiness=current_weather.cloudiness,
            precipitation=current_weather.precipitation,
            wind_intensity=current_weather.wind_intensity,
            fog_density=current_weather.fog_density,
            wetness=current_weather.wetness,
            precipitation_deposits=current_weather.precipitation_deposits,
            sun_altitude_angle=altitude_deg,  # Use the calculated Altitude
            sun_azimuth_angle=azimuth_deg    # Use the calculated Azimuth
        )

        # Apply the new weather settings
        world.set_weather(custom_weather)
        

        print(f"\nSuccessfully set CARLA sun position:")
        print(f"  CARLA Altitude: {altitude_deg:.2f}°")
        print(f"  CARLA Azimuth: {azimuth_deg:.2f}°")
        
    except carla.World.TimeoutException:
        print(f"\nError: Could not connect to CARLA at {carla_host}:{carla_port}. Is the simulator running?")
    except Exception as e:
        print(f"\nAn error occurred while setting CARLA weather: {e}")

if __name__ == '__main__':
    
    with open('crashes/summary/summary_510149.txt') as file:
        lines = file.readlines()
    
    for line in lines:
        if "Date" in line:
            target_year = 2023
            target_day = int(line.strip().split(" ")[1])
            target_month = line.strip().split(" ")[2]
            datetime_object = datetime.datetime.strptime(target_month, "%B")
            target_month = datetime_object.month
        if "Time" in line:
            target_hour = int(line.split(":")[1].strip())
            target_minute = int(line.split(":")[2].strip())
            target_second = 0
        if "Latitude" in line:
            target_lat = float(line.split(":")[1].strip())
        if "Longitude" in line:
            target_lon = float(line.split(":")[1].strip())
        target_tz = 'America/New_York'

    set_sun_position(
        target_year, target_month, target_day, 
        target_hour, target_minute, target_second, 
        target_lat, target_lon, 
        target_tz
    )
    
    # Wait for a moment to confirm the settings were applied
    time.sleep(2)
    print("--- Script Finished ---")