import email
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL, MySQLdb
import mysql
import MySQLdb.cursors
import re



app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'expresswrite'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
@app.route('/')

@app.route('/login', methods =['GET', 'POST'])
def login():
    if request.method == 'POST':
        email= request.form['email']
        password = request.form['password'].encode('utf-8')
        
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM user WHERE email = %s AND password = %s", (email, password))
        users = cur.fetchone()
        cur.close()
        if users:
            session['loggedin'] = True
            session['email'] = users['email']
            return render_template('index.html')
        else:
            return 'Incorrect email / password !'
    return render_template('login.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method =='POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO user(name,email,password) VALUES(%s, %s, %s)", (name, email, password))
        mysql.connection.commit()
        cur.close()
        return render_template('login.html')
    return render_template('register.html')



if __name__ == "__main__":
    app.secret_key = "express"
    app.run(debug=True)