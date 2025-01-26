
import pandas as pd
import json  

def pretty_print(data):
    """
    Pretty-print JSON data.
    """
    print(json.dumps(data, indent=4))

def save_json_to_file(data, filename):
    """
    Save JSON data to a file.
    """
    with open(filename, "w") as json_file:
        json.dump(data, json_file, indent=4)  # Save with indentation for readability
    print(f"JSON data saved to {filename}")

