# Test suite for statsCollector.py
# Mostly written by Claude Sonnet 4.5 because I can't be bothered

import pytest
import statsCollector


def test_import_spotify_client():
    spClient = statsCollector.setup_spotify_client()
    assert spClient is not None
    # Check that the client has an expected method
    assert hasattr(spClient, "current_user")


class TestGetUserTopArtistsExtended:
    """Extended test suite for get_user_top_artists with edge cases"""

    @pytest.fixture
    def mock_spotify(self, mocker):
        """Fixture to create a mocked Spotify client"""
        return mocker.Mock()

    def test_get_user_top_artists_handles_empty_images_array(self, mock_spotify):
        """Test that function handles artists with empty images array"""
        mock_spotify.current_user_top_artists.return_value = {
            "items": [
                {
                    "name": "Test Artist",
                    "images": [],  # Empty images array
                    "genres": ["rock"],
                }
            ]
        }

        # This should raise an IndexError with current implementation
        with pytest.raises(IndexError):
            statsCollector.get_user_top_artists(mock_spotify)

    def test_get_user_top_artists_handles_no_items(self, mock_spotify):
        """Test that function handles API response with no items"""
        mock_spotify.current_user_top_artists.return_value = {"items": []}

        result = statsCollector.get_user_top_artists(mock_spotify)

        assert result["short_term"] == {}
        assert result["long_term"] == {}

    def test_get_user_top_artists_returns_correct_dict_keys(self, mock_spotify):
        """Test that function returns dictionary with integer keys"""
        mock_spotify.current_user_top_artists.return_value = {
            "items": [
                {
                    "name": "Artist 1",
                    "images": [{"url": "http://test.com/img.jpg"}],
                    "genres": ["pop"],
                }
            ]
        }

        result = statsCollector.get_user_top_artists(mock_spotify)

        # Verify integer keys
        assert 0 in result["short_term"]
        assert isinstance(list(result["short_term"].keys())[0], int)

    def test_get_user_top_artists_multiple_genres(self, mock_spotify):
        """Test that function extracts first genre from multiple genres"""
        mock_spotify.current_user_top_artists.return_value = {
            "items": [
                {
                    "name": "Multi-Genre Artist",
                    "images": [{"url": "http://test.com/img.jpg"}],
                    "genres": ["rock", "alternative", "indie"],
                }
            ]
        }

        result = statsCollector.get_user_top_artists(mock_spotify)

        assert result["short_term"][0]["genre"] == "rock"


class TestGetUserTopSongsExtended:
    """Extended test suite for get_user_top_songs with edge cases"""

    @pytest.fixture
    def mock_spotify(self, mocker):
        """Fixture to create a mocked Spotify client"""
        return mocker.Mock()

    def test_get_user_top_songs_handles_empty_album_images(self, mock_spotify):
        """Test that function handles songs with no album images"""
        mock_spotify.current_user_top_tracks.return_value = {
            "items": [
                {
                    "name": "Test Song",
                    "artists": [{"name": "Test Artist"}],
                    "album": {"images": []},  # Empty images
                }
            ]
        }

        # This should raise an IndexError with current implementation
        with pytest.raises(IndexError):
            statsCollector.get_user_top_songs(mock_spotify)

    def test_get_user_top_songs_handles_empty_artists_array(self, mock_spotify):
        """Test that function handles songs with no artists"""
        mock_spotify.current_user_top_tracks.return_value = {
            "items": [
                {
                    "name": "Test Song",
                    "artists": [],  # No artists
                    "album": {"images": [{"url": "http://test.com/img.jpg"}]},
                }
            ]
        }

        # This should raise an IndexError with current implementation
        with pytest.raises(IndexError):
            statsCollector.get_user_top_songs(mock_spotify)

    def test_get_user_top_songs_returns_integer_keys(self, mock_spotify):
        """Test that function returns dictionary with integer keys"""
        mock_spotify.current_user_top_tracks.return_value = {
            "items": [
                {
                    "name": "Song 1",
                    "artists": [{"name": "Artist 1"}],
                    "album": {"images": [{"url": "http://test.com/img1.jpg"}]},
                },
                {
                    "name": "Song 2",
                    "artists": [{"name": "Artist 2"}],
                    "album": {"images": [{"url": "http://test.com/img2.jpg"}]},
                },
            ]
        }

        result = statsCollector.get_user_top_songs(mock_spotify)

        # Verify integer keys and correct count
        assert 0 in result["short_term"]
        assert 1 in result["short_term"]
        assert len(result["short_term"]) == 2


