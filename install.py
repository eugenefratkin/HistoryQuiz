import subprocess
import sys

def install_packages():
    with open('requirements.txt') as f:
        packages = f.read().splitlines()
        for package in packages:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

if __name__ == "__main__":
    install_packages()
