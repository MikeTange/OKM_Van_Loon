import requests
import subprocess
import os

# Customize this
GITHUB_RAW_URL = "https://github.com/MikeTange/OKM_Van_Loon/local_runner.py"

print("Downloading latest script from GitHub...")
response = requests.get(GITHUB_RAW_URL)
if response.status_code != 200:
    print(f"Failed to download script: {response.status_code}")
    exit(1)

with open("local_runner.py", "w", encoding="utf-8") as f:
    f.write(response.text)

print("Running script...")
subprocess.run(["python", "local_runner.py"])