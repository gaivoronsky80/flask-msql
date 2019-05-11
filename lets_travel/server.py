from flask import Flask, render_template, request, redirect, flash, session
from flask_bcrypt import Bcrypt

import re
from mysqlconnection import connectToMySQL

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'keep it secret, keep it safe'

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$')



def register_validation(first_name, last_name, email, password, confirm_password): # REGISTER VALIDATION
	is_valid = True
	if len(first_name) < 1:
		is_valid = False
		flash('First Name cannot be blank', 'fname_sms')
	if len(first_name) < 3:
		is_valid = False
		flash('First Name must be greater than 3 characters', 'fname_sms')
	if len(last_name) < 1:
		is_valid = False
		flash('Last Name cannot be blank', 'lname_sms')
	if len(last_name) < 3:
		is_valid = False
		flash('Last Name must be greater than 3 characters', 'lname_sms')
	if len(email) < 1:
		is_valid = False
		flash('Email cannot be blank', 'email_sms')
	if not EMAIL_REGEX.match(email):
		is_valid = False
		flash('Invalid email address', 'email_sms')

	query = "SELECT * FROM users WHERE email = %(eml)s;"
	data = {
		'eml': email
	}
	db = connectToMySQL('lets_travel')
	result = db.query_db(query, data)
	if len(result) > 0:
		is_valid = False
		flash('Email already exists!', 'exist')

	if len(password) < 1:
		is_valid = False
		flash('Password cannot be blank', 'password_sms')
	if len(password) < 8:
		is_valid = False
		flash('Password must be greater than 8 characters', 'password_sms')
	if len(password) > 20:
		is_valid = False
		flash('Password must be less than 20 characters', 'password_sms')
	if not PASSWORD_REGEX.match(password):
		flash('Password must contain at least one lowercase letter, one uppercase letter, and one digit', 'password_sms')
	if len(confirm_password) < 1:
		is_valid = False
		flash('Confirm Password cannot be blank', 'c_password_sms')
	if password != confirm_password:
		is_valid = False
		flash('Confirm password must be match to password', 'c_password_sms')
	if not is_valid:
		password = None
		confirm_password = None
		return False
	
	return is_valid #___________________________________________________________



def login_validation(email, password): # LOGIN VALIDATION_______________________
	is_valid = True
	if len(email) < 1:
		is_valid = False
		flash('Email cannot be blank', 'email_sms')
	if not EMAIL_REGEX.match(email):
		is_valid = False
		flash('Invalid email address!', 'email_sms')
	if len(password) < 1:
		is_valid = False
		flash('Password cannot be blank', 'password_sms')
	if len(password) < 8:
		is_valid = False
		flash('Password must be greater than 8 characters', 'password_sms')
	if not PASSWORD_REGEX.match(password):
		flash('Password must contain at least one lowercase letter, one uppercase letter, and one digit', 'password_sms')
	
	return is_valid #___________________________________________________________



def trip_validation(destination, start_date, end_date, plan): # TRIP VALIDATION___
	is_valid = True
	if len(destination) < 3:
		is_valid = False
		flash('A trip destination must consist of at least 3 characters', 'destination_sms')
	if len(plan) < 1:
		is_valid = False
		flash('A plan must be provided', 'plan_sms')
	if len(start_date) < 1:
		is_valid = False
		flash('Please select a start date', 'start_date_sms')
	if len(start_date) < 1:
		is_valid = False
		flash('Please select a end date', 'end_date_sms')
	
	return is_valid #___________________________________________________________



@app.route('/') # LOGIN_________________________________________________________
def login():

	return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_user():
	password = request.form['password']
	email = request.form['email']
	
	if not login_validation(email, password):
		return redirect('/')

	user_info = "SELECT * FROM users WHERE email = %(eml)s;"
	data = {
		'eml': email
	}
	db = connectToMySQL('lets_travel')
	result = db.query_db(user_info, data)
	
	if len(result) > 0:
		if bcrypt.check_password_hash(result[0]['password'], password):
			user_id = result[0]['user_id']
			set_session(user_id)
			return redirect('/dashboard')

	flash('You could not be logged in')
	return redirect('/')

