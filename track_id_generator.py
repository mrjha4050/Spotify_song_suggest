import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
from spotipy.oauth2 import SpotifyOAuth
import json

CLIENT_ID = "client-id"
CLIENT_SECRET = "client-secret"

model_name = "gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

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

def get_song_recommendations(user_input, sp, limit):
    genre_songs = []
    if "hindi" in user_input.lower():
        track_ids = get_track_ids(sp, "hindi", limit)
        genre_songs.extend(track_ids)
    if "english" in user_input.lower():
        track_ids = get_track_ids(sp, "english", limit)
        genre_songs.extend(track_ids)
    return genre_songs

def chat_with_gpt(input_text):
    input_ids = tokenizer.encode(input_text, return_tensors="pt")
    attention_mask = torch.ones(input_ids.shape, dtype=torch.long)
    response = model.generate(input_ids, attention_mask=attention_mask, pad_token_id=tokenizer.eos_token_id, max_length=50, num_return_sequences=1)
    response_text = tokenizer.decode(
        response[:, input_ids.shape[-1]:][0], skip_special_tokens=True
    )
    return response_text

sp = authenticate_spotify()

user_input = input("Enter your language (Hindi, English, or both): ")
suggested_track_ids = get_song_recommendations(user_input, sp, 5)

print("Searching songs.......")
print("Suggested songs:")
for track_id in suggested_track_ids:
    print(f"Track ID: {track_id}")

seed_tracks = {"seed_tracks": suggested_track_ids}
with open("seed_tracks.json", "w") as f:
    json.dump(seed_tracks, f)

print("Seed track IDs have been saved to seed_tracks.json")
