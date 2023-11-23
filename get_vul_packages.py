import json
# import requests

def read_json_file (json_file_path) :
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    return data

def get_dependencies(package_json) :
    dependencies = package_json.get("dependencies", {})
    devDependencies = package_json.get("devDependencies", {})
    all_dependencies = {**dependencies, **devDependencies}
    print(all_dependencies)
    return all_dependencies


json_file_path = input("Enter path to package.json file: ")
package_json = read_json_file(json_file_path)
dependencies = get_dependencies(package_json)