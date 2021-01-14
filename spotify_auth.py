from secrets import randbelow
from flask import request, session
from urllib.parse import quote
import os
import requests
import base64
import time

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

state_key = "spotify_auth_state"
scope = "playlist-modify-public playlist-modify-private"

def setupLogin(client_id, client_secret, redirect_uri):
    def generateRandomString(length):
        possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        return ''.join([possible[randbelow(len(possible))] for _ in range(length)])

    state = generateRandomString(16)
    session[state_key] = state

    auth_query_params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": scope,
        "redirect_uri": redirect_uri,
        "state": state,
        "response_type": "code"
    }
    params_string = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_params.items()])
    url = SPOTIFY_AUTH_URL + "/?" + params_string
    return url


def getTokens(client_id, client_secret, redirect_uri):
    code = None if ('code' not in request.args) else request.args['code']
    state = None if ('state' not in request.args) else request.args['state']
    stored_state = None if (state_key not in session) else session[state_key]

    if(state == None or state != stored_state):
        return 'State mismatch'
    else:
        session.pop(state_key)
        body = {
            "grant_type": "authorization_code",
            "code": str(code),
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret
        }
        post_resp = requests.post(SPOTIFY_TOKEN_URL, data=body)
        if post_resp.status_code == 200:
            resp_json = post_resp.json()
            session['access_token'] = resp_json['access_token']
            session['refresh_token'] = resp_json['refresh_token']
            session['token_expire'] = resp_json['expires_in'] + time.time()
            return 'access token gotten'
        else:
            print('oops')
            return '500'


# needs testing
def checkToken(client_id, client_secret):
    if time.time() >= session['token_expiration']:
        refresh_tok = session['refresh_token']
        body = {
            "grant_type": "authorization_code",
            "refresh_token": refresh_tok,
            "client_id": client_id,
            "client_secret": client_secret
        }
        post_resp = requests.post(SPOTIFY_TOKEN_URL, data=body)
        if post_resp.status_code == 200:
            resp_json = post_resp.json()
            session['access_token'] = resp_json['access_token']
            session['token_expire'] = resp_json['expires_in'] + time.time()
            return "Success"
    return None