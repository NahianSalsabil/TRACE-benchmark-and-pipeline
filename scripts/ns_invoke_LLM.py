import os
from google import genai
from google.genai import types
import re
from ns_check_points import check_and_get_direction
import json
import time

MAX_RETRIES = 5
client = genai.Client()
model_name = "gemini-2.5-flash"

def get_file_content(filepath):
    with open(filepath, 'r') as f:
        return f.read()

def construct_prompt(summary_data, bbox_data):
    """
    Constructs the prompt by injecting file data into the optimized template.
    """
    prompt_template = f"""
You are an expert in accident reconstruction using CARLA.
Your task is to deduce the pre-crash positions (5 seconds prior) of two vehicles involved in a crash.

### INPUT DATA
**1. Crash Summary:**
{summary_data}

**2. Map Context (Local CARLA Coordinates):**
{bbox_data}

---

### CRITICAL TRAFFIC RULES
**Region:** United States (USA).
**Rule:** **RIGHT-HAND TRAFFIC (RHT)** is mandatory.
- Vehicles MUST drive on the right side of the road.
- When moving "backwards" from the crash point to find the start point, ensure the resulting position places the vehicle in the correct lane (the right lane relative to its forward direction).

---

### REQUIRED REASONING STEPS
Before generating the final JSON, you must strictly follow these reasoning steps. 
**Do not skip these steps**, as they ensure the coordinates are physically valid.

**Task 1: Scenario Analysis**
- Summarize the crash scenario.

**Task 2: Distance Calculation**
- Calculate the distance traveled in 5 seconds.
- Formula: Distance = Speed (m/s) * 5. (Convert MPH to m/s first: 1 MPH = 0.447 m/s).

**Task 3: Crash Location**
- Extract the crash location (x, y) explicitly from the summary.

**Task 4: Road & Bounding Box Selection**
- Identify which Road ID and Bounding Box each vehicle started in.
- **RHT Constraint:** Select the road segment/box that corresponds to the RIGHT side of the road for the vehicle's direction of travel.
- **Constraint:** Vehicles approaching a junction usually come from different roads.
- **Constraint:** There must be a valid path from the Start Point to the Crash Point.
- **Constraint:** Putting the vehicles in the assigned bounding box has more priority than following the spped mentioned.
- **Constraint:** For both junction and non-junction crashes, The initial locations of the two vehicles cannot be the same.

**Task 5: Coordinate Calculation & Verification (CRITICAL)**
- Calculate the start position (x, y) by moving backwards from the crash site by the distance found in Task 2.
- **Constraint:** The coordinates you select must be **inside** the respective assigned bounding box.
- **Constraint:** The coordinates cannot be the four corners of the bounding boxes provided.
- **Constraint:** The coordinates must not be very close to the edge of the bounding box.
- **Constraint:** The positions of the two vehicles cannot be same.
- **VERIFICATION:** You must strictly verify your calculated point is inside the chosen bounding box.
- *Check:* Is calculated X between Box X_min and X_max? 
- *Check:* Is calculated Y between Box Y_min and Y_max?
- If the point is outside, adjust it slightly along the road geometry until it is **inside** the box.

---

### FINAL OUTPUT
After you have completed the reasoning above, output the final result in a single VALID JSON block.
The JSON must be the **last** thing in your response.

```json
{{
  "crash_location": {{ "x": float, "y": float }},
  "vehicle_1": {{
      "road_id": int,
      "position": {{ "x": float, "y": float }}
  }},
  "vehicle_2": {{
      "road_id": int,
      "position": {{ "x": float, "y": float }}
  }}
}}
```
"""
    return prompt_template

