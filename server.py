import json
from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, session, url_for
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
app = Flask(__name__)
oauth = OAuth(app)
auth0 = oauth.register(
    'auth0',
    client_id='pOSo8bL1n6nNROIU6SekQWy0MWygTOTN',
    client_secret='FheIT4CilBrHWQ0IH44PNq6v_MwkSujM1t2VbnsaznckCWbDctq468w3ibZPWDvV',
    api_base_url='https://dev-gr3qe9to.auth0.com',
    access_token_url='https://dev-gr3qe9to.auth0.com/oauth/token',
    authorize_url='https://dev-gr3qe9to.auth0.com/authorize',
    client_kwargs={
        'scope': 'openid profile email'
    }
)
app.secret_key = 'Doodie'
app.debug = True
@app.route('/callback')
def callback_handler():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect('/dashboard')

@app.route('/login', methods = ['POST', 'GET'])
def login():
    return auth0.authorize_redirect(redirect_uri = 'http://localhost:5000/callback')

@app.route('/logout')
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {'returnTo': url_for('home', _external=True), 'client_id': 'pOSo8bL1n6nNROIU6SekQWy0MWygTOTN'}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    if 'profile' not in session:
      # Redirect to Login page here
      return redirect('/')
    return f(*args, **kwargs)

  return decorated
@app.route('/', methods =['POST', 'GET'])
def index():
    return render_template('home.html')
@app.route('/dashboard')
@requires_auth
def dashboard():
    return render_template('dashboard.html',
                           userinfo=session['profile'],
                           userinfo_pretty=json.dumps(session['jwt_payload'], indent=4))

if __name__ == '__main__':
    app.run()
