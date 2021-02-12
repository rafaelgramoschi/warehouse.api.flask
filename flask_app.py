"""
# REQUIREMENTS
pip3 install Flask
pip3 install Flask-SQLAlchemy
pip3 install psycopg2 # postgresql connector
pip3 install Flask-Migrate # used to migrate database
pip3 install Flask-Script # used to write commands & configs & scripts

superuser manages all items (units, boxes, users)
warehouse:
	
	unit (org_id):
		- users
		- boxes (set limit)

	unit (org_id):
		- users
		- boxes (set limit)
"""
import read_my_file
import uuid
import jwt # used for making tokens
import datetime
from flask import Flask
from flask import jsonify
from flask import request
from flask import make_response
from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy import or_
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from models import db
from models import User
from models import Organization
from models import Unit
from models import Box
from models import workcontracts
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = \
					read_my_file.read_first_line("secret_key.txt")
app.config["SQLALCHEMY_DATABASE_URI"] = \
					read_my_file.read_first_line("psql.uri")
db.init_app(app)

@app.route("/")
def home():
	return '<p><a href="/warehouse">Admin Panel</a> \
			or <a href="/signup">Sign Up</a> \
			or <a href="/login">Log In</a></p>'

def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = None

		# header
		if 'x-access-token' in request.headers:
			token = request.headers['x-access-token']

		if not token:
			return jsonify({'error':'token is missing.'}), 401

		try:
			data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
			current_user = User.query.filter_by(public_id=data['public_id']).first()

		except:
			return jsonify({'msg':'token is invalid'}), 401

		return f(current_user, *args, **kwargs)
	
	return decorated


@app.route("/login", methods=['GET'])
def login():
	auth = request.authorization
	print("\n\nauth=\n{}\n\n".format(auth))
	if not auth or not auth.username or not auth.password:
		return make_response("Can't verify creds.", 401, {"WWW-Authenticate": "Basic realm='Login required!'"})

	user = User.query.filter_by(username=auth.username).first()

	if user:
		if check_password_hash(user.password, auth.password):
			token = jwt.encode({'public_id': user.public_id,'exp': datetime.datetime.utcnow()+datetime.timedelta(minutes=30)},app.config['SECRET_KEY'],algorithm="HS256")
			
			return jsonify({'token':token}) #.decode('UTF-8')

	return make_response("Can't verify user.", 401, {"WWW-Authenticate": "Basic realm='Login required!'"})


@app.route("/warehouse", methods=['GET'])
@token_required
def admin_panel(current_user):
	"""Superuser access level required (access_level==2)"""
	if current_user.is_admin:
		html = ""
		
		list_of_units = info_all_units().get_json()
		
		for unit in list_of_units:
			html += "<ul id='unit'>"
			html += "<li>{} ({})".format(unit['unit_id'], unit['org_name'])
			html += "<ul>"
			html += "<li>Used {}/{}</li>".format(unit['used'],unit['max'])
			html += "<li>{}</li>".format(unit['employees'])
			html += "</ul></li></ul>"

		return html
	else:
		return jsonify({"msg":"You are not admin."})


@app.route("/units", methods=['GET'])
@token_required
def info_all_units(current_user):

	units = Unit.query.all()

	output = []
	
	for unit in units:
		single_unit_data = {}
		
		single_unit_data["unit_id"] = unit.unit_id
		single_unit_data["used"] = unit.used_boxes
		single_unit_data["max"] = unit.max_boxes
		single_unit_data["employees"] = []
		org = Organization.query.filter_by(org_id=unit.org_id).first()
		single_unit_data["org_name"] = org.name
		
		for user in org.workers:
			single_unit_data["employees"].append(user.public_id)
		
		output.append(single_unit_data)
	
	return jsonify(output)


