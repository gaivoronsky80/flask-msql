from flask import Flask, render_template, request, redirect, flash, session
from flask_bcrypt import Bcrypt

import re
from mysqlconnection import connectToMySQL
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app = Flask(__name__)

bcrypt = Bcrypt(app)
app.secret_key = 'keep it secret, keep it safe'



@app.route('/') #LOGIN________________________________________________
def login_user():
	return render_template('login.html')

@app.route('/login_success', methods=['POST'])
def login_user_success():
	is_valid = True
	if not EMAIL_REGEX.match(request.form['email']):
		is_valid = False
		flash('Invalid email address!', 'email')
	if len(request.form["password"]) < 1:
		is_valid = False
		flash("Invalid password!", 'password')
	if not is_valid:
		return redirect('/')
	else:
		query = "SELECT * FROM users WHERE email = %(eml)s;"
		data = {
			'eml': request.form['email']
		}
		db = connectToMySQL('login_and_registration')
		result = db.query_db(query, data)
		session['email'] = request.form['email']
		if len(result) > 0:
			if bcrypt.check_password_hash(result[0]['password'], request.form['password']):
				session['user_id'] = result[0]['id']
				return redirect('/show_info/' + str(session['user_id']))
		flash('You could not be logged in')
		return redirect('/')



@app.route('/add_user') #REGISTER_____________________________________
def new_user():
	return render_template('create.html')

@app.route('/add_success', methods=['POST'])
def sing_success():
	is_valid = True
	if len(request.form["first_name"]) < 1:
		is_valid = False
		flash("Please enter a first name", 'first_name')
	if len(request.form["last_name"]) < 1:
		is_valid = False
		flash("Please enter a last name", 'last_name')
	if not EMAIL_REGEX.match(request.form['email']):
		is_valid = False
		flash('Please enter an email', 'email')
	if len(request.form["password"]) < 1:
		is_valid = False
		flash("Please enter a password", 'password')
	if len(request.form["confirm_password"]) < 1:
		is_valid = False
		flash("Please enter a confirm password", 'confirm_password')
	if request.form['password'] != request.form["confirm_password"]:
		is_valid = False
		flash('Confirm password must be match to password', 'match_password')
	if not is_valid:
		return redirect('/add_user')
	else:
		pw_hash = bcrypt.generate_password_hash(request.form['password'])
		print(pw_hash)
		db = connectToMySQL('login_and_registration')
		query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(eml)s, %(pw_hash)s, NOW(), NOW());"
		data = {
			"fn": request.form.get("first_name"),
			"ln": request.form.get("last_name"),
			"eml": request.form.get("email"),
			"pw_hash": pw_hash
		}
		id = db.query_db(query, data)	
		return redirect('/show_info/' + str(id))



@app.route('/show_info/<user_id>') #USER PAGE_________________________
def show_user(user_id):
	query = 'SELECT id, first_name, last_name, email, created_at, updated_at FROM users WHERE id = %(fi)s;'
	data = {
		"fi": user_id
	}
	mysql = connectToMySQL('login_and_registration')
	query= mysql.query_db(query, data)
	return render_template('info.html', users=user_id, query=query)



@app.route('/update/<user_id>') #EDIT_________________________________
def update_user(user_id):
	query = 'SELECT id FROM users WHERE id = %(fi)s;'
	data = {
		"fi": user_id
	}
	db = connectToMySQL('login_and_registration')
	query = db.query_db(query, data)
	print(query)
	return render_template('edit.html', users=user_id, query=query)

@app.route('/update_success/<user_id>', methods=['POST'])
def update_user_success(user_id):
	update = "UPDATE users SET first_name = %(fn)s, last_name = %(ln)s, email = %(eml)s WHERE id = %(fi)s;"
	data = {
		"fn": request.form.get("edit_first_name"),
		"ln": request.form.get("edit_last_name"),
		"eml": request.form.get("edit_email"),
		"fi": user_id
	}
	db = connectToMySQL('login_and_registration')
	update = db.query_db(update, data)
	print(update)
	return redirect('/show_info/' + str(session['user_id']))




@app.route('/delete/<user_id>') #DELETE__________________________
def delete(user_id):
	query = 'SELECT id FROM users WHERE id = %(fi)s;'
	data = {
		"fi": user_id
	}
	db = connectToMySQL('login_and_registration')
	query = db.query_db(query, data)
	delete = "DELETE FROM users WHERE id = %(fi)s;"
	data = {
		"fi": user_id
	}
	db = connectToMySQL('login_and_registration')
	delete = db.query_db(delete, data)
	print(delete, query)
	return redirect('/')



@app.route('/logout') #LOGOUT_____________________________________
def logout_user():
	session.pop('user_id')
	session.pop('email')
	return redirect('/')



if __name__=="__main__":
    app.run(debug=True)