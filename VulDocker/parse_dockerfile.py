import re, json, yaml, subprocess
from dockerfile_parse import DockerfileParser
import requests
import pandas as pd

def parse_dockerfile(dockerfile) :
    parser = DockerfileParser()

    parser.content =  dockerfile
    instructions = parser.structure

    return instructions

def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            file = file.read()
            return file
    except FileNotFoundError:
        return None
    except IOError:
        return None

def get_latest_tag_from_registry(image_name):
    api_url = f"https://hub.docker.com/v2/repositories/{image_name}/tags"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        tags = data.get('results', [])

        if tags:
            latest_tag = tags[0].get('name')
            return latest_tag
        else:
            return None
    else:
        return None
    
def compare_image_version(image_name, image_version):
    latest_version = get_latest_tag_from_registry(image_name)

    if image_version != latest_version:
        return True
    return False

def find_image_vuln_with_snyk(image_name, image_version):
    command = ['snyk', 'container', 'test', f'{image_name}:{image_version}', '--json']

    try:
        result = subprocess.run(command, capture_output=True, text=True)

        try:
            result = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            print(f"Error decoding json output: {e}")
            return None
        
        if not result['vulnerabilities']:
            return None
        else:
            vulnerabilities = result['vulnerabilities']
            df = pd.DataFrame(vulnerabilities)
            unique_df = df.drop_duplicates(subset='title')
            vulnerabilities = unique_df.to_dict(orient='records')
            return vulnerabilities[:3]
        
    except subprocess.CalledProcessError as e:
        print(f"Error running the Synk command: {e}")
        print(e.stderr)
        return None


def check_dockerfile_violations(instructions, rules):
    violations = []

    for instruction in instructions:
        if (instruction['instruction'].upper() == 'COMMENT'):
            continue
        if (instruction['instruction'].upper() == 'FROM'):
            image_pattern = r'([\w.-]+)(?::([\w.-]+)?)'
            match = re.match(image_pattern, instruction['value'])

            if match:
                image_name = match.group(1)
                image_version = match.group(2) or 'latest'
            
                if compare_image_version(image_name, image_version):
                    violations.append({
                        'rule_name': "Outdated image version",
                        'description': 'The version of your image is out of date',
                        'line': instruction['startline'] + 1
                    })
                
                image_vulnerabilities = find_image_vuln_with_snyk(image_name, image_version)

                if not image_vulnerabilities:
                    continue

                for vulnerability in image_vulnerabilities:
                    violations.append({
                        'rule_name': vulnerability['title'],
                        'description': vulnerability['description'],
                        'line': instruction['startline'] + 1,
                        'severity': vulnerability['severity']
                    })

        for rule in rules:
            pattern = re.compile(rule['pattern'])

            if (pattern.match(instruction['content'])):
                violations.append({
                    'rule_name': rule['name'],
                    'description': rule['description'],
                    'line': instruction['startline'] + 1,
                    'severity': rule['severity'] or None
                })

    return violations

def main():
    dockerfile_path = './Dockerfile'
    dockerfile_content = read_file(dockerfile_path)

    if not dockerfile_content:
        print("\n\033[91m⚠️⚠️ Dockerfile doesn't exist in directory structure\033[0m")
        print("Ensure the name is exactly \033[1mDockerfile\033[0m\n")
        print("Exiting program ...")
        exit()
    
    instructions = parse_dockerfile(dockerfile_content)

    rule_path = "./security_rules.yaml"
    security_rules = read_file(rule_path)
    
    if not security_rules:
        print("\n\033[33m⚠️⚠️ No security rules defined\033[0m")
        print("Exiting program ...")
        exit()

    security_rules = yaml.safe_load(security_rules)
    violations = check_dockerfile_violations(instructions, security_rules)

    if not violations:
        print("\nHurray🎉🎉, your Dockerfile is free of vulnerabilities💃\n")
        exit()
    
    print("💣------------------------------------")
    
    for violation in violations:
        print(f"\t\033[91m{violation['rule_name']} on line {violation['line']}\033[0m")
        print(f"\tDescription: {violation['description']}")
        print("\n")

    print("💣------------------------------------")

main()
