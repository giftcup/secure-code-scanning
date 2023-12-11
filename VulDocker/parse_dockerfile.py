import yaml
import re
from dockerfile_parse import DockerfileParser
import requests

def parse_dockerfile(dockerfile) :
    parser = DockerfileParser()

    parser.content =  dockerfile
    instructions = parser.structure

    return instructions

def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            file = file.read()
    except FileNotFoundError:
        print(f"The file path {file_path} doesn't exist.")
        exit()
    except IOError:
        print(f"An error occured when trying to read file from {file_path}")
        exit()
    return file

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
        

def check_dockerfile_violations(instructions, rules):
    violations = []

    for rule in rules:
        pattern = re.compile(rule['pattern'])
        print(pattern)
        for instruction in instructions:
            if (instruction['instruction'] == 'COMMENT'):
                continue
            if (pattern.match(instruction['content'])):
                violations.append({
                    'rule_name': rule['name'],
                    'description': rule['description'],
                    'line': instruction['startline'] + 1
                })

    return violations

def main():
    dockerfile_path = "./Dockerfile"
    dockerfile_content = read_file(dockerfile_path)
    instructions = parse_dockerfile(dockerfile_content)

    rule_path = "./security_rules.yaml"
    security_rules = read_file(rule_path)
    security_rules = yaml.safe_load(security_rules)
    violations = check_dockerfile_violations(dockerfile_content, instructions, security_rules)
    
    print("💣------------------------------------")
    
    for violation in violations:
        print(f"\t\033[91m{violation['rule_name']} on line {violation['line']}\033[0m")
        print(f"\tDescription: {violation['description']}")
        print("\n")

    print("💣------------------------------------")

main()
