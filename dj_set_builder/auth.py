import spotipy

def get_authorised_spotify(username: str, client_id: str, client_secret: str, redirect_uri: str):
    scope='user-read-playback-state,user-modify-playback-state,playlist-modify-private,playlist-modify-public'
    token = spotipy.util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)
    sp = spotipy.Spotify(auth=token)
    return sp