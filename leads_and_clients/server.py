from flask import Flask, render_template, request, redirect, flash
from mysqlconnection import connectToMySQL

app = Flask(__name__)
app.secret_key = 'keep it secret, keep it safe'


@app.route('/') #SHOW ALL USERS
def index():
	mysql = connectToMySQL('leads_and_clients')
	users_leads = mysql.query_db('''
							SELECT CONCAT(customers.first_name,' ', customers.last_name) 
							AS full_name, customers.client_id, count(leads.leads_id) 
							AS quant, leads.customer_id 
							FROM customers 
							LEFT JOIN leads 
							ON leads.customer_id = customers.client_id 
							GROUP BY customers.client_id;''')
	return render_template('index.html', users_leads=users_leads)



if __name__=="__main__":
    app.run(debug=True)