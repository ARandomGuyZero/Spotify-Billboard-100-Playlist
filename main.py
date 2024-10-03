"""
Spotify Billboard 100 Playlist

Author: Alan
Date: October 3rd 2024

This script creates a playlist of songs based on the date the user inputs to.
The list comes from: https://www.billboard.com
More info: https://spotipy.readthedocs.io/en/2.24.0/
"""

from os import environ
from requests import get
from bs4 import BeautifulSoup
from spotipy import SpotifyOAuth, Spotify
from dotenv import load_dotenv
import lxml

load_dotenv()

# Make sure to fill the .env file
YOUR_CLIENT_ID = environ["YOUR_CLIENT_ID"]
YOUR_CLIENT_SECRET = environ["YOUR_CLIENT_SECRET"]

def get_song_list(date_format : str):
    """
    Gets a list of songs using the site https://www.billboard.com via web scrapping.
    :param date_format: String with the date in YYYY-MM-DD format
    :return: A list of strings with the names of the songs
    """
    # Get the link of the 100 songs
    url = "https://www.billboard.com/charts/hot-100/" + date_format

    # Get the webpage code
    webpage = get(url, headers={"User-Agent": "Mozilla/5.0"}).text

    # New soup object with the webpage data
    soup = BeautifulSoup(webpage, "lxml")

    # Search through the elements to find the songs
    all_songs = soup.select("li ul li h3")

    # Get a list of all songs
    return [song_name.getText().strip() for song_name in all_songs]

def spotify_authentication():
    """
    Gets the authentication from Spotify to use their API.
    More info: https://spotipy.readthedocs.io/en/2.24.0/#authorization-code-flow
    :return:
    """

    # Spotify Authentication
    spotify = Spotify(
        auth_manager=SpotifyOAuth(
            scope="playlist-modify-private",
            redirect_uri="http://example.com",
            client_id=YOUR_CLIENT_ID,
            client_secret=YOUR_CLIENT_SECRET,
            show_dialog=True,
            cache_path="token.txt"
        )
    )

    # Get the user id
    spotify_user_id = spotify.current_user()["id"]

    return spotify, spotify_user_id

def get_song_uris(song_year, top_song_list):
    """
    Using the songs and the year, it searches the songs in the Spotify database to retrieve the URIs.
    More info: https://spotipy.readthedocs.io/en/2.24.0/#api-reference
    :param song_year: String with the year of the songs
    :param top_song_list: List of strings with the lists of the songs
    :return: List of data with the songs URIs
    """

    song_uris = []

    # For each song in song_list
    for song in top_song_list:

        # Search each of the songs
        result = sp.search(q=f"track:{song} year:{song_year}", type="track")
        print(result)
        try:
            uri = result["tracks"]["items"][0]["uri"]
            song_uris.append(uri)
        except IndexError:
            print(f"{song} doesn't exist in Spotify. Skipped.")

    return song_uris

def create_playlist(song_uris):
    """
    Creates a new playlist using the list of songs URIs.
    More info: https://spotipy.readthedocs.io/en/2.24.0/#api-reference
    :param song_uris: List of songs URIs
    :return:
    """
    # Get the variables
    playlist_name = date + " Billboard 100"
    playlist_description = "Best songs of " + date

    # Create a new user playlist
    playlist = sp.user_playlist_create(user_id, playlist_name, public=False, description=playlist_description)

    sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)

is_date_correct = False
date = ""
song_list = []

# Simple loop to get a list of songs as long the URL exists
while not is_date_correct:

    # Ask the user for the date
    date = input("Which year do you want to travel to? (YYYY-MM-DD)\n")

    song_list = get_song_list(date_format=date)

    # If we found the list, and it exists, then we will break the loop and continue
    if song_list:
        is_date_correct = True
        break

    # If the user didn't manage to get a right date, it'll ask again
    print("Sorry, we have no songs for this date")

# Get the spotify authentication and the user id
sp, user_id = spotify_authentication()

# Get the year of the date
year = date.split("-")[0]

# Get a list for songs of a year
uris_list = get_song_uris(year, song_list)

# Create your own user list based on the user list
create_playlist(uris_list)
