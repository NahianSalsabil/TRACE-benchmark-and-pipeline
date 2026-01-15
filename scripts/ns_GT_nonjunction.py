import math
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt


class OpenDRIVEChecker:

    def __init__(self, xodr_data):
        self.road_data, self.junction_data = self._parse_opendrive_data(xodr_data)

    def _parse_geometry(self, geom_element):
            geom_type_element = list(geom_element)[0]
            
            base_data = {
                's': float(geom_element.get('s')),
                'x': float(geom_element.get('x')),
                'y': float(geom_element.get('y')),
                'hdg': float(geom_element.get('hdg')),
                'length': float(geom_element.get('length')),
                'type': geom_type_element.tag
            }

            if geom_type_element.tag == 'line':
                return base_data

            elif geom_type_element.tag == 'paramPoly3':
                poly_data = {
                    'aU': float(geom_type_element.get('aU')),
                    'bU': float(geom_type_element.get('bU')),
                    'cU': float(geom_type_element.get('cU')),
                    'dU': float(geom_type_element.get('dU')),
                    'aV': float(geom_type_element.get('aV')),
                    'bV': float(geom_type_element.get('bV')),
                    'cV': float(geom_type_element.get('cV')),
                    'dV': float(geom_type_element.get('dV')),
                    'pRange': geom_type_element.get('pRange', 'arcLength')
                }
                return {**base_data, **poly_data}

            return None

    def _parse_lanes(self, lane_element):
        width_element = lane_element.find('width')
        # We only extract width 'a' (constant width) for simplicity
        width_a = float(width_element.get('a')) if width_element is not None else 0.0
        
        return {
            'id': int(lane_element.get('id')),
            'type': lane_element.get('type'),
            'width_a': width_a
        }

    def _parse_opendrive_data(self, xodr_xml_string):
        parsed_roads = []
        parsed_junctions = []

        try:
            root = ET.fromstring(xodr_xml_string)
            
            for road_element in root.findall('road'):
                road_data = {
                    'id': int(road_element.get('id')),
                    'name': road_element.get('name'),
                    'length': road_element.get('length'),
                    'junction': int(road_element.get('junction')),
                    'geometry': [],
                    'lane_section': [],
                    'predecessor': (),
                    'successor': ()
                }

                for connection in road_element.findall('link/predecessor'):
                    predecessor_type = connection.get('elementType')
                    predecessor_id = int(connection.get('elementId'))
                    pred = (predecessor_type, predecessor_id)
                    road_data['predecessor'] = pred

                for connection in road_element.findall('link/successor'):
                    successor_type = connection.get('elementType')
                    successor_id = int(connection.get('elementId'))
                    succ = (successor_type, successor_id)
                    road_data['successor'] = succ
                
                # 1. Parse Geometry (planView)
                for geom_element in road_element.findall('planView/geometry'):
                    geom = self._parse_geometry(geom_element)
                    if geom:
                        road_data['geometry'].append(geom)

                # 2. Parse Lane Sections
                for section_element in road_element.findall('lanes/laneSection'):
                    section_data = {'s_offset': float(section_element.get('s')), 'right_lanes': [], 'left_lanes': []}

                    # Parse Right Lanes (Negative IDs)
                    for lane_element in section_element.findall('right/lane'):
                        section_data['right_lanes'].append(self._parse_lanes(lane_element))

                    # Parse Left Lanes (Positive IDs)
                    for lane_element in section_element.findall('left/lane'):
                        section_data['left_lanes'].append(self._parse_lanes(lane_element))

                    road_data['lane_section'].append(section_data)

                parsed_roads.append(road_data)

            for junction_element in root.findall('junction'):
                junction_data = {
                    'id': int(junction_element.get('id')),
                    'name': junction_element.get('name'),
                    'connections': []
                }
                
                for connection_element in junction_element.findall('connection'):
                    connection_data = {
                        'id': int(connection_element.get('id')),
                        'incomingRoad': int(connection_element.get('incomingRoad')),
                        'connectingRoad': int(connection_element.get('connectingRoad')),
                        'contactPoint': connection_element.get('contactPoint'),
                        'lane_links': []
                    }
                    
                    for lane_link_element in connection_element.findall('laneLink'):
                        connection_data['lane_links'].append({
                            'from': int(lane_link_element.get('from')),
                            'to': int(lane_link_element.get('to'))
                        })
                    
                    junction_data['connections'].append(connection_data)
                
                parsed_junctions.append(junction_data)    
            
            print(f"SUCCESS: Parsed {len(parsed_roads)} roads from XODR data.")
            return parsed_roads, parsed_junctions

        except ET.ParseError as e:
            print(f"ERROR: Failed to parse XML string: {e}")
            return []

    def _get_road_width(self, road):
        road_width = 0.0

        # In this simplified model, we only use the laneSection at s=0
        lane_section = road['lane_section'][0] 
        
        for lane in lane_section.get('right_lanes', []):
            if(lane['type'] == "driving"):
                road_width += lane['width_a']

        if road_width == 0:
            for lane in lane_section.get('left_lanes', []):
                if(lane['type'] == "driving"):
                    road_width += lane['width_a']

        return road_width

    def _calculate_closest_point_on_line(self, P, P1, P2):
        V = (P2[0] - P1[0], P2[1] - P1[1])  # Segment vector
        W = (P[0] - P1[0], P[1] - P1[1])  # Vector from P1 to P

        # Calculate the projection parameter 'c1' (Dot product W . V)
        c1 = W[0] * V[0] + W[1] * V[1] 
        c2 = V[0] * V[0] + V[1] * V[1]  # Squared length of segment (V . V)
        

        if c1 <= 0:
            # Projection falls before P1, so P1 is the closest point.
            return P1, 0.0

        t = c1 / c2

        if c2 == 0:
            # P1 and P2 are the same point (zero length), return P1
            return P1, t

        if c1 >= c2:
            # Projection falls after P2, so P2 is the closest point.
            return P2, t

        # Projection falls within P1-P2 segment
        Px = P1[0] + t * V[0]
        Py = P1[1] + t * V[1]
        
        return (Px, Py), t

    def _get_paramPoly3_point_and_tangent(self, geom, u):
        """Calculates (x, y) coordinates, and tangent components (dx/du, dy/du) 
           for a given parameter u on the paramPoly3 geometry."""
        
        # Polynomials for the U and V components of the curve in the local system (u, v)
        # U(u) = aU + bU*u + cU*u^2 + dU*u^3
        U = geom['aU'] + geom['bU']*u + geom['cU']*(u**2) + geom['dU']*(u**3)
        V = geom['aV'] + geom['bV']*u + geom['cV']*(u**2) + geom['dV']*(u**3)
        
        # Derivatives for the local tangent vector (dU/du, dV/du)
        # U'(u) = bU + 2*cU*u + 3*dU*u^2
        dU_du = geom['bU'] + 2*geom['cU']*u + 3*geom['dU']*(u**2)
        # V'(u) = bV + 2*cV*u + 3*dV*u^2
        dV_du = geom['bV'] + 2*geom['cV']*u + 3*geom['dV']*(u**2)
        
        # Rotation matrix (from local u/v to global x/y)
        hdg = geom['hdg']
        cos_hdg = math.cos(hdg)
        sin_hdg = math.sin(hdg)
        
        # Global coordinates (X, Y)
        X = geom['x'] + U * cos_hdg - V * sin_hdg
        Y = geom['y'] + U * sin_hdg + V * cos_hdg
        
        # Global Tangent (T_x, T_y) from local derivatives
        Tx = dU_du * cos_hdg - dV_du * sin_hdg
        Ty = dU_du * sin_hdg + dV_du * cos_hdg

        return (X, Y), (Tx, Ty)

    def _calculate_closest_point_on_paramPoly3(self, P, geom, max_iterations=10, tolerance=1e-5):
        
        P_x, P_y = P
        
        # Initial guess for the parameter u (midpoint of the segment)
        # OpenDRIVE pRange="normalized" means u is between 0 and 1.
        u = 0.5 
        
        for _ in range(max_iterations):
            # 1. Get current point (X, Y) and tangent (Tx, Ty) on the curve at u
            (X, Y), (Tx, Ty) = self._get_paramPoly3_point_and_tangent(geom, u)
            
            # 2. Vector from curve point to query point (V_x, V_y)
            V_x = X - P_x
            V_y = Y - P_y
            
            # 3. Objective function (distance squared derivative w.r.t u): F(u) = (X-Px)*Tx + (Y-Py)*Ty = 0
            # This is the dot product of the vector V (from P to X, Y) and the tangent T.
            F_u = V_x * Tx + V_y * Ty
            
            # 4. Check for convergence
            if abs(F_u) < tolerance:
                # Closest point found, normalize the distance along the length
                s_norm = u # For normalized pRange, s_norm is u
                return (X, Y), s_norm 
            
            # 5. Calculate derivative of F(u): F'(u) (This requires the second derivatives of X and Y w.r.t u)
            # F'(u) = Tx^2 + Ty^2 + (X-Px)*Tx' + (Y-Py)*Ty'
            
            # Since calculating Tx' and Ty' from the rotation is very complex, 
            # we use a simpler approach: the magnitude of the tangent vector squared (||T||^2) as the denominator 
            # for a simple update, often used for path following:
            F_prime_approx = Tx**2 + Ty**2
            
            if F_prime_approx < tolerance: # Flat spot or zero length
                break 

            # 6. Newton's step: u_next = u - F(u) / F'(u)
            delta_u = F_u / F_prime_approx
            u_next = u - delta_u
            
            # 7. Clamp u to the segment boundaries [0, 1]
            u = max(0.0, min(1.0, u_next))
            
            # Check for convergence in u
            if abs(delta_u) < tolerance:
                (X, Y), _ = self._get_paramPoly3_point_and_tangent(geom, u)
                s_norm = u
                return (X, Y), s_norm
        
        # If max iterations reached, return the last calculated point/parameter
        (X, Y), _ = self._get_paramPoly3_point_and_tangent(geom, u)
        s_norm = u
        return (X, Y), s_norm

    def _calculate_point(self, geom, s_iter):
        if geom['type'] == 'line':
            x = geom['x'] + s_iter * math.cos(geom['hdg'])
            y = geom['y'] + s_iter * math.sin(geom['hdg'])
            hdg = geom['hdg']
            return x, y, hdg
        
        elif geom['type'] == 'paramPoly3':
            if geom['pRange'] == 'normalized': u = s_iter / geom['length']
            else: u = s_iter
            
            U = geom['aU'] + geom['bU']*u + geom['cU']*(u**2) + geom['dU']*(u**3)
            V = geom['aV'] + geom['bV']*u + geom['cV']*(u**2) + geom['dV']*(u**3)
            
            dU = geom['bU'] + 2*geom['cU']*u + 3*geom['dU']*(u**2)
            dV = geom['bV'] + 2*geom['cV']*u + 3*geom['dV']*(u**2)
            
            cos_h = math.cos(geom['hdg'])
            sin_h = math.sin(geom['hdg'])
            
            x = geom['x'] + U*cos_h - V*sin_h
            y = geom['y'] + U*sin_h + V*cos_h
            
            tx = dU*cos_h - dV*sin_h
            ty = dU*sin_h + dV*cos_h
            hdg = math.atan2(ty, tx)
            
            return x, y, hdg
        return 0,0,0

    def _calculate_offset_point(self, road, geom, s_iter, side):
        
        ref_x, ref_y, ref_hdg = self._calculate_point(geom, s_iter)
        
        if side == 'right':
            t_offset = -self._get_road_width(road)/2.0
        else:
            t_offset = self._get_road_width(road)/2.0
        
        nx = -math.sin(ref_hdg)
        ny = math.cos(ref_hdg)
        
        final_x = ref_x + (t_offset * nx)
        final_y = ref_y + (t_offset * ny)
        
        return final_x, -final_y
    
    def get_trajectory(self, crash_P, P, road_id, side, step_size, overshoot=0):
        
        road = next((r for r in self.road_data if r['id'] == road_id), None)
        if not road:
            print(f"Error: Road {road_id} not found.")
            return []

        def _find_location_on_road(target_point):
            best_match = {
                'distance': float('inf'),
                'type': None,
                'road_id': None,
                's': None,
                's_local': None,
                't': None,
                'P_ref_x': None,
                'P_ref_y': None,
                'hdg': None,
                'geom_index': -1,
                't_norm': None
            }
            P_x, P_y = target_point

            for i, geom in enumerate(road['geometry']):   
                P_ref, t_norm = None, None
                roadtype = None
                hdg, length = 0.0, geom['length']
                
                if geom['type'] == 'line':
                    P_start = (geom['x'], geom['y'])
                    hdg = geom['hdg']
                    P_end = (
                        geom['x'] + length * math.cos(hdg),
                        geom['y'] + length * math.sin(hdg)
                    )
                    P_ref, t_norm = self._calculate_closest_point_on_line(target_point, P_start, P_end)
                    roadtype = 'line'

                elif geom['type'] == 'paramPoly3':
                    P_ref, t_norm = self._calculate_closest_point_on_paramPoly3(target_point, geom)
                    (_, _), (Tx, Ty) = self._get_paramPoly3_point_and_tangent(geom, t_norm)
                    hdg = math.atan2(Ty, Tx)
                    roadtype = 'parampoly'

                distance = math.sqrt((P_x - P_ref[0])**2 + (P_y - P_ref[1])**2)

                # Check if this geometry is the closest match
                if distance <= best_match['distance']:
                    s_current_geom = t_norm * length
                    s_total = geom['s'] + s_current_geom
                    
                    # Determine orientation relative to road (Forward/Backward check helper)
                    Tx = math.cos(hdg)
                    Ty = math.sin(hdg)
                    Vx = P_x - P_ref[0]
                    Vy = P_y - P_ref[1]
                    signed_distance = distance * math.copysign(1, -(Tx * Vy - Ty * Vx))

                    if 0 <= t_norm <= 1:
                        best_match['type'] = roadtype
                        best_match['distance'] = distance
                        best_match['road_id'] = road_id
                        best_match['s'] = s_total
                        best_match['s_local'] = s_current_geom
                        best_match['t'] = signed_distance
                        best_match['P_ref_x'] = P_ref[0]    #in opendrive coordinate
                        best_match['P_ref_y'] = P_ref[1]    #in opendrive coordinate
                        best_match['geom_index'] = i
                        best_match['t_norm'] = max(0.0, min(1.0, t_norm)) # Clamp for safety
                        if signed_distance < 0:
                            best_match['hdg'] = hdg + math.pi
                        else:
                            best_match['hdg'] = hdg

            return best_match

        # 1. Find Start and Crash Locations
        start_loc = _find_location_on_road(P)
        crash_loc = _find_location_on_road(crash_P)

        if start_loc['geom_index'] == -1 or crash_loc['geom_index'] == -1:
            print("Error: Could not map points to road geometry.")
            return []

        # 2. Determine Direction and Range
        # We add an overshoot buffer (e.g., 20 meters) to drive PAST the crash point
        OVERSHOOT = overshoot 
        
        geometries = road['geometry']
        trajectory = []
        
        print(f"Start S: {start_loc['s']:.2f}, Crash S: {crash_loc['s']:.2f}")

        # CASE A: Moving Forward (Start S < Crash S)
        if start_loc['s'] <= crash_loc['s']:
            direction = 1
            print("Direction: Forward (s increasing)")
            
            # Calculate target global S (Crash + Buffer)
            target_s = crash_loc['s'] + OVERSHOOT
            
            # Iterate through relevant segments from Start Index onwards
            current_geom_idx = start_loc['geom_index']
            
            while current_geom_idx < len(geometries):
                geom = geometries[current_geom_idx]
                length = geom['length']
                geom_start_s = geom['s']
                
                # Determine where to start and end ON THIS SEGMENT
                # If it's the first segment, start at the calculated local S. Otherwise start at 0.
                if current_geom_idx == start_loc['geom_index']:
                    current_local_s = start_loc['s_local']
                else:
                    current_local_s = 0.0
                
                # Loop through this segment
                while current_local_s <= length:
                    global_s = geom_start_s + current_local_s
                    
                    # Stop if we have gone past the target overshoot
                    if global_s > target_s:
                        break
                    
                    px, py = self._calculate_offset_point(road, geom, current_local_s, side)
                    trajectory.append((px, py))
                    
                    current_local_s += step_size

                if global_s > target_s:
                    break # Stop processing further segments
                    
                current_geom_idx += 1

        # CASE B: Moving Backward (Start S > Crash S)
        else:
            direction = -1
            print("Direction: Backward (s decreasing)")
            
            # Calculate target global S (Crash - Buffer)
            target_s = crash_loc['s'] - OVERSHOOT
            
            # Iterate backwards from Start Index
            current_geom_idx = start_loc['geom_index']
            
            while current_geom_idx >= 0:
                geom = geometries[current_geom_idx]
                length = geom['length']
                geom_start_s = geom['s']
                
                # If first segment, start at local S. Otherwise start at end of segment (length).
                if current_geom_idx == start_loc['geom_index']:
                    current_local_s = start_loc['s_local']
                else:
                    current_local_s = length
                    
                # Loop "backwards" through this segment
                while current_local_s >= 0:
                    global_s = geom_start_s + current_local_s
                    
                    if global_s < target_s:
                        break
                    
                    px, py = self._calculate_offset_point(road, geom, current_local_s, side)
                    trajectory.append((px, py))
                    
                    current_local_s -= step_size # Decrement
                
                if global_s < target_s:
                    break
                    
                current_geom_idx -= 1

        return trajectory

