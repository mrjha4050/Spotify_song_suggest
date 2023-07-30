import spotipy 
from spotipy.oauth2 import SpotifyClientCredentials
import json
import random
import time
import openai
import streamlit as st
import os

# generate your client id from spotify developer c
CLIENT_ID = ""
CLIENT_SECRET = ""

OPENAI_API_KEY = ""

st.title("🎧🎵 Spotify Playlist Generator")

with open('seed_tracks.json', 'r') as f:
    data = json.load(f)

seed_tracks = data['seed_tracks']

def authenticate_spotify():
    client_credentials_manager = SpotifyClientCredentials(
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return sp

def get_track_ids(sp, genre, limit=5):
    track_ids = []
    offset = 0
    while len(track_ids) < limit:
        results = sp.search(q="genre:" + genre, type="track", limit=limit, offset=offset)
        new_track_ids = [track["id"] for track in results["tracks"]["items"]]
        # Filter out duplicate track IDs
        new_track_ids = [track_id for track_id in new_track_ids if track_id not in track_ids]
        track_ids.extend(new_track_ids)
        offset += limit
    return track_ids

def generate_seed_tracks(genre):
    sp = authenticate_spotify()
    track_ids = get_track_ids(sp, genre, limit=5)

    seed_tracks = []
    for track_id in track_ids:
        seed_tracks.append(track_id)

    random.shuffle(seed_tracks)

    seed_data = {
        "seed_tracks": seed_tracks
    }
    with open("seed_tracks.json", "w") as f:
        json.dump(seed_data, f, indent=4)
    print("New seed track JSON file has been generated.")


if not os.path.exists('seed_tracks.json'):
    st.info("Generating new seed tracks. Please wait...")
    generate_seed_tracks("Hindi")  # Default to "Hindi" if no user input
    st.success("New seed tracks generated.")
else:
    with open('seed_tracks.json', 'r') as f:
        data = json.load(f)
    seed_tracks = data['seed_tracks']

user_genre = st.text_input("Enter your choice (Hindi, English, or both) : ")
generate_seed_tracks(user_genre)


def get_song_recommendations(user_genre, sp):
    recommendations = sp.recommendations(seed_tracks=seed_tracks, limit=5)
    songs = [track["name"] for track in recommendations["tracks"]]
    return songs

def chat_with_gpt(input_text):
    response = openai.Completion.create(
        engine="text-davinci-002",  # Use the appropriate GPT-3 engine
        prompt=input_text,
        max_tokens=50,
        n=1,  # Number of responses to generate
        stop=None,  # Set stop condition if needed
    )
    response_text = response['choices'][0]['text'].strip()
    return response_text

def get_suggested_songs(user_genre):
    sp = authenticate_spotify()
    return get_song_recommendations(user_genre, sp)

suggested_songs = get_suggested_songs(user_genre)

# suggested_songs = get_song_recommendations(user_genre, sp)

st.text("Searching songs for you...\n")

with open("quotes.txt", "r") as f:
    quotes = [line.strip() for line in f.readlines()]

st.text(random.choice(quotes))
time.sleep(6)
st.text("Suggested songs:")

for song in suggested_songs:
    st.text(song)

# print("\n")
st.text("Link of the songs:")

def get_track_link(song_name):
    sp = authenticate_spotify()
    results = sp.search(q=f"track:{song_name}", type="track", limit=1)
    if len(results["tracks"]["items"]) > 0:
        track_id = results["tracks"]["items"][0]["id"]
        return f"https://open.spotify.com/track/{track_id}"
    return None

song_info = {}
for song_name in suggested_songs:
    link = get_track_link(song_name)
    if link:
        song_info[song_name] = link

for song_name, link in song_info.items():
    st.markdown(f'<a href="{link}" target="_blank">{song_name}</a>', unsafe_allow_html=True)

output_file = "suggested_songs.txt"
with open(output_file, "w") as f:
    f.write("Suggested songs:\n\n")
    for song_name, link in song_info.items():
        f.write(f"{song_name}: {link}\n")

st.text(f"Suggested songs with links have been saved to :suggested_songs.txt")
