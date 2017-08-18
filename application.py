from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Ad

app = Flask(__name__)

# Connect to database and create database session
engine = create_engine('sqlite:///catelog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Route for the login page
# @app.route('/login')

# Route for the homepage
@app.route('/')
@app.route('/catelog')
def showAllCategories():
	categories = session.query(Category).order_by(asc(Category.name))
	return render_template('publichomepage.html', categories=categories)

# Route for the user homepage
@app.route('/catelog/<int:user_id>')
def showMyHomepage(user_id):
	user = session.query(User).filter_by(id=user_id)
	latest_ads = session.query(Ad).order_by(Ad.id).limit(3).all()
	categories = session.query(Category).order_by(asc(Category.name))
	return render_template('userhomepage.html', user=user, latest_ads=latest_ads,
	 categories=categories)

# Route for showCategory function
@app.route('/catelog/<string:category_name>')
def showCategory(category_name):
	ads = session.query(Ad).filter_by(category = 
		session.query(Category).filter_by(name = category_name).one()).all()
	return render_template('showads.html', category_name = category_name, ads = ads)

# Route for showMyAds function
@app.route('/catelog/<int:user_id>/ads')
def showMyAds(user_id):
	user = session.query(User).filter_by(id = user_id).one()
	ads = session.query(Ad).filter_by(user_id = user_id).all()
	return render_template('showmyads.html', user = user, ads = ads)

# Route for newAd function
@app.route('/catelog/<int:user_id>/new', methods=['GET', 'POST'])
def newAd(user_id):
	if request.method == 'POST':
		newAd = Ad(name = request.form['name'], description = 
			request.form['description'], price = request.form['price'],
			category = session.query(Category).filter_by(
				name = request.form['category']).one(), 
			user = session.query(User).filter_by(id = user_id).one())
		session.add(newAd)
		session.commit()
		return redirect(url_for('showAllCategories'))
	else: 
		return render_template('newad.html', user_id=user_id)

# Route for editAd function
@app.route('/catelog/<int:user_id>/<int:ad_id>/edit', methods = ['GET', 'POST'])
def editAd(user_id, ad_id):
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
		 ad=editedAd)

# Route for deleteAd function
@app.route('/catelog/<int:user_id>/<int:ad_id>/delete', methods =['GET', 'POST'])
def deleteAd(user_id, ad_id):
	adToDelete = session.query(Ad).filter_by(id=ad_id).one()
	if request.method == 'POST':
		session.delete(adToDelete)
		session.commit()
		return redirect(url_for('showMyAds', user_id=user_id))

	else:
		return render_template('deletead.html', user_id=user_id, ad_id=ad_id,
			ad=adToDelete)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)