def set_session(user_id):
	session['user_id'] = user_id #______________________________________________



@app.route('/') # REGISTER______________________________________________________
def new_user():

	return render_template('login.html')

@app.route('/add', methods=['POST'])
def add_new_user():
	first_name = request.form['first_name']
	last_name = request.form['last_name']
	email = request.form['email']
	password = request.form['password']
	confirm_password = request.form['confirm_password']

	if register_validation(first_name, last_name, email, password, confirm_password) != True:
		return redirect('/')
	else:
		pw_hash = bcrypt.generate_password_hash(request.form['password'])
		print(pw_hash)
		db = connectToMySQL('lets_travel')
		add_user = '''INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) 
						   VALUES (%(fn)s, %(ln)s, %(eml)s, %(pw_hash)s, NOW(), NOW());'''
		data = {
			"fn": request.form.get("first_name"),
			"ln": request.form.get("last_name"),
			"eml": request.form.get("email"),
			"pw_hash": pw_hash
		}
		new_user_id = db.query_db(add_user, data)
		set_session(new_user_id)

		return redirect('/dashboard') #_________________________________________



@app.route('/dashboard') # DASHBOARD PAGE_______________________________________
def dashboard():
	user_info_query = "SELECT * FROM users WHERE user_id = %(user_id)s;"
	data = {
		'user_id': session['user_id']
	}
	db = connectToMySQL('lets_travel')
	result = db.query_db(user_info_query, data)



	db = connectToMySQL('lets_travel')
	trips_query = '''
				SELECT * FROM trips 
						WHERE creater_id = %(user_id)s 
					 ORDER BY created_at DESC;'''
	data = {
		'user_id': session['user_id']
	}
	trips = db.query_db(trips_query, data)



	db = connectToMySQL('lets_travel')
	all_trips_query = '''
					SELECT * FROM trips 
							WHERE creater_id != %(user_id)s 
						 ORDER BY created_at DESC'''
	data = {
		'user_id': session['user_id']
	}
	all_trips = db.query_db(all_trips_query, data)

	return render_template('dashboard.html', trips=trips, result=result, all_trips=all_trips)



@app.route('/new_trip') # NEW TRIP____________________________________________
def add_trip():
	user_info_query = "SELECT * FROM users WHERE user_id = %(user_id)s;"
	data = {
		'user_id': session['user_id']
	}
	db = connectToMySQL('lets_travel')
	result = db.query_db(user_info_query, data)

	return render_template('new_trip.html', result=result)


@app.route('/add_trip', methods=['POST'])
def edit_user():
	destination = request.form['destination']
	start_date = request.form['start_date']
	end_date = request.form['end_date']
	plan = request.form['plan']

	if not trip_validation(destination, start_date, end_date, plan):
		return redirect('/new_trip')

	add_trip_query = '''
				INSERT INTO trips (destination, start_date, end_date, plan, 
							creater_id, created_at, updated_at) 
					 VALUES (%(destination)s, %(start_date)s, %(end_date)s, 
					 		%(plan)s, %(creater_id)s, NOW(), NOW());'''
	data = {
		'destination': request.form.get("destination"),
		'start_date': request.form.get("start_date"),
		'end_date': request.form.get("end_date"),
		'plan': request.form.get("plan"),
		'creater_id': session['user_id']
	}
	db = connectToMySQL('lets_travel')
	add_trip = db.query_db(add_trip_query, data)
	
	return redirect('/dashboard') #_____________________________________________




