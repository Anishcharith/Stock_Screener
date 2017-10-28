from flask import Flask, render_template, flash, request, redirect, url_for, session
from content_management import content
from dbconnect import connection
import numpy as np
import pandas as pd
import datetime


from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc
import scipy
import pygal

def screen(chunk):
    c.execute("select compname from companies;")
    comp_names = np.array(c.fetchall())
    chunk = ["roe3", ">", "30"]
    ans = []
    for comp in comp_names:
        procname =  chunk[0][:-1]
        args = [comp[0], int(chunk[0][-1]), 0.0]
        output = c.callproc(procname, args)
        c.execute('select @_'+procname+'_0, @_'+procname+'_1, @_'+procname+'_2')
        temp = c.fetchall()[0]
        if (eval(str(temp[2])+chunk[1]+chunk[2])):
            ans.append(temp)
        c.close()
        c = conn.cursor()
    return ans


app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def homepage():
    if request.method=="POST":
        print("OK")
        compx=request.form['search']
        print(compx)
        #return redirect(url_for("/login
        return redirect(url_for("Technical",comp=compx))
    else:
        return render_template("main.html")

@app.route('/dashboard/', methods = ['GET', 'POST'])
def dashboard():
    try:
        if session["logged_in"] == True:    
            flash('Logged in')
            return render_template("dashboard.html")
    except:
        return redirect(url_for("login"))

@app.route('/header/', methods=['GET','POST'])
def header():
    if request.method=="POST":
        print("OK")
        compx=request.form['search']
        print(compx)
        #return redirect(url_for("/login
        return redirect(url_for("Technical",comp=compx))

    else:
        return render_template("header.html")

@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method=="POST":
        c,conn=connection()
        attempted_username=request.form["username"]
        attempted_password=request.form["password"]
        data=c.execute("SELECT * FROM users WHERE username='%s';"%str((attempted_username)))
        data=c.fetchone()
        if sha256_crypt.verify(attempted_password,data[2]):
            session["logged_in"] = True
            session["username"] = data[1]
            return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route('/logout/',methods=['GET','POST'])
def logout():
    session.clear() 
    return redirect(url_for("homepage"))

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
            (username)
            x=c.execute("select * from users where username='"+str((username))+"'")
            if int(x)>0:
                return render_template("register.html")
            else:
                c.execute("INSERT INTO users (username,password,email) VALUES ('%s','%s','%s');"%(str((username)),str((password)),str((email))))
                conn.commit()
                c.close()
                conn.close()
                gc.collect()
                return redirect(url_for("login"))
    return render_template("register.html")