def clean_trajectory(trajectory, min_dist=0.5, max_angle_deg=120):
    """
    Removes points that cause the path to backtrack or zigzag.
    
    Args:
        trajectory: List of (x,y) or (x,y,z) tuples.
        min_dist: Minimum distance required between points (removes overlaps).
        max_angle_deg: Maximum allowed turn angle. If a point requires a 
                    turn sharper than this (e.g., >120 deg), it's likely a backtrack.
    """
    if not trajectory or len(trajectory) < 2:
        return trajectory

    cleaned = [trajectory[0]]
    
    for i in range(1, len(trajectory)):
        curr_p = trajectory[i]
        prev_p = cleaned[-1]
        
        dist = math.sqrt((curr_p[0] - prev_p[0])**2 + (curr_p[1] - prev_p[1])**2)
        
        # If point is too close (overlap), skip it
        if dist < min_dist:
            continue

        # 2. Angle/Backtrack Check
        if len(cleaned) > 1:
            prev_prev_p = cleaned[-2]
            
            # Vector 1: Prev_Prev -> Prev
            v1 = (prev_p[0] - prev_prev_p[0], prev_p[1] - prev_prev_p[1])
            # Vector 2: Prev -> Curr
            v2 = (curr_p[0] - prev_p[0], curr_p[1] - prev_p[1])
            
            # Calculate angle between vectors
            dot_prod = v1[0]*v2[0] + v1[1]*v2[1]
            mag_v1 = math.sqrt(v1[0]**2 + v1[1]**2)
            mag_v2 = math.sqrt(v2[0]**2 + v2[1]**2)
            
            if mag_v1 * mag_v2 > 0:
                cos_angle = dot_prod / (mag_v1 * mag_v2)
                # Clamp to avoid float errors
                cos_angle = max(-1.0, min(1.0, cos_angle)) 
                angle = math.degrees(math.acos(cos_angle))
                
                # If the turn is sharper than max_angle (e.g., 180 is a U-turn), 
                # this point is likely "behind" the previous one. Skip it.
                if abs(angle) > max_angle_deg:
                    continue

        cleaned.append(curr_p)

    return cleaned

