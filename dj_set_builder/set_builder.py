import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

from auth import get_authorised_spotify
from transform import tabulate_playlist, tabulate_reccs
from vars import TARGET_PLAYLIST_URI, FILTER_DEFAULTS, N_FILTER_COLUMNS


import spotipy
from spotipy.oauth2 import SpotifyOAuth

def get_token(oauth, code):

    token = oauth.get_access_token(code, as_dict=False, check_cache=False)
    # remove cached token saved in directory
    os.remove(".cache")
    
    # return the token
    return token


def sign_in(token):
    sp = spotipy.Spotify(auth=token)
    return sp


def app_get_token():
    try:
        token = get_token(st.session_state["oauth"], st.session_state["code"])
    except Exception as e:
        st.error("An error occurred during token retrieval!")
        st.write("The error is as follows:")
        st.write(e)
    else:
        st.session_state["cached_token"] = token



def app_sign_in():
    try:
        sp = sign_in(st.session_state["cached_token"])
    except Exception as e:
        st.error("An error occurred during sign-in!")
        st.write("The error is as follows:")
        st.write(e)
    else:
        st.session_state["signed_in"] = True
        app_display_welcome()
        st.success("Sign in success!")
        
    return sp


def app_display_welcome():
    
    # import secrets from streamlit deployment
    spotify_client_id = os.getenv("SPOTIPY_CLIENT_ID") or st.secrets["SPOTIPY_CLIENT_ID"]
    spotify_secret = os.getenv("SPOTIPY_CLIENT_SECRET") or st.secrets["SPOTIPY_CLIENT_SECRET"]
    spotipy_redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI") or st.secrets["SPOTIPY_REDIRECT_URI"]


    # set scope and establish connection
    scopes='user-read-playback-state,user-modify-playback-state,playlist-modify-private,playlist-modify-public'


    # create oauth object
    oauth = SpotifyOAuth(scope=scopes,
                         redirect_uri=spotipy_redirect_uri,
                         client_id=spotify_client_id,
                         client_secret=spotify_secret)
    
    # store oauth in session
    st.session_state["oauth"] = oauth

    # retrieve auth url
    auth_url = oauth.get_authorize_url()
    
    # this SHOULD open the link in the same tab when Streamlit Cloud is updated
    # via the "_self" target
    link_html = " <a target=\"_self\" href=\"{url}\" >{msg}</a> ".format(
        url=auth_url,
        msg="Click me to authenticate!"
    )
    


    st.title("DJ Set Builder")

    if not st.session_state["signed_in"]:
        st.write(" ".join(["No tokens found for this session. Please log in by",
                          "clicking the link below."]))
        st.markdown(link_html, unsafe_allow_html=True)

        st.session_state["code"] = st.text_input(label="Code")
        st.session_state["cached_token"] = get_token(st.session_state["oauth"], st.session_state["code"])
        st.session_state["signed_in"] = True


# Initialization
def initialise():
    if 'spotify' not in st.session_state:
        st.write("No spotify session state found!")
        load_dotenv("spotify.env")
        st.session_state.spotify_username = os.getenv("SPOTIPY_USERNAME")
        spotify_client_id = os.getenv("SPOTIPY_CLIENT_ID") or st.secrets["SPOTIPY_CLIENT_ID"]
        spotify_secret = os.getenv("SPOTIPY_CLIENT_SECRET") or st.secrets["SPOTIPY_CLIENT_SECRET"]
        spotipy_redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI") or st.secrets["SPOTIPY_REDIRECT_URI"]


        if "signed_in" not in st.session_state:
            st.session_state["signed_in"] = False
        if "cached_token" not in st.session_state:
            st.session_state["cached_token"] = ""
        if "code" not in st.session_state:
            st.session_state["code"] = ""
        if "oauth" not in st.session_state:
            st.session_state["oauth"] = None

        # %% authenticate with response stored in url

        # get current url (stored as dict)
        url_params = st.query_params

        # attempt sign in with cached token
        if st.session_state["cached_token"] != "":
            sp = app_sign_in()
        # if no token, but code in url, get code, parse token, and sign in
        elif "code" in url_params:
            # all params stored as lists, see doc for explanation
            st.session_state["code"] = url_params["code"][0]
            app_get_token()
            sp = app_sign_in()
        # otherwise, prompt for redirect
        else:
            app_display_welcome()


        st.session_state.spotify = SpotifyInterface()
        st.session_state.playlist_id = None
        st.session_state.recommendations = pd.DataFrame()
        st.session_state.filter_settings = FILTER_DEFAULTS        
        st.session_state.filter_ranges = {}


class PlaylistSelectorPanel:
    def display():
        current_username = st.session_state.spotify_username
        new_username = st.text_input(label="Spotify username", value=current_username)
        current_playlist_id = st.session_state.playlist_id
        new_playlist_id = st.text_input(label="Playlist ID", value=TARGET_PLAYLIST_URI)
        if (new_playlist_id != current_playlist_id) or (new_username != current_username):
            st.session_state.playlist_id = new_playlist_id
            st.session_state.spotify_username = new_username
            st.session_state.spotify.fetch_playlist()
        st.write("------")


