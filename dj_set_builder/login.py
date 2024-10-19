import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

# Spotify API credentials
load_dotenv("spotify.env")
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID") or st.secrets["SPOTIPY_CLIENT_ID"]
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET") or st.secrets["SPOTIPY_CLIENT_SECRET"]
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI") or st.secrets["SPOTIPY_REDIRECT_URI"]
SCOPE = 'playlist-read-private user-library-read'

# Set up the SpotifyOAuth object
sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        redirect_uri=REDIRECT_URI,
                        scope=SCOPE)

def get_token_from_url_code():
    code = st.query_params['code']
    st.write(code)
    token_info = sp_oauth.get_access_token(code, as_dict=False)
    st.session_state['token_info'] = token_info
    st.write(token_info)
    return token_info

# Function to get user info and playlists
def get_playlists():
    sp = spotipy.Spotify(auth_manager=sp_oauth)
    playlists = sp.current_user_playlists()
    return playlists

# Streamlit app
def main():
    if 'code' in st.query_params:
        st.session_state.token_info = get_token_from_url_code()

    st.title("Spotify Playlist Loader")

    # Check if the user is authenticated
    if st.session_state.get('token_info'):
        # Use the token to get playlists
        token_info = st.session_state['token_info']
        sp = spotipy.Spotify(auth=token_info)

        playlists = get_playlists()
        
        st.write("Your Playlists:")
        for playlist in playlists['items']:
            st.write(playlist['name'])
            st.write(playlist['external_urls']['spotify'])

    else:
        # Redirect user to authenticate with Spotify
        st.write("Please log in to Spotify")
        auth_url = sp_oauth.get_authorize_url()
        st.markdown(f"[Log in to Spotify]({auth_url})")

        # Handle callback to capture token
        if 'code' in st.query_params:
            get_token_from_url_code()

if __name__ == "__main__":
    main()
