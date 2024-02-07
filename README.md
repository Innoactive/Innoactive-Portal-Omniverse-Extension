# Innoactive Omniverse Extension

This extension for NVIDIA Omniverse allows you to create a sharing link to Innoactive Portal that will allow users to launch the USD file with Omniverse Enterprise in the cloud and stream it into their browser and/or Standalone VR headset.

## How it works:
1. Install the extension
2. Copy the sharing link and sent it to the user
3. User clicks the sharing link and can use USD file with Omniverse Enterprise on Innoactive Portal cloud.

## Benefits:
- Users can contribute and review USD files without need for a own workstation
- XR cloud streaming supported: stream not only to the browser but even to a Standalone VR headset
- Compliant with your IT: Both SaaS and Self-hosted options available

![Innoactive Omniverse Extension](https://github.com/Innoactive/innoactive-omniverse-extension/blob/master/exts/de.innoactive/data/preview_readme.png?raw=true)

## Requirements:
- NVIDIA Omniverse Enterprise license
- USD file needs to be hosted on your Nucleus Server
- Users need to have access permissions to the USD file on the Nucleus Server
- Users need to have a Innoactive Portal user account and access permissions to the Omniverse runtime you want to use

## Installation:
1. Checkout this repository on your PC
2. Go to "Window / Extensions / Options / Settings"
3. Add the repository path to the Extension Search Paths (e.g. ../innoactive-omniverse-extension/exts)
4. Search for "Innoactive" in "Third Party" and enable the Innoactive extension (de.innoactive)

## Usage:
1. Select USD file (will get auto-filled from current Stage)
2. Select OV runtime
3. Select streaming mode (browser, VR, local=no streaming)
4. Base Url: configure this to match your base URL of Innoactive Portal cloud (login here https://portal.innoactive.io/ and copy paste the domain name incl. https:// but without trailing slash)
5. Click "Test" to start a cloud streaming session yourself
6. Click "Copy" to copy the sharing URL to the clipboard.
7. Send the sharing link to the user you want to view the USD file via cloud streaming. Ensure the user has a Innoactive Portal account (Click "Invite user" button if needed)

