import requests
import json
import re

def clean_version(version_string):
    cleaned_version = re.sub(r'[^\d.]', '', version_string)
    return cleaned_version

def get_supported_node_version():
    try:
        node_api_url = "https://nodejs.org/dist/index.json"
        response = requests.get(node_api_url)

        if response.status_code == 200:
            data = response.json()
            
            lts_versions = [clean_version(release['version']) for release in data if release.get('lts', False)]
            
            return lts_versions
        
        else:
            print(f"Error: Unable to fetch node js versions")

    except Exception as e:
        print(f"Error: {e}")
        return None


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
        # Recursively call the function for nested dictionaries
        for key, value in data.items():
            get_node_versions(value, versions_list)
    elif isinstance(data, list):
        # Recursively call the function for elements in the list
        for item in data:
            get_node_versions(item, versions_list)


json_file_path = input("Enter path to package.json file")
supported_versions = get_supported_node_version()
node_versions_list = []

try:
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    get_node_versions(data, node_versions_list)

    cleaned_versions = [clean_version(version) for version in node_versions_list]
    # print("Cleaned Node.js versions:", cleaned_versions)

except FileNotFoundError:
    print(f"Error: File '{json_file_path}' not found.")
except json.JSONDecodeError:
    print(f"Error: Invalid JSON format in file '{json_file_path}'.")
except Exception as e:
    print(f"Error: {e}")

if any(element not in supported_versions for element in node_versions_list):
    print("Package.json contains unsupported node versions")

