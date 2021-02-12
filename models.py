# To make the tables in the "test" database
# open a python interactive shell and type:
# >>> from models import db
# >>> db.create_all()

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

workcontracts = db.Table(
	'workcontracts',
	db.Column('wc_id', db.Integer, primary_key=True),
	db.Column('access_level',db.Integer), #2=admin,1=user-rw, 0=user-r
	
	db.Column('user_id', db.Integer, db.ForeignKey('users.user_id',onupdate="CASCADE", ondelete="CASCADE")),
	db.Column('org_id', db.Integer, db.ForeignKey('organizations.org_id',onupdate="CASCADE", ondelete="CASCADE"))
)

class User(db.Model):
	__tablename__= 'users'
	user_id = db.Column(db.Integer, primary_key=True)
	public_id = db.Column(db.String)
	username = db.Column(db.String)
	password = db.Column(db.String)
	is_admin = db.Column(db.Boolean)

	# -     first association/relationship: "users" with "Organization"
	# since it is a many-to-many, we need a "secondary relationship":
	# - secondary association/relationship: "users" with "workcontracts"
	# - backref is like a field that will be added to "organizations"
	# so I could do Organization.workers and will get all the workers
	# - lazy will give the option to make a custom query (filtering)
	# instead of giving all the data at once
	contracts = db.relationship(
									'Organization',
									secondary='workcontracts',
									backref=db.backref(
														'workers',
														lazy='dynamic',
														),
									cascade="all, delete"
								)

class Organization(db.Model):
	__tablename__ = 'organizations'
	org_id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	
	units = db.relationship("Unit")
"""	workers = db.relationship(
								'User',
								secondary='workcontracts',
								backref=db.backref(
										'contracts',
										lazy='dynamic'
									),
								cascade="all, delete"
							 )
"""
class Unit(db.Model):
	__tablename__ = 'units'
	unit_id = db.Column(db.Integer, primary_key=True)
	used_boxes = db.Column(db.Integer)
	max_boxes = db.Column(db.Integer)
	access_level = db.Column(db.Integer)
	
	org_id = db.Column(db.Integer, db.ForeignKey('organizations.org_id'))

	boxes = db.relationship("Box")

class Box(db.Model):
	__tablename__ = 'boxes'
	box_id = db.Column(db.Integer, primary_key=True)
	description = db.Column(db.String)
	access_level = db.Column(db.Integer)

	unit_id = db.Column(db.Integer, db.ForeignKey('units.unit_id') )
