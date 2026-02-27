#!/usr/bin/env python3
import json
import requests
import os
import time
from pathlib import Path

def download_mod(project_id, file_id, output_dir):
    """Download a mod from CurseForge using the eternal API."""

    # CurseForge API endpoint
    api_url = f"https://api.curseforge.com/v1/mods/{project_id}/files/{file_id}"

    # Try to get file info from CurseForge API
    # Note: This requires an API key, but we'll try the download URL directly

    # CurseForge CDN URL format
    # The file ID needs to be formatted: first 4 digits / last 3+ digits
    file_id_str = str(file_id)
    if len(file_id_str) >= 4:
        folder = file_id_str[:4]
        file = file_id_str[4:]
    else:
        folder = file_id_str
        file = ""

    # Try multiple CDN endpoints
    cdn_urls = [
        f"https://edge.forgecdn.net/files/{folder}/{file}/",
        f"https://mediafilez.forgecdn.net/files/{folder}/{file}/"
    ]

    # We need to make a request to get the actual filename
    # Let's use the CurseForge API without auth (it might work for public files)
    try:
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0'
        }

        # Try the public API endpoint
        response = requests.get(
            f"https://www.curseforge.com/api/v1/mods/{project_id}/files/{file_id}",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            download_url = data.get('data', {}).get('downloadUrl')
            filename = data.get('data', {}).get('fileName')

            if download_url and filename:
                print(f"Downloading {filename}...")
                file_response = requests.get(download_url, headers=headers, timeout=60)

                if file_response.status_code == 200:
                    output_path = os.path.join(output_dir, filename)
                    with open(output_path, 'wb') as f:
                        f.write(file_response.content)
                    print(f"✓ Downloaded: {filename}")
                    return True
                else:
                    print(f"✗ Failed to download file: {file_response.status_code}")
                    return False

        # If that didn't work, try alternative method
        print(f"Trying alternative download method for project {project_id}, file {file_id}")

        # Try direct download link
        direct_url = f"https://www.curseforge.com/api/v1/mods/{project_id}/files/{file_id}/download"
        response = requests.get(direct_url, headers=headers, allow_redirects=True, timeout=60)

        if response.status_code == 200:
            # Try to get filename from Content-Disposition header
            content_disp = response.headers.get('Content-Disposition', '')
            if 'filename=' in content_disp:
                filename = content_disp.split('filename=')[-1].strip('"')
            else:
                filename = f"mod_{project_id}_{file_id}.jar"

            output_path = os.path.join(output_dir, filename)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"✓ Downloaded: {filename}")
            return True

    except Exception as e:
        print(f"✗ Error downloading project {project_id}, file {file_id}: {str(e)}")
        return False

    return False

def main():
    # Read manifest
    manifest_path = "modpack_temp/manifest.json"
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    # Create mods directory
    mods_dir = "mods"
    os.makedirs(mods_dir, exist_ok=True)

    files = manifest.get('files', [])
    total = len(files)

    print(f"Found {total} mods to download...\n")

    successful = 0
    failed = []

    for i, mod in enumerate(files, 1):
        project_id = mod['projectID']
        file_id = mod['fileID']

        print(f"[{i}/{total}] Project: {project_id}, File: {file_id}")

        if download_mod(project_id, file_id, mods_dir):
            successful += 1
        else:
            failed.append((project_id, file_id))

        # Rate limiting
        time.sleep(0.5)

    print(f"\n{'='*50}")
    print(f"Download complete!")
    print(f"Successful: {successful}/{total}")

    if failed:
        print(f"Failed: {len(failed)}")
        print("\nFailed mods:")
        for project_id, file_id in failed:
            print(f"  - Project: {project_id}, File: {file_id}")

if __name__ == "__main__":
    main()
