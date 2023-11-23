import json
import re

def clean_version(version_string):
    # Use regex to remove characters that don't represent the version
    cleaned_version = re.sub(r'[^\d.]', '', version_string)
    return cleaned_version

def get_node_versions(data, versions_list):
    if isinstance(data, dict):
        # Check if 'engines' key is present in the dictionary
        engines_data = data.get('engines')
        if engines_data:
            # Get the value of 'node' from the 'engines' dictionary
            node_version_requirement = engines_data.get('node')
            if node_version_requirement:
                versions = node_version_requirement.split('||')
                for version in versions:
                    cleaned_version = clean_version(version)
                    versions_list.append(cleaned_version)
        for key, value in data.items():
            get_node_versions(value, versions_list)
    elif isinstance(data, list):
        # Recursively call the function for elements in the list
        for item in data:
            get_node_versions(item, versions_list)

# Specify the path to your JSON file
json_file_path = input("Enter packet.json file path: ")

# List to store cleaned versions
node_versions_list = []

try:
    # Open the file and load JSON data
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Call the function with the loaded JSON data and versions list
    get_node_versions(data, node_versions_list)

    # Clean and print the versions list
    cleaned_versions = [clean_version(version) for version in node_versions_list]
    print("Cleaned Node.js versions:", cleaned_versions)

except FileNotFoundError:
    print(f"Error: File '{json_file_path}' not found.")
except json.JSONDecodeError:
    print(f"Error: Invalid JSON format in file '{json_file_path}'.")
except Exception as e:
    print(f"Error: {e}")

