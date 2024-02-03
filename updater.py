import urllib.request
import json
import base64
import os
import time

def Get(URL :str):
    """Returns content of the response to a GET request"""
    with urllib.request.urlopen(URL) as response:
        return response.read()

run :str= ""
dep :str= ""
while dep.lower() not in ["y", "n"]:
    dep = input("Fetch dependencies after updating? (y/n): ")
while run.lower() not in ["y", "n"]:
    run = input("Run the game after updating? (y/n): ")

REPO_TREE :str = "https://api.github.com/repos/devboiagru/racing-ball/git/trees/main?recursive=1"
COOLDOWN :float= 0.5                                    # Delay between HTTP requests to prevent rate limiting

print (f"Getting repository tree: {REPO_TREE}")
files = json.loads(Get(REPO_TREE))['tree']

trees :list= []
blobs :list= []

try:
    with open("local_checksums.json", "+r") as checksum_file:
        checksums :dict= json.load(checksum_file)
except FileNotFoundError:
    with open("local_checksums.json","+w") as checksum_file:
        checksum_file.write("[]")
        checksums :dict= {}

for file in files:
    if file["type"] == "blob":
        try:                                            # Only update files which have changed
            if file["sha"] != checksums[file["path"]]:
                print (f"New / Updated file: {file['path']}...")
                blobs.append(file)
            else:
                print (f"Checksum matches for: {file['path']}, not updating...")
        except KeyError:
            blobs.append(file)
    else:                                               # File is a tree
        trees.append(file)

for folder in trees:                                    # Create folders
    try:
        print(f"Creating {folder['path']}")
        os.mkdir(folder["path"])
    except FileExistsError:
        print(f"{folder['path']} already exists")

with open("local_checksums.json", "+w") as checksum_file:

    for blob in blobs:
        try:
            with open(blob["path"], "+wb") as file:
                print (f"Getting {blob['url']}")
                checksums[blob["path"]] = blob["sha"]
                file_data  = json.loads(Get(blob["url"]))
                file_b64   = file_data["content"]
                file_bytes = base64.b64decode(file_b64)
                print (f"Writing {blob['path']}")
                file.write(file_bytes)
            time.sleep(COOLDOWN)
        except Exception as e:
            print (f"Exception {e} of type {type(e)}")
    json.dump(checksums, checksum_file, indent=4)

if dep.lower() == "y":
    os.system('"pip install -r requirements.txt"')
if run.lower() == "y":
    os.system('"python main.py"')