from flask import Flask, render_template, request, redirect, flash, session
from flask_bcrypt import Bcrypt

import re
from mysqlconnection import connectToMySQL

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'keep it secret, keep it safe'

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$')



def register_validation(): #REGISTER VALIDATION
	is_valid = True
	if len(request.form["first_name"]) < 1:
		is_valid = False
		flash('First Name cannot be blank', 'fname_sms')
	if len(request.form["first_name"]) < 2:
		is_valid = False
		flash('First Name must be greater than 2 characters', 'fname_sms')
	if len(request.form["last_name"]) < 1:
		is_valid = False
		flash('Last Name cannot be blank', 'lname_sms')
	if len(request.form["last_name"]) < 2:
		is_valid = False
		flash('Last Name must be greater than 2 characters', 'lname_sms')
	if len(request.form["email"]) < 1:
		is_valid = False
		flash('Email cannot be blank', 'email_sms')
	if not EMAIL_REGEX.match(request.form['email']):
		is_valid = False
		flash('Invalid email address', 'email_sms')
	if len(request.form["password"]) < 1:
		is_valid = False
		flash('Password cannot be blank', 'password_sms')
	if len(request.form['password']) < 8:
		is_valid = False
		flash('Password must be greater than 8 characters', 'password_sms')
	if not PASSWORD_REGEX.match(request.form['password']):
		flash('Password must contain at least one lowercase letter, one uppercase letter, and one digit', 'password_sms')
	if len(request.form["confirm_password"]) < 1:
		is_valid = False
		flash('Confirm Password cannot be blank', 'c_password_sms')
	if request.form['password'] != request.form["confirm_password"]:
		is_valid = False
		flash('Confirm password must be match to password', 'c_password_sms')
	if not is_valid:
		session['password'] = None
		session['confirm_password'] = None
		return False
	else:
		session['first_name'] = request.form.get("first_name")
		session['last_name'] = request.form.get("last_name")
		session['email'] = request.form.get("email")
		session['password'] = request.form.get("password")
		session['confirm_password'] = request.form.get("confirm_password")
		return True



def login_validation():
	is_valid = True
	if len(request.form["email"]) < 1:
		is_valid = False
		flash('Email cannot be blank', 'email_sms')
	if not EMAIL_REGEX.match(request.form['email']):
		is_valid = False
		flash('Invalid email address!', 'email_sms')
	if len(request.form["password"]) < 1:
		is_valid = False
		flash('Password cannot be blank', 'password_sms')
	if len(request.form['password']) < 8:
		is_valid = False
		flash('Password must be greater than 8 characters', 'password_sms')
	if not PASSWORD_REGEX.match(request.form['password']):
		flash('Password must contain at least one lowercase letter, one uppercase letter, and one digit', 'password_sms')
	if not is_valid:
		session['password'] = None
		return False
	else:
		session['email'] = request.form.get("email")
		session['password'] = request.form.get("password")
		return True



def user_id():
	user_id = 'SELECT id FROM users WHERE email = %(eml)s;'
	data = {
		'eml': request.form['email']
	}
	db = connectToMySQL('private_wall')
	id = db.query_db(user_id, data)
	session['user_id'] = id[0]['id']
	return True
		


@app.route('/') #LOGIN________________________________________________
def login():
	session['email'] = request.form.get("email")
	session['password'] = request.form.get("password")
	return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_user():
	if login_validation() != True:
		return redirect('/')
	else:
		session['password'] = request.form['password']
		user_info = "SELECT * FROM users WHERE email = %(eml)s;"
		data = {
			'eml': request.form['email']
		}
		db = connectToMySQL('private_wall')
		result = db.query_db(user_info, data)
		session['email'] = request.form['email']
		if len(result) > 0:
			if bcrypt.check_password_hash(result[0]['password'], request.form['password']):
				session['user_id'] = result[0]['id']
				return redirect('/show_info')
		flash('You could not be logged in')
		return redirect('/')



@app.route('/add_user') #REGISTER_____________________________________
def new_user():
	session['first_name'] = request.form.get("first_name")
	session['last_name'] = request.form.get("last_name")
	session['email'] = request.form.get("email")
	session['password'] = request.form.get("password")
	return render_template('create.html')

@app.route('/add', methods=['POST'])
def add_new_user():
	if register_validation() != True:
		return redirect('/add_user')
	else:
		pw_hash = bcrypt.generate_password_hash(request.form['password'])
		print(pw_hash)
		db = connectToMySQL('private_wall')
		add_user = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(eml)s, %(pw_hash)s, NOW(), NOW());"
		data = {
			"fn": request.form.get("first_name"),
			"ln": request.form.get("last_name"),
			"eml": request.form.get("email"),
			"pw_hash": pw_hash
		}
		id = db.query_db(add_user, data)
		session['user_id'] = id
		# print(add_user)	
		return redirect('/show_info')



