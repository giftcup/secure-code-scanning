import json
import requests

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

def get_vulnerabilities(package_name, package_version, package_ecosystem="npm") :
    headers = {"Content-Type": "application/json"}
    url = "https://api.osv.dev/v1/query"
    query = {
        "version": package_version, 
        "package": {
            "name": package_name,
            "ecosystem": package_ecosystem
        }
    }

    response = requests.post(url, data = json.dumps(query), headers = headers)

    if response.status_code == 200:
        vulnerabilities = response.json()
        return vulnerabilities
    else:
        print(f"Failed to return vulnerabilities for {package_name}@{package_version} for the {package_ecosystem} ecosystem")
        return None
    

def main() :
    json_file_path = input("Enter path to package.json file: ")

    package_json = read_json_file(json_file_path)
    dependencies = get_dependencies(package_json)
    
    vulnerability_dictionary = {}

    for package_name, package_version in dependencies.items():
        vulnerabilities = get_vulnerabilities(package_name, package_version)

        if vulnerabilities:
            print(f"Vulnerabilities found for {package_name}@{package_version}:")

            for vulnerability in vulnerabilities['vulns']:
                vulnerability_id = vulnerability['id']
                vulnerability_summary = vulnerability['summary']

                vulnerability_dictionary[vulnerability_id] = vulnerability_summary
                print("💣------------------------------------")
                print(f"\tID: {vulnerability_id}")
                print(f"\tSummary: {vulnerability_summary}")
                print("💣------------------------------------")
            print(f"{vulnerability_dictionary}")
    
    if not vulnerability_dictionary:
        print("\nHurray🎉🎉, you're package.json is free of vulnerabilities💃💃\n")              
main()