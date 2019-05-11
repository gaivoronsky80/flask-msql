from flask import Flask, render_template, request, redirect, flash, session
from flask_bcrypt import Bcrypt

import re
from mysqlconnection import connectToMySQL

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'keep it secret, keep it safe'

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$')



def register_validation(first_name, last_name, email, password, confirm_password): #REGISTER VALIDATION
	is_valid = True
	if len(first_name) < 1:
		is_valid = False
		flash('First Name cannot be blank', 'fname_sms')
	if len(first_name) < 2:
		is_valid = False
		flash('First Name must be greater than 2 characters', 'fname_sms')
	if len(last_name) < 1:
		is_valid = False
		flash('Last Name cannot be blank', 'lname_sms')
	if len(last_name) < 2:
		is_valid = False
		flash('Last Name must be greater than 2 characters', 'lname_sms')
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
	db = connectToMySQL('admins')
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
	
	return is_valid



def login_validation(email, password):
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
	
	return is_valid




@app.route('/') #LOGIN________________________________________________
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
	db = connectToMySQL('admins')
	result = db.query_db(user_info, data)
	
	if len(result) > 0:
		if bcrypt.check_password_hash(result[0]['password'], password):
			user_id = result[0]['user_id']
			user_level = result[0]['user_level']
			set_session(user_id, user_level)
			if user_level == '9':
				return redirect('/admin')
			return redirect('/user')

	flash('You could not be logged in')
	return redirect('/')

def set_session(user_id, user_level):
	session['user_id'] = user_id
	session['user_level'] = user_level


@app.route('/') #REGISTER_____________________________________
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
		db = connectToMySQL('admins')
		add_user = '''INSERT INTO users (first_name, last_name, email, password, user_level, 
								  created_at, updated_at) 
						   VALUES (%(fn)s, %(ln)s, %(eml)s, %(pw_hash)s, '0', NOW(), NOW());'''
		data = {
			"fn": request.form.get("first_name"),
			"ln": request.form.get("last_name"),
			"eml": request.form.get("email"),
			"pw_hash": pw_hash
		}
		new_user_id = db.query_db(add_user, data)
		set_session(new_user_id, '0')	
		return redirect('/user')



@app.route('/admin') # ADMIN PAGE_________________________________________
def user_admin():
	if session['user_level'] != '9' or 'user_level' not in session:
		flash('You were log out!', 'danger')
		return redirect('/logout')
	
	mysql = connectToMySQL('admins')
	users = mysql.query_db('SELECT * FROM users;')

	query = "SELECT * FROM users WHERE user_id = %(fi)s;"
	data = {
		'fi': session['user_id']
	}
	db = connectToMySQL('admins')
	result = db.query_db(query, data)

	return render_template('admin.html', users=users, result=result)


@app.route('/user') #USER PAGE___________________________________________
def user_normal():
	db = connectToMySQL('admins')
	info_query = '''
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
	info = db.query_db(info_query, data)
	return render_template('info.html', info=info)



@app.route('/delete/<user_id>') #DELETE USER_______________________
def delete(user_id):
	if session['user_level'] != '9' or 'user_level' not in session:
		flash('You were log out!', 'danger')
		return redirect('/logout')

	info = 'SELECT id FROM users WHERE user_id = %(fi)s;'
	data = {
		"fi": user_id
	}
	db = connectToMySQL('admins')
	info = db.query_db(info, data)

	delete = "DELETE FROM users WHERE user_id = %(fi)s;"
	data = {
		"fi": user_id
	}
	db = connectToMySQL('admins')
	delete = db.query_db(delete, data)
	print(delete)
	return redirect('/admin')



@app.route('/switch/<user_id>') #SWITCH USER LEVEL
def switch(user_id):
	if session['user_level'] != '9' or 'user_level' not in session:
		flash('You were log out!', 'danger')
		return redirect('/logout')
	print(user_id)
	print(session['user_id'])
	query = "SELECT * FROM users WHERE user_id = %(fi)s;"
	data = {
		'fi': user_id
	}
	db = connectToMySQL('admins')
	result = db.query_db(query, data)
	if session['user_id'] == user_id:
		flash('You can not switch yourself!', 'warning')
		return redirect('/admin')
	if result[0]['user_level'] == '0':
		add_admin_query = "UPDATE users SET user_level = '9' WHERE user_id = %(fi)s;"
		data = {
			"fi": user_id
		}
		db = connectToMySQL('admins')
		add_admin = db.query_db(add_admin_query, data)
		return redirect('/admin')

	else:
		del_admin_query = "UPDATE users SET user_level = '0' WHERE user_id = %(fi)s;"
		data = {
			"fi": user_id
		}
		db = connectToMySQL('admins')
		del_admin = db.query_db(del_admin_query, data)
		return redirect('/admin')




@app.route('/logout') #LOGOUT___________________
def logout_user():
	session.clear()
	return redirect('/')



if __name__=="__main__":
	app.run(debug=True)
