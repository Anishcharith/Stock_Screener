from flask import Flask, render_template, flash
#from content_management import Content
#from dbconnect import connection
#from wtforms import Form
#from passlib.hash import sha256_crypt
#from MySQLdb import escape_string as thwart
#import gc

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
    return render_template("login.html")
"""
class RegistrationForm(Form):
    username=TextField('Username',[validators.Length(min=4,max=20)])
    email=TextField('Email Address',[validators.Length(min=6,max=50)])
    password=PasswordField('Password',[validators.Required(),
        validators.EqualTo('confirm',message="Passwords must Match")]) 
    confirm= PasswordField('Repeat password')
    accept_tos=BoolenField('GG')
    
@app.route('/register/',methods=['GET','POST'])
def register_page():
    try:
        form=RegistrationForm(request.form)
        if request.method=="POST" and form.validate():
            username=form.username.data
            email=form.email.data
            password=sha256_crypt.encrypt((str(form.password.data)))
            c,conn =connection()
            x=c.execute("select * from users where username=(%s)",
                    (thwart(username)))

            if int(x) >0:
                flash("Username taken boi")
                return render_template('register.html',form=form)
            else:
                c.execute("insert into users (username,password,email) values(%s,%s,%s)"
                (thwart(username),thwart(password),thwart(email)))
                conn.commit()
                flash("thanks for registering")
                c.close()
                conn.close()
                gc.collect()
                session['logged_in']=True
                session['username']=username
                return redirect(url_for('dashboard'))

            return render_template("register.html",form=form)
    except Exception as e:
        return str(e)
"""
if __name__ == "__main__":
    app.run()
