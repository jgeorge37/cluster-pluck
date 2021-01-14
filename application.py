from flask import Flask, render_template, redirect, request, session
import spotify_auth

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config.from_object('config')

# Spotify URLS
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

state_key = "spotify_auth_state"
client_id = app.config['CLIENT_ID']
client_secret = app.config['CLIENT_SECRET']
redirect_uri = app.config['REDIRECT_URI']
scope = "playlist-modify-public playlist-modify-private"


@app.route('/')
def index():
    return render_template('application.html', message='hello jing')

@app.route('/login')
def login():
    url = spotify_auth.setupLogin(client_id, client_secret, redirect_uri)
    return redirect(url)

@app.route('/callback')
def callback():
    message = spotify_auth.getTokens(client_id, client_secret, redirect_uri)
    return render_template('application.html', message=session['access_token'])
