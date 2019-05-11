from flask import Flask, render_template, request, redirect, flash, session
import re
from mysqlconnection import connectToMySQL

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app = Flask(__name__)
app.secret_key = 'keep it secret, keep it safe'



@app.route('/') #SHOW INPUT
def index():
	return render_template('index.html')



@app.route('/add', methods=['POST']) #ADD EMAIL
def add_mail():
	is_valid = True
	if not EMAIL_REGEX.match(request.form['email']):
		is_valid = False
		flash('Invalid email address!', 'email')
	if not is_valid:
		return redirect('/')
	else:
		query = "INSERT INTO emails (email, created_at, updated_at) VALUES (%(eml)s, NOW(), NOW());"
		data = {
			'eml': request.form.get('email')
		}
		db = connectToMySQL('email_valid')
		db.query_db(query, data)
		session['email'] = request.form['email']
		return redirect('/success')



@app.route('/success') #SHOW INFO
def info():
	query = 'SELECT * FROM emails;'
	db = connectToMySQL('email_valid')
	query= db.query_db(query)
	return render_template('success.html', email=session['email'], query=query)



if __name__=="__main__":
	app.run(debug=True)

