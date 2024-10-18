from collections import OrderedDict

TARGET_PLAYLIST_URI = '6PMDU7e878EQuN4AA4GOag'
N_FILTER_COLUMNS = 4

# This sets which filters are present and their order
FILTERS = [
    "tempo",
    "key",
    "mode",
    "acousticness",
    "danceability",
    "energy",
    "instrumentalness",
    "liveness",
    "loudness",
    "speechiness",
    "valence",
]

# Initial settings for filters. 
# min_value and max_value are the extreme ends of the sliders.
# value is range specifying the initial selected range.
FILTER_SETTINGS = {
    "tempo": {
        "label": "Tempo (BPM)",
        "min_value": 80,
        "max_value": 160,
        "value": (80, 160),
    },
    "key": {
        "label": "Key (0 = C)",
        "min_value": 0,
        "max_value": 11,
        "value": (0, 11),
    },
    "mode": {
        "label": "Mode (1 = Major)",
        "min_value": 0,
        "max_value": 1,
        "value": (0, 1),
    },
    "acousticness": {
        "label": "Acousticness",
        "min_value": 0.,
        "max_value": 1.,
        "value": (0., 1.),
        "step": 0.05,
    },
    "danceability": {
        "label": "Danceability",
        "min_value": 0.,
        "max_value": 1.,
        "value": (0., 1.),
        "step": 0.05,
    },
    "energy": {
        "label": "Energy",
        "min_value": 0.,
        "max_value": 1.,
        "value": (0., 1.),
        "step": 0.05,
    },
    "instrumentalness": {
        "label": "Instrumentalness",
        "min_value": 0.,
        "max_value": 1.,
        "value": (0., 1.),
        "step": 0.05,
    },
    "liveness": {
        "label": "Liveness",
        "min_value": 0.,
        "max_value": 1.,
        "value": (0., 1.),
        "step": 0.05,
    },
    "loudness": {
        "label": "Loudness (dB)",
        "min_value": -60,
        "max_value": 0,
        "value": (-60, 0),
    },
    "speechiness": {
        "label": "Speechiness",
        "min_value": 0.,
        "max_value": 1.,
        "value": (0., 1.),
        "step": 0.05,
    },
    "valence": {
        "label": "Valence",
        "min_value": 0.,
        "max_value": 1.,
        "value": (0., 1.),
        "step": 0.05,
    },
}
FILTER_DEFAULTS = OrderedDict(
    ((filter, FILTER_SETTINGS[filter]) for filter in FILTERS)
)

