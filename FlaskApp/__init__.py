from flask import Flask, render_template, flash, request, redirect, url_for
from content_management import content
from dbconnect import connection
#from wtforms import Form

from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc
app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template("main.html")

@app.route('/dashboard/')
def dashboard():
    return render_template("dashboard.html")

@app.route('/header/')
def header():
    return render_template("header.html")

@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method=="POST":
        c,conn=connection()
        attempted_username=request.form["username"]
        attempted_password=request.form["password"]
        data=c.execute("SELECT * FROM users WHERE username='%s';"%str(thwart(attempted_username)))
        data=c.fetchone()[2]
        if sha256_crypt.verify(attempted_password,data):
            return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route('/register/',methods=['GET','POST'])
def register_page():
    if request.method=="POST":
        email=request.form["email"]
        username=request.form["username"]
        password=request.form["password"]
        repassword=request.form["repassword"]
        if not(password!=repassword or email==None or len(username)<3 or len(password)<3):
            password=sha256_crypt.encrypt(str(password))
            c,conn=connection()
            thwart(username)
            x=c.execute("select * from users where username='"+str(thwart(username))+"'")
            if int(x)>0:
                return render_template("register.html")
            else:
                c.execute("INSERT INTO users (username,password,email) VALUES ('%s','%s','%s');"%(str(thwart(username)),str(thwart(password)),str(thwart(email))))
                conn.commit()
                c.close()
                conn.close()
                gc.collect()
                return redirect(url_for("login"))
    return render_template("register.html")

if __name__ == "__main__":
    app.run()
