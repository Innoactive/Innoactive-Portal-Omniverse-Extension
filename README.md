# Innoactive Portal Omniverse Extension

This extension for NVIDIA Omniverse allows you to create a sharing link to Innoactive Portal that will allow users to launch the USD file with Omniverse Enterprise in the cloud and stream it into their browser and/or Standalone VR headset.

## How it works:
1. Install the extension
2. Copy the sharing link and sent it to the user
3. User clicks the sharing link and can use USD file with Omniverse Enterprise on Innoactive Portal cloud.

## Benefits:
- Users can contribute and review USD files without need for a own workstation
- XR cloud streaming supported: stream not only to the browser but even to a Standalone VR headset
- Compliant with your IT: Both SaaS and Self-hosted options available

![Innoactive Omniverse Extension](https://github.com/Innoactive/Portal-Omniverse-Extension/blob/master/exts/innoactive.omniverse/data/preview_readme.png?raw=true)

## Requirements:
- Innoactive Portal Account (get one at https://innoactive.io/)
- NVIDIA Omniverse Enterprise license
- USD file needs to be hosted on your Nucleus Server
- Users need to have access permissions to the USD file on the Nucleus Server
- Users need to have a Innoactive Portal user account and access permissions to the Omniverse runtime you want to use

## Installation:
1. In Omniverse, go to "Window / Extensions / Options / Settings"
2. Add this to the Extension Search Paths: git://github.com/Innoactive/Innoactive-Portal-Omniverse-Extension?branch=main&dir=exts
3. Search for "Innoactive" in "Third Party" and enable the Innoactive extension (innoactive.omniverse)
4. Enable "autoload" if desired

## Usage:
1. Load a USD file from Nucleus Server
2. Open Innoactive Extension
3. Click "From Stage" to load the current USD URL
2. Select OV runtime to use for the stream
3. Select streaming mode: browser, VR (CloudXR), local (no streaming)
4. Configure Base Url to match Innoactive Portal cloud domain
5. Click "Test" to start a cloud streaming session yourself
6. Click "Copy" to copy the sharing URL to the clipboard.
7. Send the sharing link to the user you want to view the USD file via cloud streaming

Hints:
- Ensure that the user has a Innoactive Portal account (Click "Invite user" button if needed)
- Ensure that the user has access permissions for the selected Omniverse runtime

Please contact [Innoactive Support](https://www.innoactive.io/support) for any questions