@app.route("/user/<public_id>/units", methods=['GET'])
@token_required
def user_units(current_user,public_id):
	"""Returns the list of accessible Units for the given User."""
	if current_user.public_id==public_id or current_user.is_admin:
		user_id = User.query.filter_by(public_id=public_id).first().user_id
		user_contracts = db.session.query(workcontracts).filter_by(user_id=user_id).all()

		if not user_contracts:
			return jsonify({'msg':'no access found.'})

		output = []
		for contract in user_contracts:
			organization = Organization.query.filter_by(org_id=contract.org_id).first()
			for unit in organization.units:
				if unit.access_level <= contract.access_level:
					output.append({
									#"contract_id": contract.wc_id,
									"org_id" : contract.org_id,
									"user_id": contract.user_id,
									"unit_id": unit.unit_id,
									"unit_access_level": unit.access_level,
									"user_access_level": contract.access_level
								  })

		return jsonify(output)
	
	return jsonify("You are not authorized."),401


@app.route("/user/<public_id>/boxes", methods=['GET'])
@token_required
def user_boxes(current_user,public_id):
	"""Returns the list of accessible Boxes for the given User."""
	if current_user.public_id==public_id or current_user.is_admin:
		user_id = User.query.filter_by(public_id=public_id).first().user_id
		user_contracts = db.session.query(workcontracts).filter_by(user_id=user_id).all()

		if not user_contracts:
			return jsonify({'msg':'no access found.'})

		output = []
		for contract in user_contracts:
			organization = Organization.query.filter_by(org_id=contract.org_id).first()
			for unit in organization.units:
				for box in unit.boxes:
					if box.access_level <= contract.access_level:
						output.append({
									#"contract_id": contract.wc_id,
									"org_id" : contract.org_id,
									"user_id": contract.user_id,
									"unit_id": unit.unit_id,
									"box_id": box.box_id,
									"box_access_level": unit.access_level,
									"user_access_level": contract.access_level
								  })

		return jsonify(output)
	
	return jsonify("You are not authorized."),401


# WAREHOUSE SUPERUSER ONLY
@app.route("/signup/organization", methods=['POST'])
@token_required
def signup_org(current_user):
	"""Signup a new user."""
	
	"""
	The request must have the application/json content type,
	or use request.get_json(force=True) to ignore the content type.
	in curl, use the header: -H "Content-Type: application/json"
	"""
	if current_user.is_admin:
		data = request.get_json(force=True)

		org_name_to_add = data['org_name']
		
		org_already_exists = Organization.query.filter((Organization.name==org_name_to_add)).first()
		if org_already_exists:
			return jsonify({'error':'Organization name already exists'})
		
		new_org = Organization(name=org_name_to_add)
			
		db.session.add(new_org)
		db.session.commit()

		return jsonify({'msg':'user successfully added.'})
	
	return jsonify({'error':'no user added: you don\'t have administrative authorization.'})


# WAREHOUSE SUPERUSER ONLY
@app.route("/newunit", methods=['POST'])
@token_required
def new_unit(current_user):
	"""Make a new Unit and set its owner to be a given Organization."""
	if current_user.is_admin:
		data = request.get_json(force=True)

		org_id = data['org_id']
		max_boxes = data['max_boxes']
		access_level = data['unit_access_level']

		organization_exists = Organization.query.filter_by(org_id=org_id).first()

		if not organization_exists:
			return jsonify({'error':'No organization with such ID.'})

		new_unit = Unit(
			org_id=org_id,
			used_boxes=0,
			max_boxes=max_boxes,
			access_level=access_level
		)

		db.session.add(new_unit)
		db.session.commit()
		return jsonify({'msg':'Unit successfully assigned.'})
	
	return jsonify({'error':'No unit assigned: you don\'t have administrative authorization.'})


