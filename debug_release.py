import requests
import os

REPO_OWNER = "Kostyaptrv"
REPO_NAME = "pomoshnik"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/tags/v1.0"
response = requests.get(url, headers=headers)

print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")

if response.status_code == 200:
    release = response.json()
    print(f"Release ID: {release['id']}")
else:
    print("Failed to get release")
