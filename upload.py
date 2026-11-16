import requests
import os
import sys

REPO_OWNER = "Kostyaptrv"
REPO_NAME = "pomoshnik"
TOKEN = sys.argv[1] if len(sys.argv) > 1 else ""

if not TOKEN:
    print("Usage: python upload.py <token>")
    sys.exit(1)

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/tags/v1.0"
response = requests.get(url, headers=headers)

if response.status_code != 200:
    print(f"Error getting release: {response.status_code}")
    sys.exit(1)

release = response.json()
release_id = release["id"]
print(f"Release ID: {release_id}")

# Delete old assets
assets_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/{release_id}/assets"
response = requests.get(assets_url, headers=headers)
assets = response.json()

for asset in assets:
    del_response = requests.delete(asset['url'], headers=headers)
    if del_response.status_code == 204:
        print(f"Deleted: {asset['name']}")

# Upload new installer
installer_path = r"installer\Pomoshnik_Setup_1.0.exe"
if not os.path.exists(installer_path):
    print(f"Installer not found: {installer_path}")
    sys.exit(1)

print(f"Uploading: {os.path.getsize(installer_path) / 1024 / 1024:.1f} MB")

upload_url = f"https://uploads.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/{release_id}/assets?name=Pomoshnik_Setup_1.0.exe"
files = {"file": open(installer_path, "rb")}
data = {"content_type": "application/octet-stream"}

response = requests.post(upload_url, files=files, data=data, headers=headers)

if response.status_code in [200, 201]:
    asset = response.json()
    print(f"Uploaded! {asset['browser_download_url']}")
else:
    print(f"Upload error: {response.status_code}")
    print(response.text)
