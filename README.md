# SpotifyStats

<div align="center">

<a href="">![Python](https://img.shields.io/badge/python-3.14-blue.svg)</a>
<a href="">![Flask](https://img.shields.io/badge/flask-3.1.0-green.svg)</a>
<a href="">![Spotipy](https://img.shields.io/badge/spotipy-2.25.0-1DB954.svg)</a>
<a href="">![Vercel](https://img.shields.io/badge/vercel-deployed-black.svg)</a>
<a href="">![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)</a>

</div>

A serverless API that collects your Spotify listening statistics using the spotipy library and makes them available for display in GitHub READMEs or other applications. Built with Python, Flask, and deployed on Vercel.

[To deploy this solution for your own needs, jump to THIS section](#deployment-guide)

## Project Goal

Create a lightweight, serverless API that:

- Fetches personalized Spotify statistics (top artists, top tracks, recently saved albums)
- Serves a stats card via HTTP endpoints
- Can be called from GitHub READMEs to display dynamic infographics
- Runs entirely on Vercel's free serverless platform

## Project Structure

SpotifyStats/ <br>
├── .github/workflows <br>
│ └── ci.yml # CI/CD pipeline <br>
├── api/ <br>
│ └── index.py # Flask serverless function for Vercel <br>
├── tests/ <br>
│ └── test_Collector.py # Pytest test suite <br>
├── statsCollector.py # Core stats collection logic <br>
├── getRefreshToken.py # Helper script to obtain Spotify refresh token <br>
├── requirements.txt # Python dependencies <br>
├── vercel.json # Vercel configuration <br>
└── README.md # This file <br>

## Features

### Current Implementation

- **Top Artists**: Retrieves your top 5 artists for both short-term and long-term listening periods
- **Top Songs**: Fetches your top 5 tracks with album art and artist information
- **Recently Saved Albums**: Gets your 3 most recently saved albums
- **Serverless Deployment**: Runs on Vercel with automatic scaling
- **OAuth Authentication**: Uses Spotify refresh tokens for persistent access
- **Comprehensive Tests**: Full pytest suite with mocking for CI/CD

### API Endpoints

- `GET /` - Home endpoint with basic information
- `GET /stats` - Returns image with all your Spotify statistics

## Deployment Guide

Follow these steps to deploy your own instance with your Spotify data.

### Step 1: Create a Spotify Developer Application

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click **Create an App**
4. Fill in the app name and description, select **Web API** and accept the TOS
5. Once created, note your **Client ID** and **Client Secret**
6. Click **Edit Settings**
7. Add `http://localhost:8888/callback` to **Redirect URIs**
8. Save the settings

### Step 2: Get Your Spotify Refresh Token | ⚠️ INCONSISTENT ⚠️

The refresh token allows the API to access your Spotify data without requiring browser interaction.

1. Clone this repository:

```bash
git clone https://github.com/yourusername/SpotifyStats.git
cd SpotifyStats
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Edit `getRefreshToken.py` and replace the placeholders:

```py
client_id="YOUR_CLIENT_ID", # From Spotify Dashboard
client_secret="YOUR_CLIENT_SECRET", # From Spotify Dashboard
```

5. Run the script:

```bash
python getRefreshToken.py
```

6. A browser window may open asking you to authorize the app
7. The script will print your **refresh token** to the terminal- save this securely!

### Step 3: Fork and Configure the Repository

1. Fork this repository to your GitHub account
2. Go to your forked repository settings
3. Navigate to **Secrets and variables** → **Actions**
4. Add the following secrets (these are for CI/CD testing):

- `SPOTIPY_CLIENT_ID`: Your Spotify Client ID
- `SPOTIPY_CLIENT_SECRET`: Your Spotify Client Secret
- `SPOTIPY_REDIRECT_URI`: `http://localhost:8888/callback`

### Step 4: Deploy to Vercel

1. Go to [Vercel](https://vercel.com) and sign up/log in
2. Click **Add New Project**
3. Import your forked GitHub repository
4. Vercel will detect the Python project automatically
5. Create a Github Personal Access Token (PAT) --> you can see the steps [here](https://github.com/anuraghazra/github-readme-stats?tab=readme-ov-file#on-vercel)
6. Before deploying, add **Environment Variables**:

- `SPOTIPY_CLIENT_ID`: Your Spotify Client ID
- `SPOTIPY_CLIENT_SECRET`: Your Spotify Client Secret
- `SPOTIPY_REDIRECT_URI`: `http://localhost:8888/callback`
- `SPOTIFY_REFRESH_TOKEN`: The refresh token from Step 2
- `PAT_1`: The created PAT

7. Click **Deploy**

### Step 5: Test Your Deployment

Once deployed, Vercel will give you a URL like `https://your-project.vercel.app`

Test your API:

```bash
curl https://your-project.vercel.app/stats
```

You should receive JSON with your Spotify statistics!

### Step 6: Use in Your GitHub README

Add the following to any GitHub README to display your stats:

```markdown
! ADD finished URI !
```

## Try out locally

Create a .env file in the project root:

```
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
SPOTIFY_REFRESH_TOKEN=your_refresh_token
```

Run the collector directly:

```bash
python -m dotenv run -- python -m statsCollector
```

Or run the Flask API locally:

```bash
cd api
python -m dotenv run -- python index.py
```

Running Tests

```bash
python -m dotenv run -- python -m pytest -q
```
