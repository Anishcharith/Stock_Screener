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

def compfound(comp):
    c,conn=connection()
    try:
        if session["logged_in"]==True:
            c.execute("select compId from nifty200 where compname='"+comp+"';")
            compId=c.fetchone()[0]
            x=c.execute("select * from watchlist where userId="+str(session["userid"])+" and compId = "+str(compId)+";")
            test=c.fetchall()
            print(test)
            if x>0:
                return True
            else:
                return False
    except:
        return False

app.jinja_env.globals.update(compfound=compfound)

@app.route('/',methods=['GET','POST'])
def homepage():
    c,conn=connection()
    if request.method=="POST":
        try:
            compx=request.form['search']
            c.execute("select compname from nifty200 where compname like '%"+compx+"%';")
            compnames=np.array(c.fetchall())[:,0]
            print(compnames)
            return render_template("searchreasults.html",compnames=compnames)
        except:
            pass
    return render_template("main.html")

@app.route('/searchreasults/',methods=['GET','POST'])
def searchreasults(compnames):
    c,conn=connection()
    if request.method=="POST":
        try:
            compx=request.form['search']
            c.execute("select compname from nifty200 where compname like '%"+compx+"%';")
            compnames=np.array(c.fetchall())[:,0]
            print(compnames)
            return render_template("searchreasults.html",compnames=compnames)
        except:
            pass
    return render_template("searchreasults.html",compnames=compnames)

@app.route('/dashboard/', methods = ['GET', 'POST'])
def dashboard():
    c,conn=connection()
    if request.method=="POST":
        try:
            compx=request.form['search']
            c.execute("select compname from nifty200 where compname like '%"+compx+"%';")
            compnames=np.array(c.fetchall())[:,0]
            print(compnames)
            return render_template("searchreasults.html",compnames=compnames)
        except:
            pass
    try:
        if session["logged_in"] == True:    
            flash('Logged in')
            return redirect(url_for("homepage"))
    except:
        return redirect(url_for("login"))

@app.route('/header/', methods=['GET','POST'])
def header():
    c,conn=connection()
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
    c,conn=connection()
    if request.method=="POST":
        try:
            compx=request.form['search']
            c.execute("select compname from nifty200 where compname like '%"+compx+"%';")
            compnames=np.array(c.fetchall())[:,0]
            print(compnames)
            return render_template("searchreasults.html",compnames=compnames)
        except:
            pass
    if request.method=="POST":
        c,conn=connection()
        attempted_username=request.form["username"]
        attempted_password=request.form["password"]
        data=c.execute("SELECT * FROM users WHERE username='%s';"%str((attempted_username)))
        data=c.fetchone()
        try:
            if sha256_crypt.verify(attempted_password,data[2]):
                session["logged_in"] = True
                session["username"] = data[1]
                session["userid"]=data[0]
                return redirect(url_for("dashboard"))
        except:
            flash('invalid credentials, try again')
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route('/logout/',methods=['GET','POST'])
def logout():
    session.clear() 
    return redirect(url_for("homepage"))

@app.route('/register/',methods=['GET','POST'])
def register_page():
    c,conn=connection()
    if request.method=="POST":
        try:
            compx=request.form['search']
            c.execute("select compname from nifty200 where compname like '%"+compx+"%';")
            compnames=np.array(c.fetchall())[:,0]
            print(compnames)
            return render_template("searchreasults.html",compnames=compnames)
        except:
            pass
    if request.method=="POST":
        email=request.form["email"]
        username=request.form["username"]
        password=request.form["password"]
        repassword=request.form["repassword"]
        if not(password!=repassword or email==None or len(username)<3 or len(password)<3):
            password=sha256_crypt.encrypt(str(password))
            (username)
            x=c.execute("select * from users where username='"+str((username))+"'")
            if int(x)>0:
                flash("username already taken")
                return render_template("register.html")
            else:
                c.execute("INSERT INTO users (username,password,email) VALUES ('%s','%s','%s');"%(str((username)),str((password)),str((email))))
                conn.commit()
                c.close()
                conn.close()
                gc.collect()
                return redirect(url_for("login"))
        else:
            flash(" error in one of the fields")
            return render_template("register.html")
    return render_template("register.html")

