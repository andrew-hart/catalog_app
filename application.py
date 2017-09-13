#!/#!/usr/bin/env python
import random
import string
import httplib2
import json
from flask import make_response
import requests
from flask import Flask, render_template, request
from flask import redirect, url_for, jsonify, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Ad
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

app = Flask(__name__)

#  client ID
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "cat-e-log"

# Connect to database and create database session
engine = create_engine('sqlite:///catelog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# API Endpoints for an arbitrary ad
@app.route('/catelog/<int:ad_id>/ad/JSON')
def adJSON(ad_id):
    ad = session.query(Ad).filter_by(id=ad_id).one()
    return jsonify(ad=ad.serialize)


# Route for the login page
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Route for gconnect
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                                 'Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Check to see if the user exists, if they don't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h3>Welcome, '
    output += login_session['username']

    return output


# Route for gdisconnect
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
                                 'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        print 'Logout successful'
        return redirect('/catelog')
    else:
        response = make_response(json.dumps(
                                 'Failed to revoke token for given user.',
                                 400))
        response.headers['Content-Type'] = 'application/json'
        print 'Logout failed'
        return redirect('/catelog')


# Route for the homepage
@app.route('/')
@app.route('/catelog')
def showAllCategories():
    categories = session.query(Category).order_by(asc(Category.name))
    latest_ads = session.query(Ad).order_by(Ad.id.desc()).limit(3)
    return render_template('publichomepage.html', categories=categories,
                           latest_ads=latest_ads)


# Route for the user homepage
@app.route('/catelog/user')
def showMyHomepage():
    if 'username' not in login_session:
        return redirect('/login')
    user = session.query(User).filter_by(id=login_session['user_id']).one()
    latest_ads = session.query(Ad).order_by(Ad.id.desc()).limit(3)
    categories = session.query(Category).order_by(asc(Category.name))
    return render_template('userhomepage.html', user=user,
                           categories=categories, latest_ads=latest_ads)


# Route for the user profile
@app.route('/catelog/profile/<int:user_id>')
def showMyProfile(user_id):
    if 'username' not in login_session:
        return redirect('/login')
    user = getUserInfo(user_id)
    return render_template('userprofile.html', user=user)


# Route for showCategory function
@app.route('/catelog/<string:category_name>')
def showCategory(category_name):
    ads = session.query(Ad).filter_by(category=session.query(
        Category).filter_by(name=category_name).one()
        ).order_by(Ad.id.desc()).all()
    if 'username' not in login_session:
        return render_template('showcategory.html',
                               category_name=category_name, ads=ads)
                               
    else:
        user = getUserInfo(login_session['user_id'])
        return render_template('usershowcategory.html',
                               category_name=category_name,
                               ads=ads, user=user)


# Route for showMyAds function
@app.route('/catelog/<int:user_id>/ads')
@login_required
def showMyAds(user_id):
    # Make sure the user is authorized
    if login_session['user_id'] != user_id:
        return redirect('/catelog')
    user = session.query(User).filter_by(id=user_id).one()
    ads = session.query(Ad).filter_by(user_id=user_id).order_by(
                                      Ad.id.desc()).all()
    return render_template('showmyads.html', user=user, ads=ads)


# Route for newAd function
@app.route('/catelog/<int:user_id>/new', methods=['GET', 'POST'])
@login_required
def newAd(user_id):
    # Make sure the user is authorized
    if login_session['user_id'] != user_id:
        return redirect('/catelog')
    user = getUserInfo(user_id)
    ads = session.query(Ad).filter_by(user_id=user_id).order_by(
                                      Ad.id.desc()).all()
    categories = session.query(Category).order_by(asc(Category.name))
    if request.method == 'POST':
        newAd = Ad(name=request.form['name'],
                   description=request.form['description'],
                   price=request.form['price'],
                   category=session.query(Category).filter_by(
                   name=request.form['category']).one(),
                   user=session.query(User).filter_by(id=user_id).one())
        session.add(newAd)
        session.commit()
        ads = session.query(Ad).filter_by(
                                           user_id=user_id).order_by(
                                           Ad.id.desc()).all()
        return render_template('showmyads.html', user=user, ads=ads)
    else:
        return render_template('newad.html', user_id=user_id, user=user,
                               categories=categories)


# Route for editAd function
@app.route('/catelog/<int:user_id>/<int:ad_id>/edit', methods=['GET', 'POST'])
@login_required
def editAd(user_id, ad_id):
    # Make sure the user is authorized
    if login_session['user_id'] != user_id:
        return redirect('/catelog')
    user = getUserInfo(user_id)
    categories = session.query(Category).order_by(asc(Category.name))
    editedAd = session.query(Ad).filter_by(id=ad_id).one()
    if request.method == 'POST':
        # Update ad name
        if request.form['name']:
            editedAd.name = request.form['name']
        # Update ad category
        if request.form['category']:
            editedAd.category.name = request.form['category']
        # Update ad price
        if request.form['price']:
            editedAd.price = request.form['price']
        # Update ad description
        if request.form['description']:
            editedAd.description = request.form['description']
        session.add(editedAd)
        session.commit()
        return redirect(url_for('showMyAds', user_id=user_id))
        
    else:
        return render_template('editad.html', user_id=user_id, ad_id=ad_id,
                               ad=editedAd, user=user, categories=categories)


# Route for deleteAd function
@app.route('/catelog/<int:user_id>/<int:ad_id>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteAd(user_id, ad_id):
    # Make sure the user is the owner first
    if login_session['user_id'] != user_id:
        return redirect('/catelog')
        user = getUserInfo(user_id)
        adToDelete = session.query(Ad).filter_by(id=ad_id).one()
    if request.method == 'POST':
        session.delete(adToDelete)
        session.commit()
        return redirect(url_for('showMyAds', user_id=user_id))
    else:
        return render_template('deletead.html', user_id=user_id,
                               ad_id=ad_id, ad=adToDelete, user=user)


# Function decorator to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            return redirect('/login')
    return decorated_function


# Function to create a new user
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    print 'User created'
    return user.id


# Function to get a user object
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# Function to get a user id
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
