import subprocess, os

def convert_requirements_to_poetry(requirements_file):
    # Read the requirements file
    with open(requirements_file, 'r') as file:
        requirements = file.readlines()

    # Process each requirement
    for req in requirements:
        # Clean up the requirement string
        req = req.strip()
        if req:
            # Add the requirement using Poetry
            subprocess.run(["poetry", "add", req], check=True)

def main():
    requirements_file = 'requirements.txt'  # Path to your requirements.txt file
    print("current working directory is ",os.getcwd())
    convert_requirements_to_poetry(requirements_file)

if __name__ == "__main__":
    main()