@app.route('/Technical/<comp>/',methods=['GET','POST'])
def Technical(comp):
    c,conn=connection()
    if request.method=="POST":
        try:
            compx=request.form['search']
            c.execute("select compname from nifty200 where compname like '%"+compx+"%';")
            compnames=np.array(c.fetchall())[:,0]
            print(compnames)
            return render_template("searchreasults.html",compnames=compnames)
        except:
            pass
    query = "SELECT * FROM %s_F ;"%(comp)
    c.execute(query)
    data_F = c.fetchall()
    header = ["Year", "Sales",	"Depr.", "Int.", "PBT","Tax", "NP", "Div_Amt", "Eq_Share_Cap", "Reserves","Borrowings", "Oth_Liab", "Net_Block", "CWIP",	"Inv", "Oth_Assets", "Rcvbles", "Inven.", "Cash","Eq_Shares"]
    c,conn=connection()
    c.execute("SELECT * FROM nse200_T a, (select * from nse200_T where Comp_ID='"+comp+"' order by Date DESC limit 1) as b WHERE a.Comp_ID='"+comp+"' and DATEDIFF(b.Date,a.Date)<30;")
    graph=pygal.Line()
    data=c.fetchall()
    print(data)
    date=pd.DatetimeIndex(np.array(data)[:,1])
    graph.x_labels = map(lambda d: d.strftime('%Y-%m-%d'),date)
    graph.add(comp,np.array(data)[:,6])
    graph_data1m=graph.render_data_uri()
    c.execute("SELECT * FROM nse200_T a, (select * from nse200_T where Comp_ID='"+comp+"' order by Date DESC limit 1) as b WHERE a.Comp_ID='"+comp+"' and DATEDIFF(b.Date,a.Date)<90;")
    graph=pygal.Line()
    data=c.fetchall()
    date=pd.DatetimeIndex(np.array(data)[:,1])
    graph.x_labels = map(lambda d: d.strftime('%Y-%m-%d'),date)
    graph.add(comp,np.array(data)[:,6])
    graph_data3m=graph.render_data_uri()
    c.execute("SELECT * FROM nse200_T a, (select * from nse200_T where Comp_ID='"+comp+"' order by Date DESC limit 1) as b WHERE a.Comp_ID='"+comp+"' and DATEDIFF(b.Date,a.Date)<180;")
    graph=pygal.Line()
    data=c.fetchall()
    date=pd.DatetimeIndex(np.array(data)[:,1])
    graph.x_labels = map(lambda d: d.strftime('%Y-%m-%d'),date)
    graph.add(comp,np.array(data)[:,6])
    graph_data6m=graph.render_data_uri()
    c.execute("SELECT * FROM nse200_T a, (select * from nse200_T where Comp_ID='"+comp+"' order by Date DESC limit 1) as b WHERE a.Comp_ID='"+comp+"' and DATEDIFF(b.Date,a.Date)<365;")
    graph=pygal.Line()
    data=c.fetchall()
    date=pd.DatetimeIndex(np.array(data)[:,1])
    graph.x_labels = map(lambda d: d.strftime('%Y-%m-%d'),date)
    graph.add(comp,np.array(data)[:,6])
    graph_data1y=graph.render_data_uri()
    c.execute("SELECT * FROM nse200_T a, (select * from nse200_T where Comp_ID='"+comp+"' order by Date DESC limit 1) as b WHERE a.Comp_ID='"+comp+"' and DATEDIFF(b.Date,a.Date)<730;")
    graph=pygal.Line()
    data=c.fetchall()
    date=pd.DatetimeIndex(np.array(data)[:,1])
    graph.x_labels = map(lambda d: d.strftime('%Y-%m-%d'),date)
    graph.add(comp,np.array(data)[:,6])
    graph_data2y=graph.render_data_uri()
    c.execute("SELECT * FROM nse200_T where Comp_ID='"+comp+"' order by Date asc")
    graph=pygal.Line()
    data=c.fetchall()
    date=pd.DatetimeIndex(np.array(data)[:,1])
    graph.x_labels = map(lambda d: d.strftime('%Y-%m-%d'),date)
    graph.add(comp,np.array(data)[:,6])
    graph_datamax=graph.render_data_uri()
    c.execute("select Company from nse200 where Comp_ID='"+comp+"';")
    compname=np.array(c.fetchone())[0]
    return render_template("compdata.html",compname=compname,comp=comp,graph_data1m=graph_data1m,graph_data3m=graph_data3m,graph_data6m=graph_data6m,graph_data1y=graph_data1y,graph_data2y=graph_data2y,graph_datamax=graph_datamax)

@app.route('/watchlist/',methods=['GET','POST'])
def test():
    c,conn=connection()
    if request.method=="POST":
        try:
            compx=request.form['search']
            c.execute("select compname from nifty200 where compname like '%"+compx+"%';")
            compnames=np.array(c.fetchall())[:,0]
            print(compnames)
            return render_template("searchreasults.html",compnames=compnames)
        except:
            pass
    try:
        if session["logged_in"]:
            c.execute("select compname from nifty200 where compId in (select compId from watchlist group by compId order by count(*) )limit 10;")
            popularcomps=np.array(c.fetchall())[:,0]
            c.execute("select compname from nifty200 where compId in (select compId from watchlist where userId="+str(session["userid"])+");")
            try:
                usercomps=np.array(c.fetchall())[:,0]
            except:
                usercomps=[]
            return render_template("watchlist.html",popularcomps=popularcomps,usercomps=usercomps)
    except:
        flash('Need to login first')
        return redirect(url_for("login"))

@app.route('/addtowatchlist/<comp>/',methods=['GET','POST'])
def addtowatchlist(comp):
    c,conn=connection()
    if session["logged_in"]==True:
        c.execute("select compId from nifty200 where compname='"+comp+"';")
        compId=c.fetchone()[0]
        c.execute("select uid from users where username='"+session['username']+"';")
        userId=c.fetchone()[0]
        c.execute("insert into watchlist (compId,userId) values("+str(compId)+","+str(userId)+");")
        conn.commit()
        flash("added to watchlist")
        return redirect(url_for("Technical",comp=comp))

@app.route('/removefromwatchlist/<comp>/',methods=['GET','POST'])
def removefromwatchlist(comp):
    c,conn=connection()
    if session["logged_in"]==True:
        c.execute("select compId from nifty200 where compname='"+comp+"';")
        compId=c.fetchone()[0]
        c.execute("select uid from users where username='"+session['username']+"';")
        userId=c.fetchone()[0]
        c.execute("delete from watchlist where compId="+str(compId)+" and userId = "+str(userId)+";")
        conn.commit()
        flash("deleted from watchlist")
        return redirect(url_for("Technical",comp=comp))

@app.route('/screens/',methods=['GET','POST'])
def screens():
    c,conn=connection()
    if request.method=="POST":
        try:
            compx=request.form['search']
            c.execute("select compname from nifty200 where compname like '%"+compx+"%';")
            compnames=np.array(c.fetchall())[:,0]
            print(compnames)
            return render_template("searchreasults.html",compnames=compnames)
        except:
            pass
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
