# SpotifyStats

Small utility to collect simple Spotify metrics using the Spotipy python client.

## What it does

- Connects to the Spotify Web API (via `spotipy`) to fetch user / track / playlist statistics.
- Minimal starter project: dependency and CI already configured.

## Requirements

- Python 3.14
- See dependencies: [requirements.txt](requirements.txt) (contains `spotipy==2.25.1`).

## Setup (so far)

1. Create and activate a virtual environment:
   ```sh
   python -m venv .venv
   source .venv/bin/activate
   ```

- setup spotify for dev app
  get client id and client secret
  setup secrets in github secrets
  setup redirect uri in github secrets

- on first run --> accept spotify prompt in browser