class TestGetUserLastListenedToAlbumsExtended:
    """Extended test suite for get_user_last_listenedTo_albums"""

    @pytest.fixture
    def mock_spotify(self, mocker):
        """Fixture to create a mocked Spotify client"""
        return mocker.Mock()

    def test_get_user_last_listenedTo_albums_handles_empty_artists(self, mock_spotify):
        """Test that function handles albums with no artists"""
        mock_spotify.current_user_saved_albums.return_value = {
            "items": [{"album": {"name": "Test Album", "artists": []}}]
        }

        # This should raise an IndexError with current implementation
        with pytest.raises(IndexError):
            statsCollector.get_user_last_listenedTo_albums(mock_spotify)

    def test_get_user_last_listenedTo_albums_returns_integer_keys(self, mock_spotify):
        """Test that function returns dictionary with integer keys"""
        mock_spotify.current_user_saved_albums.return_value = {
            "items": [
                {"album": {"name": "Album 1", "artists": [{"name": "Artist 1"}]}},
                {"album": {"name": "Album 2", "artists": [{"name": "Artist 2"}]}},
            ]
        }

        result = statsCollector.get_user_last_listenedTo_albums(mock_spotify)

        assert 0 in result
        assert 1 in result
        assert isinstance(list(result.keys())[0], int)

    def test_get_user_last_listenedTo_albums_empty_response(self, mock_spotify):
        """Test that function handles empty saved albums"""
        mock_spotify.current_user_saved_albums.return_value = {"items": []}

        result = statsCollector.get_user_last_listenedTo_albums(mock_spotify)

        assert result == {}


class TestGetUserDataExtended:
    """Extended test suite for get_user_data function"""

    @pytest.fixture
    def mock_spotify(self, mocker):
        """Fixture to create a mocked Spotify client"""
        return mocker.Mock()

    def test_get_user_data_missing_albums_in_json(self, mocker, mock_spotify):
        """Test that get_user_data properly assigns albums data to userDataJson"""
        # This test reveals a bug: albums are not assigned to userDataJson
        mock_artists = mocker.patch("statsCollector.get_user_top_artists")
        mock_songs = mocker.patch("statsCollector.get_user_top_songs")
        mock_albums = mocker.patch("statsCollector.get_user_last_listenedTo_albums")

        mock_artists.return_value = {"short_term": {}, "long_term": {}}
        mock_songs.return_value = {"short_term": {}, "long_term": {}}
        mock_albums.return_value = {"0": {"name": "Album", "artist": "Artist"}}

        statsCollector.userDataJson = {}
        statsCollector.get_user_data(mock_spotify)

        # This assertion will FAIL with current code - albums not assigned
        # The bug is in line: get_user_last_listenedTo_albums(sp) without assignment
        assert "last_albums" in statsCollector.userDataJson
        assert statsCollector.userDataJson["last_albums"] == mock_albums.return_value

    def test_get_user_data_preserves_return_values(self, mocker, mock_spotify):
        """Test that get_user_data doesn't modify returned data"""
        mock_artists = mocker.patch("statsCollector.get_user_top_artists")
        mock_songs = mocker.patch("statsCollector.get_user_top_songs")
        mock_albums = mocker.patch("statsCollector.get_user_last_listenedTo_albums")

        artists_data = {"short_term": {"0": {"name": "A"}}, "long_term": {}}
        songs_data = {"short_term": {"0": {"name": "S"}}, "long_term": {}}
        albums_data = {"0": {"name": "Album"}}

        mock_artists.return_value = artists_data
        mock_songs.return_value = songs_data
        mock_albums.return_value = albums_data

        statsCollector.userDataJson = {}
        statsCollector.get_user_data(mock_spotify)

        # Verify data integrity
        assert statsCollector.userDataJson["top_artists"] == artists_data
        assert statsCollector.userDataJson["top_songs"] == songs_data


class TestErrorHandling:
    """Test suite for error handling and exception scenarios"""

    @pytest.fixture
    def mock_spotify(self, mocker):
        """Fixture to create a mocked Spotify client"""
        return mocker.Mock()

    def test_get_user_top_artists_handles_api_exception(self, mock_spotify):
        """Test that API exceptions are propagated correctly"""
        from spotipy.exceptions import SpotifyException

        mock_spotify.current_user_top_artists.side_effect = SpotifyException(
            http_status=401, code=-1, msg="Unauthorized"
        )

        with pytest.raises(SpotifyException):
            statsCollector.get_user_top_artists(mock_spotify)

    def test_get_user_top_songs_handles_api_timeout(self, mock_spotify):
        """Test that network timeout exceptions are propagated"""
        import requests

        mock_spotify.current_user_top_tracks.side_effect = requests.exceptions.Timeout(
            "Request timed out"
        )

        with pytest.raises(requests.exceptions.Timeout):
            statsCollector.get_user_top_songs(mock_spotify)

    def test_get_user_last_listenedTo_albums_handles_network_error(self, mock_spotify):
        """Test that network errors are propagated"""
        import requests

        mock_spotify.current_user_saved_albums.side_effect = (
            requests.exceptions.ConnectionError("Network error")
        )

        with pytest.raises(requests.exceptions.ConnectionError):
            statsCollector.get_user_last_listenedTo_albums(mock_spotify)