@app.route('/Technical/<comp>/',methods=['GET','POST'])
def Technical(comp):
    c,conn=connection()
    query = "SELECT * FROM %s_F ;"%(comp)
    c.execute(query)
    data_F = c.fetchall()
    header = ["Year", "Sales",	"Depr.", "Int.", "PBT","Tax", "NP", "Div_Amt", "Eq_Share_Cap", "Reserves","Borrowings", "Oth_Liab", "Net_Block", "CWIP",	"Inv", "Oth_Assets", "Rcvbles", "Inven.", "Cash","Eq_Shares"]
    # print(data)
    # return render_template("compdata.html",comp=comp,graph_data2017=graph_data2017,graph_data2016=graph_data2016,graph_data2015=graph_data2015,graph_data2014=graph_data2014, data = data)
    #return render_template("compadata.html",comp=comp, data_F = data_F, header = header)
    if request.method=="POST":
        compx=request.form['search']
        return redirect(url_for("Technical",comp=compx))
    else:
        c,conn=connection()
        c.execute("SELECT * FROM "+comp+"_T a, (select * from "+comp+"_T order by Date DESC limit 1) as b WHERE DATEDIFF(b.Date,a.Date)<30;")
        graph=pygal.Line()#explicit_size=True )#,width=1500, height=600)
        data=c.fetchall()
        date=pd.DatetimeIndex(np.array(data)[:,0])
        #print(date)
        graph.x_labels = map(lambda d: d.strftime('%Y-%m-%d'),date)
        #graph.x_labels=map(str,set(date.month))
        graph.add(comp,np.array(data)[:,1])
        graph_data1m=graph.render_data_uri()
        c.execute("SELECT * FROM "+comp+"_T a, (select * from "+comp+"_T order by Date DESC limit 1) as b WHERE DATEDIFF(b.Date,a.Date)<90;")
        graph=pygal.Line()
        data=c.fetchall()
        date=pd.DatetimeIndex(np.array(data)[:,0])
        #print(date)
        graph.x_labels = map(lambda d: d.strftime('%Y-%m-%d'),date)
        #graph.x_labels=map(str,set(date.month))
        #graph.x_labels=date.day
        graph.add(comp,np.array(data)[:,1])
        graph_data3m=graph.render_data_uri()
        c.execute("SELECT * FROM "+comp+"_T a, (select * from "+comp+"_T order by Date DESC limit 1) as b WHERE DATEDIFF(b.Date,a.Date)<180;")
        graph=pygal.Line()
        data=c.fetchall()
        date=pd.DatetimeIndex(np.array(data)[:,0])
        #print(date)
        graph.x_labels = map(lambda d: d.strftime('%Y-%m-%d'),date)
        #graph.x_labels=map(str,set(date.month))
        #graph.x_labels=date.day
        graph.add(comp,np.array(data)[:,1])
        graph_data6m=graph.render_data_uri()
        c.execute("SELECT * FROM "+comp+"_T a, (select * from "+comp+"_T order by Date DESC limit 1) as b WHERE DATEDIFF(b.Date,a.Date)<365;")
        graph=pygal.Line()
        data=c.fetchall()
        date=pd.DatetimeIndex(np.array(data)[:,0])
        #print(date)
        #graph.x_labels=date.day
        graph.x_labels = map(lambda d: d.strftime('%Y-%m-%d'),date)
        #graph.x_labels=map(str,set(date.month))
        graph.add(comp,np.array(data)[:,1])
        graph_data1y=graph.render_data_uri()
        c.execute("SELECT * FROM "+comp+"_T a, (select * from "+comp+"_T order by Date DESC limit 1) as b WHERE DATEDIFF(b.Date,a.Date)<730;")
        graph=pygal.Line()
        data=c.fetchall()
        date=pd.DatetimeIndex(np.array(data)[:,0])
        #print(date)
        graph.x_labels = map(lambda d: d.strftime('%Y-%m-%d'),date)
        #graph.x_labels=map(str,set(date.month))
        #graph.x_labels=date.day
        graph.add(comp,np.array(data)[:,1])
        graph_data2y=graph.render_data_uri()
        c.execute("SELECT * FROM "+comp+"_T a")
        graph=pygal.Line()
        data=c.fetchall()
        date=pd.DatetimeIndex(np.array(data)[:,0])
        #print(date)
        graph.x_labels = map(lambda d: d.strftime('%Y-%m-%d'),date)
        #graph.x_labels=map(str,set(date.month))
        #graph.x_labels=date.day
        graph.add(comp,np.array(data)[:,1])
        graph_datamax=graph.render_data_uri()
        return render_template("compdata.html",comp=comp,graph_data1m=graph_data1m,graph_data3m=graph_data3m,graph_data6m=graph_data6m,graph_data1y=graph_data1y,graph_data2y=graph_data2y,graph_datamax=graph_datamax)

@app.route('/screens/',methods=['GET','POST'])
def screens():
    if request.method == "POST":
        QUERY = request.form["search_query"]
        dfs = []
        CHUNKS = QUERY.split("AND")
        for chunk in CHUNKS:
            chunk = chunk.lstrip()
            chunk = chunk.split(" ")
            dfs.append(pd.DataFrame(screen(chunk), columns = ["compname", "Years", chunk[0][:-1]]))
            df_final = reduce(lambda left,right: pd.merge(left,right,on='compname'), dfs)
    else:
        return render_template("screens.html")




if __name__ == "__main__":
    app.secret_key = 'randshit'
    app.run()