@app.route('/trip/<trip_id>') # SHOW TRIP INFO__________________________________
def event_info(trip_id):
	user_info_query = "SELECT * FROM users WHERE user_id = %(user_id)s;"
	data = {
		'user_id': session['user_id']
	}
	db = connectToMySQL('lets_travel')
	result = db.query_db(user_info_query, data)


	created_by_query = ''' 
				SELECT users.first_name, users.user_id, trips.creater_id 
				  FROM users 
			 LEFT JOIN trips 
			 		ON trips.creater_id = users.user_id 
			 	 WHERE trips.trip_id = %(trip_id)s;'''
	data = {
		'trip_id': trip_id
	}
	db = connectToMySQL('lets_travel')
	created_by = db.query_db(created_by_query, data)


	db = connectToMySQL('lets_travel')
	trip_info_query = '''SELECT * FROM trips WHERE trip_id = %(trip_id)s'''
	data = {
		'trip_id': trip_id
	}
	trip_info = db.query_db(trip_info_query, data)


	db = connectToMySQL('lets_travel')
	trips_users_query = '''
						SELECT users.first_name, users.user_id, trips.trip_id, 
							   trips_users.join_user_id, trips_users.join_trip_id, 
							   trips_users.trips_users_id 
						  FROM users 
					 LEFT JOIN trips 
					 		ON trips.creater_id = users.user_id
					 LEFT JOIN trips_users 
					 		ON trips_users.join_user_id = users.user_id 
					 	 WHERE trips_users.join_trip_id = %(trips_id)s;'''
	data = {
		'trips_id': trip_id
	}
	trips_users = db.query_db(trips_users_query, data)

	return render_template('trip_info.html', trip_info=trip_info, result=result, created_by=created_by, trips_users=trips_users) #_____________




@app.route('/join/<trip_id>') # JOIN TO TRIP__________________________________
def join_to_trip(trip_id):
	join_query = '''INSERT INTO trips_users (join_user_id, join_trip_id, created_at, updated_at) 
							  VALUES (%(join_user_id)s, %(join_trip_id)s, NOW(), NOW());'''
	data = {
		'join_user_id': session['user_id'],
		'join_trip_id': trip_id
	}
	db = connectToMySQL('lets_travel')
	join = db.query_db(join_query, data)

	return redirect('/dashboard') #_____________________________________________



@app.route('/cancel/<trip_id>') # CANCEL TRIP_________________________________
def cancel_event(trip_id):
	cancel_query = '''DELETE FROM trips WHERE trip_id = %(trip_id)s;'''
	data = {
		'trip_id': trip_id
	}
	db = connectToMySQL('lets_travel')
	cancel = db.query_db(cancel_query, data)

	return redirect('/dashboard') #_________________________________________________



@app.route('/edit_trip/<trip_id>') # UPDATE TRIP____________________________________________
def edit_event(trip_id):
	user_info_query = "SELECT * FROM users WHERE user_id = %(user_id)s;"
	data = {
		'user_id': session['user_id']
	}
	db = connectToMySQL('lets_travel')
	result = db.query_db(user_info_query, data)

	db = connectToMySQL('lets_travel')
	trip_info_query = '''SELECT * FROM trips WHERE trip_id = %(trip_id)s'''
	data = {
		'trip_id': trip_id
	}
	trip_info = db.query_db(trip_info_query, data)

	return render_template('edit_trip.html', trip_info=trip_info, result=result)

@app.route('/update_trip/<trip_id>', methods=['POST'])
def update_user(trip_id):
	destination = request.form['destination']
	start_date = request.form['start_date']
	end_date = request.form['end_date']
	plan = request.form['plan']

	if not trip_validation(destination, start_date, end_date, plan):
		return redirect('/edit_trip/' + trip_id)

	edit_trip_query = '''
				UPDATE trips 
				   SET (destination, start_date, end_date, plan, creater_id, created_at, updated_at) 
				VALUES (%(destination)s, %(start_date)s, %(end_date)s, %(plan)s, %(creater_id)s, NOW(), NOW()) 
				 WHERE trip_id = %(trip_id)s;'''
	data = {
			'destination': request.form.get("destination"),
			'start_date': request.form.get("start_date"),
			'end_date': request.form.get("end_date"),
			'plan': request.form.get("plan"),
			'creater_id': session['user_id'],
			'trip_id': trip_id
	}
	db = connectToMySQL('lets_travel')
	edit_trip = db.query_db(edit_trip_query, data)
	
	return redirect('/dashboard') #_____________________________________________



@app.route('/logout') #LOGOUT___________________________________________________
def logout_user():
	session.clear()
	return redirect('/')



if __name__=="__main__":
	app.run(debug=True)
