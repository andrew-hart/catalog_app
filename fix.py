from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Ad

engine = create_engine('sqlite:///catelog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

categories = session.query(Category).order_by(Category.name.asc())

for c in categories:
	session.delete(c)

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
session.add(tools)
session.commit()

toys = Category(name = "Toys and Games")
session.add(toys)
session.commit()

categories = session.query(Category).order_by(Category.name.asc())

for c in categories:
	print c.name