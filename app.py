from flask import Flask, render_template, url_for, request,redirect, Response, jsonify
import cv2
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode

from functools import wraps
import json
from os import environ as env
from werkzeug.exceptions import HTTPException

url = "http://73.85.164.101:8081/video.mjpg"
staticUrl = "https://dl.dropboxusercontent.com/s/a1qo1e2fsyuxnji/static-video.mp4?dl=0"
target = ''
app = Flask(__name__)

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id='XBSoL35oZ0ZJyMxbDXLZxUIcPReufQox',
    client_secret='dfovJUIbPTsdI4j00X-G3xmIGQmntUbRb8ZZpKTFbvoNqqlALBRlERhFXncec3yg',
    api_base_url='https://dev-gr3qe9to.auth0.com',
    access_token_url='https://dev-gr3qe9to.auth0.com/oauth/token',
    authorize_url='https://dev-gr3qe9to.auth0.com/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)


@app.route('/callback')
def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect('/dashboard')
@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri='https://powerful-badlands-71674.herokuapp.com/home')
@app.route('/logout')
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {'returnTo': url_for('home', _external=True), 'client_id': 'XBSoL35oZ0ZJyMxbDXLZxUIcPReufQox'}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))
def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    if 'profile' not in session:
      # Redirect to Login page here
      return redirect('/')
    return f(*args, **kwargs)

  return decorated


@app.route('/home', methods=['POST', 'GET'])
@requires_auth
def home():
    return render_template('home.html')
def gen_live(target):
    cam = cv2.VideoCapture(target)
    print('Attempting to open URL')
    if not cam.isOpened():
        raise RuntimeError('Could Not Connect to Cam')
    while True:
        result,frame = cam.read()
        if not result:
            print('Cry')
        frame_enc = cv2.imencode('.jpeg', frame)[1].tobytes()
        yield (b'--frame\r\n'
                     b'Content-Type: image/jpeg\r\n\r\n' + frame_enc + b'\r\n')
@app.route('/video_feed')
def video_feed():
    return Response(gen_live(target), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/static', methods=['POST'])
def static_stream():
    global target
    target = staticUrl
    return render_template('base.html', streamtype = "Static Stream")
@app.route('/livestream', methods=['POST'])
def live_stream():
    global target
    target = url
    return render_template('base.html', streamtype ="Livestream")
if __name__ == '__main__':
    app.run()