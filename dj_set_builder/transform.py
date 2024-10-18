import pandas as pd
import numpy as np


def tabulate_playlist(spotify_results: dict) -> pd.DataFrame:
    out = pd.DataFrame([
        extract_track_details(item["track"])
        for item in spotify_results['tracks']['items']
    ])
    out.index.name = "order"
    out = out.reset_index().set_index('id')
    return out


def tabulate_reccs(spotify_results: dict) -> pd.DataFrame:
    out = pd.DataFrame([
        extract_track_details(item)
        for item in spotify_results['tracks']
    ])
    out.index.name = "order"
    out = out.reset_index().set_index('id')
    return out


def extract_track_details(track) -> dict:
    details = {
        'id': track['id'],
        'track_name': track['name'],
        'artist_name': track['artists'][0]['name'],
        # 'duration_ms': track['duration_ms'],
        # 'duration_min': np.floor(track['duration_ms']/60000),
        # 'duration_sec': track['duration_ms'] % 60000 / 1000
    }
    return details