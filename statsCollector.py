## Inspired from https://github.com/ni5arga/spotify-stats-python, https://spotipy.readthedocs.io/en/2.25.1/, https://github.com/spotipy-dev/spotipy-examples/tree/c610a79705ef4aa55e4d61572a012f77b6f7245d/scripts and https://developer.spotify.com/documentation/web-api/reference/get-users-saved-albums
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os, json


def setup_spotify_client():
    SPOTIPY_CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID")
    SPOTIPY_CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET")
    SPOTIPY_REDIRECT_URI = os.environ.get("SPOTIPY_REDIRECT_URI")
    SCOPE = "user-library-read user-top-read user-read-recently-played user-read-playback-state"

    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,
            scope=SCOPE,
        )
    )

    return sp


def get_user_top_artists(sp: spotipy.Spotify):
    # Get User's Top Artists names and pictures, both for short term and long term listening activities
    topArtistsData = {}
    print("|====== To Artists ======|")
    for sp_range in ["short_term", "long_term"]:
        print("Range:", sp_range)

        topArtists = sp.current_user_top_artists(time_range=sp_range, limit=5)
        topArtistsDataRange = {}

        for id, artist in enumerate(topArtists["items"]):
            topArtistsDataRange[id] = {
                "name": artist["name"],
                "image": artist["images"][0]["url"],
                "genre": artist["genres"][0] if artist["genres"] else "N/A",
            }
            print(
                id,
                artist["name"],
                artist["images"][0]["url"],
                artist["genres"][0] if artist["genres"] else "N/A",
            )
        print()
        topArtistsData[sp_range] = topArtistsDataRange

    return topArtistsData


def get_user_top_songs(sp: spotipy.Spotify):
    # Get User's Top Songs names, artists names and pictures, both for short term and long term listening activities
    topSongsData = {}
    print("|====== Top Songs ======|")
    for sp_range in ["short_term", "long_term"]:
        print("Range:", sp_range)

        topSongs = sp.current_user_top_tracks(time_range=sp_range, limit=5)
        topSongsDataRange = {}
        for id, song in enumerate(topSongs["items"]):
            topSongsDataRange[id] = {
                "name": song["name"],
                "artist": song["artists"][0]["name"],
                "image": song["album"]["images"][0]["url"],
            }
            print(
                id,
                song["name"],
                "//",
                song["artists"][0]["name"],
                song["album"]["images"][0]["url"],
            )
        print()
        topSongsData[sp_range] = topSongsDataRange
    return topSongsData


def get_user_last_listenedTo_albums(sp: spotipy.Spotify):
    # Get User's Last Saved Albums names and artists names
    lastSavedAlbumsData = {}
    print("|====== Last Saved Albums ======|")
    savedAlbums = sp.current_user_saved_albums(limit=3)
    for id, item in enumerate(savedAlbums["items"]):
        album = item["album"]
        lastSavedAlbumsData[id] = {
            "name": album["name"],
            "artist": album["artists"][0]["name"],
        }
        print(id, album["name"], "//", album["artists"][0]["name"])
    print()
    return lastSavedAlbumsData


def get_user_data(sp: spotipy.Spotify):
    artistsData = get_user_top_artists(sp)
    userDataJson["top_artists"] = artistsData

    songsData = get_user_top_songs(sp)
    userDataJson["top_songs"] = songsData

    lastAlbums = get_user_last_listenedTo_albums(sp)
    userDataJson["last_albums"] = lastAlbums


if __name__ == "__main__":
    spClient = setup_spotify_client()

    userDataJson = {}
    get_user_data(spClient)
    json_data = json.dumps(userDataJson, indent=4)
    print(json_data)
