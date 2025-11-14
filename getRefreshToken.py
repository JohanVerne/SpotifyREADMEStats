# Run this ONCE on your machine to get a refresh token for Spotify API access
import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = SpotifyOAuth(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    redirect_uri="http://localhost:8888/callback",
    scope="user-library-read user-top-read user-read-recently-played user-read-playback-state",
)

token_info = sp.get_access_token()
print("Refresh Token:", token_info["refresh_token"])
# Save this refresh token - it doesn't expire!
