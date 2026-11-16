import requests

# GitHub repo info
REPO_OWNER = "Kostyaptrv"
REPO_NAME = "pomoshnik"
TOKEN = "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"
headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Get release
url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/tags/v1.0"
response = requests.get(url, headers=headers)
release = response.json()
release_id = release["id"]
print(f"Release ID: {release_id}")

# List existing assets
assets_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/{release_id}/assets"
response = requests.get(assets_url, headers=headers)
assets = response.json()
print(f"Existing assets:")
for asset in assets:
    print(f"  - {asset['name']}: {asset['size'] / 1024 / 1024:.1f} MB")
    print(f"    Delete URL: {asset['url']}")
    
    # Delete old asset
    del_response = requests.delete(asset['url'], headers=headers)
    if del_response.status_code == 204:
        print(f"    Deleted: {asset['name']}")
    else:
        print(f"    Delete failed: {del_response.status_code}")

# Upload new installer
import os
installer_path = r"installer\Pomoshnik_Setup_1.0.exe"
print(f"\nNew installer size: {os.path.getsize(installer_path) / 1024 / 1024:.1f} MB")

upload_url = f"https://uploads.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/{release_id}/assets?name=Pomoshnik_Setup_1.0.exe"
files = {"file": open(installer_path, "rb")}
data = {"content_type": "application/octet-stream"}

print("Uploading new installer...")
response = requests.post(upload_url, files=files, data=data, headers=headers)

if response.status_code in [200, 201]:
    asset = response.json()
    print(f"Success! Download: {asset['browser_download_url']}")
    print(f"Size: {asset['size'] / 1024 / 1024:.1f} MB")
else:
    print(f"ERROR: {response.status_code}")
    print(response.text)
