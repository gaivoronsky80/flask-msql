from flask import Flask, render_template, request, redirect
from mysqlconnection import connectToMySQL

app = Flask(__name__)
app.secret_key = 'keep it secret, keep it safe'

@app.route('/')
def index():
	mysql = connectToMySQL('c_plus_r_pets')
	pets = mysql.query_db('SELECT id, name, type FROM pets;')
	print(pets)
	return render_template('index.html', all_pets=pets)

@app.route('/add_pet', methods=["POST"])
def add_pet_to_db():
	query = "INSERT INTO pets (name, type, created_at, updated_at) VALUES (%(n)s, %(t)s, NOW(), NOW());"
	data = {
		"n": request.form["pet_name"],
		"t": request.form["pet_type"]
	}
	db = connectToMySQL('c_plus_r_pets')
	db.query_db(query, data)
	return redirect('/')








if __name__=="__main__":
    app.run(debug=True)