def parse_json_from_response(text):
    """Helper to safely extract JSON from LLM markdown."""
    
    match = re.search(r"```json(.*?)```", text, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
    else:
        start_index = text.find('{')
        end_index = text.rfind('}') + 1
        if start_index != -1 and end_index != -1:
            json_str = text[start_index:end_index]
        else:
            return None
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None

def validate_positions(data, xodr_path):
    """
    Checks if the points in the data are valid using the imported checker.
    Returns: (is_valid: bool, error_message: str)
    """
    if not data:
        return False, "Failed to parse valid JSON from response."

    errors = []

    v1_x = data['vehicle_1']['position']['x']
    v1_y = data['vehicle_1']['position']['y']
    v1_P = (v1_x, v1_y)
    is_v1_valid, _, _, _, _ = check_and_get_direction(True, v1_P, xodr_path) 

    if not is_v1_valid:
        errors.append(f"Vehicle 1 position ({v1_x}, {v1_y}) is OUTSIDE the valid bounding boxes.")

    v2_x = data['vehicle_2']['position']['x']
    v2_y = data['vehicle_2']['position']['y']
    v2_P = (v2_x, v2_y)
    is_v2_valid, _, _, _, _ = check_and_get_direction(True, v2_P, xodr_path)

    if not is_v2_valid:
        errors.append(f"Vehicle 2 position ({v2_x}, {v2_y}) is OUTSIDE the valid bounding boxes.")

    if errors:
        return False, " ".join(errors) + " Please recalculate coordinates that are strictly INSIDE the bounding boxes."
    
    return True, ""

def process_crash_with_retries(summary_text, bbox_text, xodr_path):
    """
    Uses Normal Mode (generate_content) but manually appends history
    to allow for retries.
    """
    
    initial_prompt = construct_prompt(summary_text, bbox_text)
    
    conversation_history = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=initial_prompt)]
        )
    ]
    
    config = types.GenerateContentConfig(temperature=0.8)

    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=conversation_history,
                config = config
            )
            
            response_text = response.text
            json_data = parse_json_from_response(response_text)
            
            is_valid, error_msg = validate_positions(json_data, xodr_path)
            
            if is_valid:
                return attempt+1, response_text, json_data
            
            conversation_history.append(
                types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=response_text)]
                )
            )
            
            correction_prompt = f"Your previous output was incorrect.\nERROR: {error_msg}\n\nPlease strictly follow the instructions: Points must be INSIDE the bounding box. Recalculate."
            conversation_history.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=correction_prompt)]
                )
            )
            
            time.sleep(1)

        except Exception as e:
            print(f"   Error: {e}")
            time.sleep(2)

    return attempt+1, None, None

def main():

    bbox_dir = "points/correct_bbox"
    summary_dir = "crashes/modified_summary"
    xodr_dir = "ns-maps/clipped_merged_xodr"
    prompt_dir = "prompts"
    llm_output_dir = "LLM_output"
    scene_points_dir = "points/scene_points"

    os.makedirs(prompt_dir, exist_ok=True)
    os.makedirs(llm_output_dir, exist_ok=True)

    for filename in os.listdir(bbox_dir):
        if filename.endswith(".txt"):
            print(f"LLM started {filename}")
            try:
                bbox_path = os.path.join(bbox_dir, filename)
                bbox_text = get_file_content(bbox_path)

                crash_id = filename.split('_')[-1].replace('.txt','')
                xodr_path = os.path.join(xodr_dir, f"map_{crash_id}.xodr")
                summary_path = os.path.join(summary_dir, f"summary_{crash_id}.txt")
                summary_text = get_file_content(summary_path)
                
                initial_prompt = construct_prompt(summary_text, bbox_text)

                with open(os.path.join(prompt_dir, f"prompt_{crash_id}.txt"), "w") as f:
                    f.write(initial_prompt)

                attempt, final_text, final_json = process_crash_with_retries(summary_text, bbox_text, xodr_path)
                
                if final_json:
                    with open(os.path.join(llm_output_dir, f"llmreasoning_{crash_id}"), "w") as f:
                        f.write(final_text)
                    
                    with open(os.path.join(scene_points_dir, f"scenepoints_{crash_id}.json"), "w") as f:
                        json.dump(final_json, f, indent=4)
                    
                    print(f"   Success: {filename} in {attempt}.")
                else:
                    print(f"   FAILED to get valid points for {filename} after {attempt} retries.")

            except Exception as e:
                print(f"\nError: {e}")
        
if __name__ == "__main__":
    main()