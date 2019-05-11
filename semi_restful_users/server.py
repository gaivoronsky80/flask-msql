from flask import Flask, render_template, request, redirect, flash
from mysqlconnection import connectToMySQL

app = Flask(__name__)
app.secret_key = 'keep it secret, keep it safe'


@app.route('/users') #SHOW ALL USERS
def index():
	mysql = connectToMySQL('semi_restful_users')
	users = mysql.query_db('SELECT id, CONCAT(first_name," ", last_name) AS full_name, email, created_at FROM users;')
	print(users)
	return render_template('read_all.html', users=users)



@app.route('/add_new') #ADD NEW USER
def add_user():
	return render_template('create.html')

@app.route('/new', methods=['POST'])
def add_a_new_user():
	is_valid = True
	if len(request.form["first_name"]) < 1:
		is_valid = False
		flash("Please enter a first name")
	if len(request.form["last_name"]) < 1:
		is_valid = False
		flash("Please enter a last name")
	if len(request.form["email"]) < 1:
		is_valid = False
		flash("Please enter an email")
	if not is_valid:
		return redirect('/add_new')
	else:
		query = "INSERT INTO users (first_name, last_name, email, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(eml)s, NOW(), NOW());"
		data = {
			"fn": request.form.get("first_name"),
			"ln": request.form.get("last_name"),
			"eml": request.form.get("email")
		}
		db = connectToMySQL('semi_restful_users')
		db.query_db(query, data)
		flash("Friend successfully added!")
		return redirect('/users')



@app.route('/users/<user_id>') #SHOW USER INFO
def show(user_id):
	query = 'SELECT id, first_name, last_name, email, created_at, updated_at FROM users WHERE id = %(fn)s;'
	data = {
		"fn": user_id
	}
	mysql = connectToMySQL('semi_restful_users')
	query= mysql.query_db(query, data)		
	return render_template('info.html', users=user_id, query=query)



@app.route('/edit/<user_id>')  # UPDATE USER INFO
def update_user_in_db(user_id):
	query = 'SELECT id FROM users WHERE id = %(fd)s;'
	data = {
		"fd": user_id
	}
	db = connectToMySQL('semi_restful_users')
	query = db.query_db(query, data)
	print(query)
	return render_template('edit.html', users=user_id, query=query)

@app.route('/update/<user_id>', methods=['POST'])
def edit_user(user_id):
	update = "UPDATE users SET first_name = %(fn)s, last_name = %(ln)s, email = %(eml)s WHERE id = %(fd)s;"
	data = {
		"fn": request.form.get("edit_first_name"),
		"ln": request.form.get("edit_last_name"),
		"eml": request.form.get("edit_email"),
		"fd": user_id
	}
	db = connectToMySQL('semi_restful_users')
	update = db.query_db(update, data)
	print(update)
	return redirect('/users')



@app.route('/delete/<user_id>')  # DELETE USER
def delete_user(user_id):
	query = 'SELECT id FROM users WHERE id = %(fd)s;'
	data = {
		"fd": user_id
	}
	db = connectToMySQL('semi_restful_users')
	query = db.query_db(query, data)
	delete = "DELETE FROM users WHERE id = %(fd)s;"
	data = {
		"fd": user_id
	}
	db = connectToMySQL('semi_restful_users')
	delete = db.query_db(delete, data)
	print(delete, query)
	return redirect('/users')




if __name__=="__main__":
    app.run(debug=True)