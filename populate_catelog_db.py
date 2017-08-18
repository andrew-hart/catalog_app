from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Ad

engine = create_engine('sqlite:///catelog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create the categories
art = Category(name = "Art and Collectables")
session.add(art)
session.commit()

clothes = Category(name = "Clothes")
session.add(clothes)
session.commit()

electronics = Category(name= "Electronics")
session.add(electronics)
session.commit()

furnature = Category(name= "Furnature")
session.add(furnature)
session.commit()

jewellery = Category(name= "Jewellery and Watches")
session.add(jewellery)
session.commit()

sports = Category(name = "Sports")
session.add(sports)
session.commit()

tools = Category(name = "Tools")
session.add(sports)
session.commit()

toys = Category(name = "Toys and Games")
session.add(sports)
session.commit()

# Create users
Andrew = User(name = "Andrew", email = "andrew@gmail.com")
session.add(Andrew)
session.commit()

#Create Ad's
ad_1 = Ad(name = "Hockey Stick", 
	description = "This hockey stick was used by Sidney Crosby",
	price = "$100", category = sports, user = Andrew)
session.add(ad_1)
session.commit()


# Print the contents of the database
items = session.query(Category).all()
for item in items:
	print item.name
	print item.id
	print ""
	#session.delete(item)
	#session.commit()

users = session.query(User).all()
for user in users:
	print user.name
	print user.id
	print ""
	#session.delete(user)
	#session.commit()

ads = session.query(Ad).all()
for ad in ads:
	print ad.name
	print ad.id
	print ad.description
	print ad.price
	print ad.category
	print ad.user
	print ""
	#session.delete(ad)
	#session.commit()