# WAREHOUSE SUPERUSER ONLY
@app.route("/signup/user", methods=['POST'])
@token_required
def signup_user(current_user):
	"""Signup a new user."""
	
	"""
	The request must have the application/json content type,
	or use request.get_json(force=True) to ignore the content type.
	in curl, use the header: -H "Content-Type: application/json"
	"""
	if current_user.is_admin:
		data = request.get_json(force=True)

		username_to_add = data['username']
		password = data['password']
		org_id = data['org_id']
		user_access_level = data['user_access_level']

		username_already_exists = User.query.filter((User.username==username_to_add)).first()
		if username_already_exists:
			workcontract_already_exists = workcontracts.query.filter_by(user_id=username_already_exists.user_id,org_id=org_id).first()
			if workcontract_already_exists:	
				return jsonify({'error':'username in selected organization already exists'})
			else:
				add_work_contract = workcontracts.insert().values(org_id=org_id, user_id=username_already_exists.user_id, access_level=user_access_level)
		else:
			hashed_password = generate_password_hash(str(password), method='sha256')

			new_user = User(
							public_id=str( uuid.uuid4() ),
							username=username_to_add,
							password=hashed_password,
						)
			add_work_contract = workcontracts.insert().values(org_id=org_id, user_id=new_user.user_id, access_level=user_access_level)

		db.session.add(new_user)
		db.session.commit()

		db.session.execute(add_work_contract)
		db.session.commit()

		return jsonify({'msg':'user successfully added.'})
	
	return jsonify({'error':'no user added: you don\'t have administrative authorization.'})


@app.route("/unit/<unit_id>/box", methods=['POST'])
@token_required
def add_box(current_user,unit_id):
	"""Adds a Box to a given Unit if there's space."""
	unit = Unit.query.filter_by(unit_id=unit_id).first()
	if not unit:
		return jsonify({'msg':'No unit found.'})

	org_id = unit.org_id
	
	if not current_user.is_admin:
		current_user_level_in_org = db.session.query(workcontracts).filter(
							(workcontracts.c.user_id==current_user.user_id)
							&(workcontracts.c.org_id==org_id)).first().access_level
	
	if current_user_level_in_org>=1: #superuser or rw permissions
		data = request.get_json(force=True)
		description = data['description']
		box_access_level = data['box_access_level']

		if unit.used_boxes >= unit.max_boxes:
			return jsonify({'msg':'Max number of boxes reached, no more space!'})

		new_box = Box(
					unit_id=unit.unit_id,
					description=description,
					access_level=box_access_level
					)

		unit.used_boxes += 1
		db.session.add(new_box)
		db.session.commit()
		del new_box # release the object
		return jsonify({'msg':'Box successfully added to Unit.'})

	return jsonify({'msg':'error: something went wrong with user authorization'})

@app.route("/unit/<unit_id>/box/<box_id>", methods=['DELETE'])
@token_required
def delete_box(current_user,unit_id,box_id):
	"""Deletes a Box from the given Unit.
	Superuser/User Permission required.
	"""
	unit = Unit.query.filter_by(unit_id=unit_id).first()
	if not unit:
		return jsonify({'msg':'No unit found.'})

	org_id = unit.org_id

	box = db.session.query(Box).filter_by(box_id=box_id)
	if box.first():
		if not current_user.is_admin:
			current_user_level_in_org = db.session.query(workcontracts).filter(
								(workcontracts.c.user_id==current_user.user_id)
								&(workcontracts.c.org_id==org_id)).first().access_level
		
		if current_user_level_in_org>=1 or current_user.is_admin: #superuser or rw permissions
			box = box.delete()
			if box == 1:
				db.session.query(Unit).filter_by(unit_id=box.first().unit_id).first().used_boxes -= 1
				db.session.commit()
				return jsonify({'msg':'box successfully deleted.'})
			else:
				return jsonify({'msg':'nothing deleted: no box with such ID.'})

	return jsonify({'error':'Not authorized.'})

@app.route("/organization/<org_id>/user/<public_id>", methods=['DELETE'])
@token_required
def delete_user(current_user,org_id,public_id):
	"""Deletes a User from the given Organization.
	Superuser/User Permission required.
	"""
	user = User.query.filter_by(public_id=public_id)
	wtd = user.delete()
	print("\nwtd: {}\n\n".format(wtd) )
	
	if wtd==1:
		db.session.commit()
		return jsonify({'msg':'user successfully deleted from organization.'})
	else:
		return jsonify({'msg':'nothing deleted: no user with such ID in the specified organization.'})


if __name__ == "__main__":
	app.debug = True
	# localhost only
	app.run(host="localhost", port="5000")
	# open ports
	#app.run(host="0.0.0.0", port="5000")