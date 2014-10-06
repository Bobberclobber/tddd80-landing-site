FACEBOOK_APP_ID = '256159431223965'
FACEBOOK_APP_SECRET = '24f4c8f9fd37d043b7275388b0e5f702'

__author__ = 'josfa'

from flask import Flask, render_template
import facebook

app = Flask(__name__)
app.debug = True


def publish_custom_story(oauth_token):
    graph = facebook.GraphAPI(oauth_token)
    graph.put_object("me", "feed", message="Hello World!")
    return render_template("custom_story_test.html")