def calculate_synchronized_speeds(xodrPath, crash_P, 
                                    v1_P, v1_road_id, v1_speed,
                                    v2_P, v2_road_id, v2_speed):
    """
    Calculates the exact speed required for Vehicle 2 to hit the crash point 
    at the exact same moment as Vehicle 1.
    
    Returns:
        (v1_kmh, v2_kmh): Tuple of synchronized speeds in Km/hour.
    """
    v1_x, v1_y = v1_P
    v1_P = (v1_x, -v1_y)
    v2_x, v2_y = v2_P
    v2_P = (v2_x, -v2_y)
    v1_side = "right"
    v2_side = "right"

    with open(xodrPath, 'r') as file:
        xodr_content = file.read()

    generator = OpenDRIVEChecker(xodr_content)

    step_size = 0.5
    
    traj_v1_measure = generator.get_trajectory(crash_P, v1_P, v1_road_id, v1_side, step_size, overshoot=0.0)
    traj_v2_measure = generator.get_trajectory(crash_P, v2_P, v2_road_id, v2_side, step_size, overshoot=0.0)

    traj_v1_measure = clean_trajectory(traj_v1_measure)
    traj_v2_measure = clean_trajectory(traj_v2_measure)

    if not traj_v1_measure or not traj_v2_measure:
        print("Error: Could not generate measurement trajectories.")
        return 0.0, 0.0

    def calculate_path_length(trajectory):
        total_dist = 0.0
        for i in range(len(trajectory) - 1):
            p1 = trajectory[i]
            p2 = trajectory[i+1]
            dist = math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
            total_dist += dist
        return total_dist

    dist_v1 = calculate_path_length(traj_v1_measure)
    dist_v2 = calculate_path_length(traj_v2_measure)

    print(f"Distance to Crash - Vehicle 1: {dist_v1:.2f} m")
    print(f"Distance to Crash - Vehicle 2: {dist_v2:.2f} m")

    if v1_speed != -1:
        v1_ms = v1_speed * 0.44704
    
        if v1_ms <= 0.1:
            print("Error: Master vehicle speed is too low.")
            return 0.0, 0.0

        ttc = dist_v1 / v1_ms
        print(f"Time to Collision: {ttc:.4f} seconds")

        v2_ms = dist_v2 / ttc
        v2_mph_adjusted = v2_ms / 0.44704
        
        v1_kmh = v1_ms * 3.6
        v2_kmh = v2_ms * 3.6
        
        print(f"V1 Speed (Fixed): {v1_speed} MPH ({v1_ms:.2f} m/s)")
        print(f"V2 Speed (Reported): {v2_speed} MPH")
        print(f"V2 Speed (Synced):   {v2_mph_adjusted:.2f} MPH ({v2_ms:.2f} m/s)")
    
        return v1_kmh, v2_kmh
    
    if v2_speed != -1:
        v2_ms = v2_speed * 0.44704
    
        if v2_ms <= 0.1:
            print("Error: Master vehicle speed is too low.")
            return 0.0, 0.0

        ttc = dist_v2 / v2_ms
        print(f"Time to Collision: {ttc:.4f} seconds")

        v1_ms = dist_v1 / ttc
        v1_mph_adjusted = v2_ms / 0.44704
        
        v1_kmh = v1_ms * 3.6
        v2_kmh = v2_ms * 3.6
        
        print(f"V2 Speed (Fixed): {v2_speed} MPH ({v2_ms:.2f} m/s)")
        print(f"V1 Speed (Reported): {v1_speed} MPH")
        print(f"V1 Speed (Synced):   {v1_mph_adjusted:.2f} MPH ({v1_ms:.2f} m/s)")
    
        return v1_kmh, v2_kmh

    return 0, 0

def route_generator(xodrPath, trajectory_path, crash_P, P_x, P_y, road_id, fileopen):
   
    with open(xodrPath, 'r') as file:
        xodr_content = file.read()

    generator = OpenDRIVEChecker(xodr_content)

    SIDE = 'right' # or 'left'
    step_size = 5

    P_opendrive = -P_y
    P = (P_x, P_opendrive)

    points = generator.get_trajectory(crash_P, P, road_id, SIDE, step_size)
    points = clean_trajectory(points)
    
    if points:
        print(f"Generated {len(points)} points for Road {road_id}, Side: {SIDE}")
        
        # Save
        with open(trajectory_path, fileopen) as f:
            for p in points:
                f.write(f"{p[0]},{p[1]}\n")

        print("trajectory generated.")
        return points



    
