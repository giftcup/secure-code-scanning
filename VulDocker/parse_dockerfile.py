import yaml
import re
from dockerfile_parse import DockerfileParser

def parse_dockerfile(dockerfile) :
    parser = DockerfileParser()

    parser.content =  dockerfile
    instructions = parser.structure

    return instructions

    # print(f"{instructions}")

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

def check_dockerfile_violations(docker_content, rules):
    violations = []
    
    for rule in rules:
        pattern = re.compile(rule['pattern'])
        if (pattern.search(docker_content)):
            violations.append({
                'rule_name': rule['name'],
                'description': rule['description']
            })

    return violations

def main():
    dockerfile_path = "/Users/pro-3is/Documents/workspace/secure-code-scanning/VulDocker/Dockerfile"
    dockerfile_content = read_file(dockerfile_path)
    instructions = parse_dockerfile(dockerfile_content)

    rule_path = "./security_rules.yaml"
    security_rules = read_file(rule_path)
    security_rules = yaml.safe_load(security_rules)
    violations = check_dockerfile_violations(dockerfile_content, security_rules)
    
    print(violations)
    
    for violation in violations:
        print("💣------------------------------------")
        print(f"\t{violation['rule_name']}")
        print(f"\tDescription: {violation['description']}")
        print("💣------------------------------------")
        print("\n\n")
main()