class TestDataIntegrity:
    """Test suite for data integrity and format validation"""

    @pytest.fixture
    def mock_spotify(self, mocker):
        """Fixture to create a mocked Spotify client"""
        return mocker.Mock()

    def test_get_user_top_artists_data_format(self, mock_spotify):
        """Test that returned data has expected structure and types"""
        mock_spotify.current_user_top_artists.return_value = {
            "items": [
                {
                    "name": "Test Artist",
                    "images": [{"url": "http://example.com/img.jpg"}],
                    "genres": ["pop"],
                }
            ]
        }

        result = statsCollector.get_user_top_artists(mock_spotify)

        # Verify structure
        assert isinstance(result, dict)
        assert "short_term" in result
        assert "long_term" in result

        # Verify data types
        for time_range in ["short_term", "long_term"]:
            assert isinstance(result[time_range], dict)
            if result[time_range]:
                item = result[time_range][0]
                assert isinstance(item["name"], str)
                assert isinstance(item["image"], str)
                assert isinstance(item["genre"], str)

    def test_get_user_top_songs_data_format(self, mock_spotify):
        """Test that returned song data has expected structure"""
        mock_spotify.current_user_top_tracks.return_value = {
            "items": [
                {
                    "name": "Test Song",
                    "artists": [{"name": "Test Artist"}],
                    "album": {"images": [{"url": "http://example.com/img.jpg"}]},
                }
            ]
        }

        result = statsCollector.get_user_top_songs(mock_spotify)

        # Verify structure
        for time_range in ["short_term", "long_term"]:
            if result[time_range]:
                item = result[time_range][0]
                assert "name" in item
                assert "artist" in item
                assert "image" in item
                assert isinstance(item["name"], str)
                assert isinstance(item["artist"], str)
                assert isinstance(item["image"], str)

    def test_get_user_last_listenedTo_albums_data_format(self, mock_spotify):
        """Test that returned album data has expected structure"""
        mock_spotify.current_user_saved_albums.return_value = {
            "items": [
                {"album": {"name": "Test Album", "artists": [{"name": "Test Artist"}]}}
            ]
        }

        result = statsCollector.get_user_last_listenedTo_albums(mock_spotify)

        # Verify structure
        assert isinstance(result, dict)
        if result:
            item = result[0]
            assert "name" in item
            assert "artist" in item
            assert isinstance(item["name"], str)
            assert isinstance(item["artist"], str)


class TestSetupSpotifyClientExtended:
    """Extended tests for setup_spotify_client function"""

    def test_setup_spotify_client_missing_env_vars(self, mocker, monkeypatch):
        """Test that function handles missing environment variables"""
        # Clear environment variables
        monkeypatch.delenv("SPOTIPY_CLIENT_ID", raising=False)
        monkeypatch.delenv("SPOTIPY_CLIENT_SECRET", raising=False)
        monkeypatch.delenv("SPOTIPY_REDIRECT_URI", raising=False)

        mock_oauth = mocker.patch("statsCollector.SpotifyOAuth")
        mocker.patch("statsCollector.spotipy.Spotify")

        statsCollector.setup_spotify_client()

        # Verify OAuth was called with None values
        call_kwargs = mock_oauth.call_args[1]
        assert call_kwargs["client_id"] is None
        assert call_kwargs["client_secret"] is None
        assert call_kwargs["redirect_uri"] is None

    def test_setup_spotify_client_scope_string_format(self, mocker, monkeypatch):
        """Test that scope is a properly formatted string"""
        monkeypatch.setenv("SPOTIPY_CLIENT_ID", "test_id")
        monkeypatch.setenv("SPOTIPY_CLIENT_SECRET", "test_secret")
        monkeypatch.setenv("SPOTIPY_REDIRECT_URI", "http://localhost:8080")

        mock_oauth = mocker.patch("statsCollector.SpotifyOAuth")
        mocker.patch("statsCollector.spotipy.Spotify")

        statsCollector.setup_spotify_client()

        call_kwargs = mock_oauth.call_args[1]
        scope = call_kwargs["scope"]

        # Verify it's a string, not a list
        assert isinstance(scope, str)
        # Verify scopes are space-separated
        assert " " in scope


class TestCallSequence:
    """Test suite to verify correct call sequences"""

    def test_get_user_data_calls_in_correct_order(self, mocker):
        """Test that get_user_data calls functions in expected order"""
        call_order = []

        def track_artists(sp):
            call_order.append("artists")
            return {"short_term": {}, "long_term": {}}

        def track_songs(sp):
            call_order.append("songs")
            return {"short_term": {}, "long_term": {}}

        def track_albums(sp):
            call_order.append("albums")
            return {}

        mocker.patch("statsCollector.get_user_top_artists", side_effect=track_artists)
        mocker.patch("statsCollector.get_user_top_songs", side_effect=track_songs)
        mocker.patch(
            "statsCollector.get_user_last_listenedTo_albums", side_effect=track_albums
        )

        statsCollector.userDataJson = {}
        mock_sp = mocker.Mock()
        statsCollector.get_user_data(mock_sp)

        # Verify order
        assert call_order == ["artists", "songs", "albums"]
