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

	# query = "SELECT * FROM users WHERE email = %(eml)s;"
	# data = {
	# 	'eml': email
	# }
	# db = connectToMySQL('got_got')
	# result = db.query_db(query, data)
	# if len(result) > 0:
	# 	is_valid = False
	# 	flash('Email already exists Bla!', 'exist')

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
	db = connectToMySQL('got_got')
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



@app.route('/email', methods=['POST'])
def email():
	found = False
	db = connectToMySQL('got_got')
	query = "SELECT email FROM users WHERE users.email = %(email)s;"
	data ={'email': request.form['email']}
	result = db.query_db(query, data)
	if result:
		found = True
	return render_template('partials/email.html', found=found)



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
		db = connectToMySQL('got_got')
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
	db = connectToMySQL('got_got')
	user_query = '''
		 SELECT user_id, 
				first_name, 
				last_name, 
				email, 
				created_at, 
				updated_at 
		   FROM users 
		  WHERE user_id = %(fi)s;'''
	data = {
		"fi": session['user_id']
	}
	user = db.query_db(user_query, data)


	db = connectToMySQL('got_got')
	num_of_host_query = '''
					SELECT count(events.title) 
						AS my_host  
					  FROM events 
					 WHERE creater_id = %(user_id)s;'''
	data = {
		'user_id': session['user_id']
	}
	num_of_host = db.query_db(num_of_host_query, data)


	db = connectToMySQL('got_got')
	num_of_join_query = '''
					SELECT count(joins.join_user_id) AS my_join FROM joins WHERE join_user_id = %(user_id)s;'''
	data = {
		'user_id': session['user_id']
	}
	num_of_join = db.query_db(num_of_join_query, data)


	db = connectToMySQL('got_got')
	p_events_query = '''SELECT * FROM events WHERE creater_id = %(user_id)s;'''
	data = {
		'user_id': session['user_id']
	}
	p_events = db.query_db(p_events_query, data)

	return render_template('dashboard.html', user=user, p_events=p_events, num_of_host=num_of_host, num_of_join=num_of_join)



@app.route('/new_event') # NEW EVENT____________________________________________
def add_event():

	return render_template('new_event.html')


@app.route('/add_event', methods=['POST'])
def edit_user():
	add_event_query = '''INSERT INTO events (title, type_of_event, location, creater_id,
									 date_and_time, created_at, updated_at) 
							  VALUES (%(title)s, %(type_of_event)s, %(location)s, %(creater_id)s,
							  		 %(date_and_time)s, NOW(), NOW());'''
	data = {
		'title': request.form.get("title"),
		'type_of_event': request.form.get("genre"),
		'location': request.form.get("location"),
		'creater_id': session['user_id'],
		'date_and_time': request.form.get("date_and_time")
	}
	db = connectToMySQL('got_got')
	add_event = db.query_db(add_event_query, data)
	
	return redirect('/dashboard') #_____________________________________________




@app.route('/shows') # ALL SHOWS PAGE___________________________________________
def all_events():
	db = connectToMySQL('got_got')
	all_events_query = '''SELECT * FROM events'''
	all_events = db.query_db(all_events_query)

	return render_template('events.html', all_events=all_events) #______________




@app.route('/event/<event_id>') # SHOW EVENT INFO_______________________________
def event_info(event_id):
	db = connectToMySQL('got_got')
	event_info_query = '''SELECT * FROM events WHERE event_id = %(event_id)s'''
	data = {
		'event_id': event_id
	}
	event_info = db.query_db(event_info_query, data)

	if session['user_id'] == 'event_info[0][creater_id]':
		flash('JOIN!', 'button')
	else:
		flash('CANCEL!', 'button')

	return render_template('event_info.html', event_info=event_info) #__________




@app.route('/join/<event_id>') # JOIN TO EVENT OR CANCEL EVENT__________________
def join_to_event(event_id):
	if session['user_id'] != creater_id:
		join_query = '''INSERT INTO joins (join_user_id, join_event_id, created_at, updated_at) 
							 VALUES (%(j_user_id)s, %(j_event_id)s, NOW(), NOW());'''
		data = {
			'j_user_id': session['user_id'],
			'j_event_id': event_id
		}
		db = connectToMySQL('got_got')
		join = db.query_db(join_query, data)

		return redirect('/shows')
	else:
		cancel_query = '''DELETE FROM events WHERE event_id = %(event_id)s;'''
		data = {
			'event_id': event_id
		}
		db = connectToMySQL('got_got')
		cancel = db.query_db(cancel_query, data)

		return redirect('/shows')



@app.route('/edit_event/<event_id>') # UPDATE EVENT____________________________________________
def edit_event(event_id):
	db = connectToMySQL('got_got')
	event_info_query = '''SELECT * FROM events WHERE event_id = %(event_id)s'''
	data = {
		'event_id': event_id
	}
	event_info = db.query_db(event_info_query, data)

	return render_template('edit_event.html', event_info=event_info)

@app.route('/update_event/<event_id>', methods=['POST'])
def update_user(event_id):
	edit_event_query = '''UPDATE events SET (title, type_of_event, location, creater_id,
									 date_and_time, created_at, updated_at) 
							  VALUES (%(title)s, %(type_of_event)s, %(location)s, %(creater_id)s,
							  		 %(date_and_time)s, NOW(), NOW()) WHERE event_id = %(event_id)s;'''
	data = {
		'title': request.form.get("title"),
		'type_of_event': request.form.get("genre"),
		'location': request.form.get("location"),
		'creater_id': session['user_id'],
		'date_and_time': request.form.get("date_and_time"),
		'event_id': event_id
	}
	db = connectToMySQL('got_got')
	edit_event = db.query_db(edit_event_query, data)
	
	return redirect('/dashboard') #_____________________________________________



@app.route('/logout') #LOGOUT___________________________________________________
def logout_user():
	session.clear()
	return redirect('/')



if __name__=="__main__":
	app.run(debug=True)
