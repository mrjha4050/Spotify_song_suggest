import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import json
import random
import time

# generate your client id from spotify developer 
CLIENT_ID = "client id"
CLIENT_SECRET = "secret - client "

model_name = "gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

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

user_genre = input("Enter your choice (Hindi, English, or both): ")
generate_seed_tracks(user_genre)


def get_song_recommendations(user_genre, sp):
    recommendations = sp.recommendations(seed_tracks=seed_tracks, limit=5)
    songs = [track["name"] for track in recommendations["tracks"]]
    return songs

def chat_with_gpt(input_text):
    input_ids = tokenizer.encode(input_text, return_tensors="pt")
    attention_mask = torch.ones(input_ids.shape, dtype=torch.long)
    response = model.generate(
        input_ids,
        attention_mask=attention_mask,
        pad_token_id=tokenizer.eos_token_id,
        max_length=50,
        num_return_sequences=1,
    )
    response_text = tokenizer.decode(
        response[:, input_ids.shape[-1] :][0], skip_special_tokens=True
    )
    return response_text

sp = authenticate_spotify()

# limit = int(input("Enter the number of songs to suggest: "))
# user_input = input("Enter your Genre: ")
suggested_songs = get_song_recommendations(user_genre, sp)

print("Searching songs for you...\n")


with open("quotes.txt", "r") as f:
    quotes = [line.strip() for line in f.readlines()]

print(random.choice(quotes), "\n")
time.sleep(6)
print("Suggested songs:")
print("\n")

for song in suggested_songs:
    print(song)

print("\n")
print("Link of the songs:")

def get_track_link(song_name):
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
    print(f"{song_name}: {link}\n")

output_file = "suggested_songs.txt"
with open(output_file, "a") as f:
    f.write("Suggested songs:\n\n")
    for song_name, link in song_info.items():
        f.write(f"{song_name}: {link}\n")

print("Suggested songs with links have been saved to:", output_file)