class PlaylistPanel:
    def display():
        st.write("Playlist")
        st.session_state.track_seed_selection = st.dataframe(
            st.session_state.playlist,
            on_select="rerun",
            selection_mode="multi-row",
        )["selection"]["rows"]
        with st.form(key='seed_track_chooser'):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                play_button = st.form_submit_button(label='▶️', on_click=PlaylistPanel.play_button_selected)
            with col2:
                stop_button = st.form_submit_button(label='⏹️', on_click=st.session_state.spotify.stop)
            with col3:        
                submit_button = st.form_submit_button(label='🍒 Generate recommendations!', on_click=PlaylistPanel.seed_track_chooser_submit)
            with col4:
                delete_button = st.form_submit_button(label='❌ Delete tracks!', on_click=PlaylistPanel.delete_button_selected)
        st.write("------")

    def play_button_selected():
        track_id = PlaylistPanel.get_track_ids_from_selection()[-1]
        if track_id:
            try:
                st.session_state.spotify.play_track(track_id)
            except:
                st.write("Failed to start the Spotify player!")

    def delete_button_selected():
        track_ids = PlaylistPanel.get_track_ids_from_selection()
        if len(track_ids) > 0:
            st.session_state.spotify.remove_tracks_from_playlist(track_ids)
            st.session_state.spotify.fetch_playlist()

    def get_track_ids_from_selection():
        if st.session_state.track_seed_selection != []: 
            selected_rows = st.session_state.track_seed_selection
            track_id = st.session_state.playlist.iloc[selected_rows].index
            return track_id
        return None

    def seed_track_chooser_submit():
        RecommendationsPanel.fetch_recommendations() 
        

class RecommendationFilters:
    def display():
        cols = st.columns(N_FILTER_COLUMNS)
        for i, attribute in enumerate(FILTER_DEFAULTS):
            with cols[i % N_FILTER_COLUMNS]:
                st.session_state.filter_ranges[attribute] = st.slider(**FILTER_DEFAULTS[attribute])  # "Tempo (BPM)", 80, 160, (115, 135))

    def transform_filters(filter_ranges: dict):
        filters = {}
        for attribute, range in filter_ranges.items():
            filters[f"min_{attribute}"] = range[0]
            filters[f"max_{attribute}"] = range[1]
        return filters
    

class RecommendationsPanel:
    def display():
        st.write("Recommendations")
        st.session_state.recommendation_track_selection = st.dataframe(
            st.session_state.recommendations,
            on_select="rerun",
            selection_mode="single-row",
        )
        with st.form(key='recc_track_chooser'):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                play_button = st.form_submit_button(label='▶️', on_click=RecommendationsPanel.play_button_selected)
            with col2:
                stop_button = st.form_submit_button(label='⏹️', on_click=st.session_state.spotify.stop)
            with col3:
                add_button = st.form_submit_button(label='➕ Add to playlist', on_click=RecommendationsPanel.add_track_to_playlist_button_selected)
            with col4:
                jump_button = st.form_submit_button(label='⏩️ Skip forward', on_click=st.session_state.spotify.get_current_play_details)                
        st.write("------")

    def fetch_recommendations():
        try:
            seed_track_ids = list(st.session_state['playlist'].iloc[st.session_state.track_seed_selection].index)
            st.session_state.recommendations = tabulate_reccs(
                st.session_state.spotify.get_recommendations(
                    seed_track_ids,
                    filters=RecommendationFilters.transform_filters(st.session_state.filter_ranges)
                )
            )
        except:
            st.write("ERROR FETCHING RECCS!!!")
            st.session_state.recommendations = pd.DataFrame()

    def play_button_selected():
        track_id = RecommendationsPanel.get_track_id_from_selection()
        if track_id:
            st.session_state.spotify.play_track(track_id)

    def add_track_to_playlist_button_selected():
        st.session_state.spotify.add_track_to_playlist()
        st.session_state.spotify.fetch_playlist()

    def get_track_id_from_selection():
        if st.session_state.recommendation_track_selection.get("selection").get("rows") != []: 
            selected_row = st.session_state.recommendation_track_selection["selection"]["rows"][0]
            track_id = st.session_state.recommendations.iloc[selected_row].name
            return track_id
        return None


class SpotifyInterface:
    def __init__(self):
        self.client = sign_in(st.session_state["cached_token"])
        # self.client = get_authorised_spotify(username, client_id, client_secret, redirect_uri)
    
    def play_track(self, track_id):
        try:
            self.client.start_playback(uris=[f'spotify:track:{track_id}'])
        except:
            st.write("ERROR: Failed to connect to Spotify device! Try going into Spotify and playing a track.")
    
    def stop(self):
        self.client.pause_playback()

    def get_recommendations(self, seed_tracks: list = None, filters = None):
        seed_tracks = seed_tracks or []
        filters = filters or {}
        return self.client.recommendations(
            seed_tracks=seed_tracks, 
            **filters,
            limit=20
        )

    def fetch_playlist(self):
        try:
            st.session_state.playlist = tabulate_playlist(
                self.client.user_playlist(
                    st.session_state.spotify_username, 
                    st.session_state.playlist_id
                )
            )
        except:
            st.write("Failed to get playlist. Check username and ID.")
            st.session_state.playlist = pd.DataFrame()

    def add_track_to_playlist(self):
        self.client.playlist_add_items(
            st.session_state.playlist_id, 
            [RecommendationsPanel.get_track_id_from_selection()]
        )

    def remove_tracks_from_playlist(self, track_ids: list):
        self.client.playlist_remove_all_occurrences_of_items(
            st.session_state.playlist_id, 
            list(track_ids)
        )

    def get_current_play_details(self):
        offset = 30000  # 30 secs
        current_pos = self.client.currently_playing()["progress_ms"]
        self.client.seek_track(current_pos + offset)


initialise()

PlaylistSelectorPanel.display()

RecommendationFilters.display()

PlaylistPanel.display()

RecommendationsPanel.display()