@app.route('/show_info') #USER PAGE_________________________
def show_user():
	info_query = '''
		 SELECT id, 
				first_name, 
				last_name, 
				email, 
				created_at, 
				updated_at 
		   FROM users 
		  WHERE id = %(fi)s;'''
	data = {
		"fi": session['user_id']
	}
	db = connectToMySQL('private_wall')
	info = db.query_db(info_query, data)
	return render_template('info.html', info=info)



@app.route('/update/<user_id>') #EDIT_________________________________
def update_user(user_id):
	info = 'SELECT id FROM users WHERE id = %(fi)s;'
	data = {
		"fi": user_id
	}
	db = connectToMySQL('private_wall')
	info = db.query_db(info, data)
	return render_template('edit.html', info=info)

@app.route('/update_success/<user_id>', methods=['POST'])
def update_user_success(user_id):
	update = "UPDATE users SET first_name = %(fn)s, last_name = %(ln)s, email = %(eml)s WHERE id = %(fi)s;"
	data = {
		"fn": request.form.get("edit_first_name"),
		"ln": request.form.get("edit_last_name"),
		"eml": request.form.get("edit_email"),
		"fi": user_id
	}
	db = connectToMySQL('private_wall')
	update = db.query_db(update, data)
	# print(update)
	return redirect('/show_info')



@app.route('/delete/<user_id>') #DELETE USER_______________________
def delete(user_id):
	info = 'SELECT id FROM users WHERE id = %(fi)s;'
	data = {
		"fi": user_id
	}
	db = connectToMySQL('private_wall')
	info = db.query_db(info, data)
	delete = "DELETE FROM users WHERE id = %(fi)s;"
	data = {
		"fi": user_id
	}
	db = connectToMySQL('private_wall')
	delete = db.query_db(delete, data)
	# print(delete, query)
	return redirect('/')



@app.route('/delete_message/<post_id>') #DELETE MESSAGE________
def delete_message(post_id):
	if session['user_id'] != session[receiver_id]:
		flash("You are trying delete the message which doesn't belong to you!", 'danger')
		return redirect('/wall_chat')
	else:
		delete_text = "DELETE FROM posts WHERE posts.id = %(fm)s;"
		data = {
			"fm": post_id
		}
		db = connectToMySQL('private_wall')
		delete_text = db.query_db(delete_text, data)
		# print(delete_text)
		return redirect('/wall_chat')




@app.route('/wall_chat') #CHAT_______________________________
def wall_chat():
	if 'user_id' not in session:
		return redirect('/')

	user_query = '''
			 SELECT first_name 
			   FROM users 
			  WHERE id = %(fi)s;'''
			  
	data = {
		'fi': session['user_id']
	}
	db = connectToMySQL('private_wall')
	user = db.query_db(user_query, data)

	all_users_query = 'SELECT * FROM users WHERE id != %(fi)s;'
	data = {
		'fi': session['user_id']
	}
	db = connectToMySQL('private_wall')
	users = db.query_db(all_users_query, data)

	wall_posts_query = '''
			 SELECT p.id, 
					p.post, 
					p.created_at, 
					u.first_name, 
					p.receiver_id 
			   FROM posts AS p
		  LEFT JOIN users AS u
		  		 ON p.receiver_id = u.id 
		  	  WHERE u.id = %(receiver_id)s 
		   ORDER BY u.first_name;'''

	data = {
		'receiver_id': session['user_id']
	}
	db = connectToMySQL('private_wall')
	posts = db.query_db(wall_posts_query, data)

	for_you_query = '''
			SELECT count(posts.post) 
				AS for_you
			  FROM posts 
			 WHERE receiver_id = %(fi)s;'''
	data = {
		'fi': session['user_id']
	}
	db = connectToMySQL('private_wall')
	for_you = db.query_db(for_you_query, data)

	you_have_query = '''
			SELECT count(posts.post) 
				AS you_have
			  FROM posts 
			 WHERE sender_id = %(fi)s;'''
	data = {
		'fi': session['user_id']
	}
	db = connectToMySQL('private_wall')
	you_have = db.query_db(you_have_query, data)
	# print("*"*80)
	# print(wall_posts)
	# print("*"*80)
	return render_template('chat.html', posts=posts, user=user, users=users, for_you=for_you, you_have=you_have)

@app.route('/add_message', methods=['POST']) #ADD POST
def add_post():
	db = connectToMySQL('private_wall')

	add_post = '''
		INSERT INTO posts (post, sender_id, receiver_id) 
			 VALUES (%(content)s, %(sender_id)s, %(receiver_id)s);'''

	data = {
		"content": request.form.get("add_text"),
		"sender_id": session['user_id'],
		"receiver_id": request.form.get("receiver")
	}
	db = db.query_db(add_post, data)
	# print(add_post)	
	return redirect('/wall_chat')





@app.route('/logout') #LOGOUT___________________
def logout_user():
	session.clear()
	return redirect('/')



if __name__=="__main__":
	app.run(debug=True)
