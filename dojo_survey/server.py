from flask import Flask, render_template, request, redirect, flash, session
from mysqlconnection import connectToMySQL

app = Flask(__name__)    
app.secret_key = 'keep it secret, keep it safe'

@app.route("/")
def index():
	return render_template("dojo_survey_index.html")

@app.route("/process", methods=["POST"])  #ADD NEW DOJO
def process_form():
	is_valid = True
	if len(request.form["first_name"]) < 1:
		is_valid = False
		flash("Please enter a first name")
	if len(request.form["last_name"]) < 1:
		is_valid = False
		flash("Please enter a last name")
	if request.form.get('location') == None:
		is_valid = False
		flash("Please enter a location")
	if request.form.get('language') == None:
		is_valid = False
		flash("Please enter a language")
	if not is_valid:
		return redirect('/')
	else:
		query = "INSERT INTO dojos (fname, lname, location, language, comment, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(lctn)s, %(lngg)s, %(cmmnt)s, NOW(), NOW());"
		data = {
			'fn': request.form.get('first_name'),
			'ln': request.form.get('last_name'),
			'lctn': request.form.get('location'),
			'lngg': request.form.get('language'),
			'cmmnt': request.form.get('comment')
		}
		db = connectToMySQL('dojo_survey_w_validation')
		db.query_db(query, data)

	session['first_name'] = request.form.get('first_name')
	session['last_name'] = request.form.get('last_name')
	session['location'] = request.form.get('location')
	session['language'] = request.form.get('language')
	session['comment'] = request.form.get('comment')
	return redirect('/success')


@app.route("/success")
def success():
	return render_template("info.html")


if __name__=="__main__":   
    app.run(debug=True)   

	# request.form['location'] = ['San Jose', 'Seattle']
	# request.form['language'] = ['HTML', 'CSS', 'JavaScript', 'Python']


