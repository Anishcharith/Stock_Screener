from flask import Flask, render_template, flash, request, redirect, url_for, session
#from content_management import content
from dbconnect import connection
import numpy as np
import pandas as pd
import datetime
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc
import scipy
import pygal

def getdefinition(screenname):
    c,conn=connection()
    c.execute("select definition from screens where screenname='"+screenname+"';")
    definition=np.array(c.fetchone())[0]
    return definition

def getrating(screenname):
    c,conn=connection()
    c.execute("select rating from screens where screenname='"+screenname+"';")
    rating=np.array(c.fetchone())[0]
    return rating

def getcmp(comp):
    c,conn=connection()
    c.execute("select Close from nse200_T where Comp_ID='"+comp+"' order by Date desc limit 1;")
    cmprice=np.array(c.fetchone())[0]
    return cmprice

def getpe(comp):
    c,conn=connection()
    procname = "latest_pe"
    args = [comp,3, 0.0]
    print(procname,args)
    output = c.callproc(procname, args)
    c.execute('select @_'+procname+'_0, @_'+procname+'_1,@_'+procname+'_2')
    temp = c.fetchall()[0]
    ans = temp[2]
    return ans

def getroe(comp):
    c,conn=connection()
    procname = "roe"
    args = [comp,3, 0.0]
    print(procname,args)
    output = c.callproc(procname, args)
    c.execute('select @_'+procname+'_0, @_'+procname+'_1,@_'+procname+'_2')
    temp = c.fetchall()[0]
    ans = temp[2]
    return ans

def screen(chunk):
    c,conn=connection()
    c.execute("select Comp_ID from nse200_F;")
    comp_names = np.array(c.fetchall())
    ans = []
    for comp in comp_names:
        try:
            spl=chunk[0].split("-")
            print(spl[1])
            procname=spl[0]
            args = [comp[0],spl[1], 0.0]
        except:
            procname =  chunk[0][:-1]
            args = [comp[0], int(chunk[0][-1]), 0.0]
            print(procname,args)
        output = c.callproc(procname, args)
        c.execute('select @_'+procname+'_0, @_'+procname+'_1, @_'+procname+'_2')
        temp = c.fetchall()[0]
        temp_1=temp[0].decode("UTF-8")
        if (eval(str(temp[2])+chunk[1]+chunk[2])):
            ans.append(temp_1)
        c.close()
        c = conn.cursor()
    return set(ans)

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

def screenfound(screenname):
    c,conn=connection()
    try:
        if session["logged_in"]==True:
            c.execute("select screenId from screens where screenname='"+screenname+"';")
            screenId=c.fetchone()[0]
            x=c.execute("select * from screenlist where userId="+str(session["userid"])+" and screenId ="+str(screenId)+";")
            if x>0:
                return True
            else:
                return False
    except:
        if session["logged_in"]==True:
            c.execute("select screenId from screens where screenname='"+screenname+"';")
            screenId=c.fetchone()[0]
            x=c.execute("select * from screenlist where userId="+str(session["userid"])+"and screenId="+str(screenId)+";")
            if x>0:
                return True
            else:
                return False
        return False
            

    
app.jinja_env.globals.update(compfound=compfound,getdefinition=getdefinition,getrating=getrating,getcmp=getcmp,getpe=getpe,getroe=getroe)
app.jinja_env.globals.update(screenfound=screenfound)

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

@app.route('/screensearchreasults/',methods=['GET','POST'])
def screensearchreasults(screenname):
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
    c.execute("select screenname,definition from nifty200 where screenname like '%"+screenname+"%';")
    screennames=np.array(c.fetchall())[:,0]
    definitions=np.array(c.fetchall())[:,1]
    return render_template("screensearchreasults.html",screennames=screennames,definitions=definitions)


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

@app.route('/createscreen/<query>',methods=['GET','POST'])
def createscreen(query):
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
        screenname=request.form["screenname"]
        description=request.form["description"]
        x=c.execute("select * from screens where screenname='"+str(screenname)+"';")
        if int(x)>0:
            flash("Screen name already taken")
            return redirect(url_for('createscreen',query=query))
        else:
            c.execute("insert into screens (creatorId,definition,screenname,rating) values("+str(session["userid"])+",'"+query+"','"+screenname+"',0);")
            conn.commit()
            return redirect(url_for('addtoscreenlist',screenname=screenname))

    return render_template("createscreen.html",query=query)

@app.route('/Technical/<comp>/',methods=['GET','POST'])
def Technical(comp):
    c,conn=connection()
    query = "SELECT * FROM nse200_F where Comp_ID='"+comp+"';"
    c.execute(query)
    data_F = c.fetchall()
    data_F=np.array(data_F)
    PL = ["Year", "Sales",	"Depr.",	"Int.",	"PBT","Tax", "NP", "Div_Amt"]
    PL_data=data_F[:,1:9]
    BS=[ "Year","Eq_Share_Cap", "Reserves","Borrowings", "Oth_Liab", "Net_Block", "CWIP",	"Inv", "Oth_Assets", "Rcvbles", "Inven.", "Cash","Eq_Shares"]
    BS_data=np.c_[data_F[:,1],data_F[:,9:]]

    if request.method=="POST":
        try:
            compx=request.form['search']
            c.execute("select compname from nifty200 where compname like '%"+compx+"%';")
            compnames=np.array(c.fetchall())[:,0]
            print(compnames)
            return render_template("searchreasults.html",compnames=compnames)
        except:
            pass
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
    return render_template("compdata.html",PL=PL,BS=BS,PL_data=PL_data,BS_data=BS_data,compname=compname,comp=comp,graph_data1m=graph_data1m,graph_data3m=graph_data3m,graph_data6m=graph_data6m,graph_data1y=graph_data1y,graph_data2y=graph_data2y,graph_datamax=graph_datamax)

@app.route('/screener/',methods=['GET','POST'])
def screener():
    return render_template("screen.html")

@app.route('/watchlist/',methods=['GET','POST'])
def watchlist():
    c,conn=connection()
    if request.method=="POST":
        try:
            compx=request.form['search']
            c.execute("select compname from nifty200 where compname like '%"+compx+"%';")
            compnames=np.array(c.fetchall())[:,0]
            print(compnames)
            return render_template("searchreasults.html",compnames=compnames)
        except:
            compx=request.form['search']
            c.execute("select compname from nifty200 where compname like '%"+compx+"%';")
            compnames=np.array(c.fetchall())[:,0]
            print(compnames)
            return render_template("searchreasults.html",compnames=compnames)
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

@app.route('/screenlist/',methods=['GET','POST'])
def screenlist():
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
            c.execute("select screenname from screens order by rating desc ")
            popularscreens=np.array(c.fetchall())[:,0]
            print(session["userid"])
            c.execute("select screenname from screens where screenId in (select screenId from screenlist where userId="+str(session["userid"])+");")
            try:
                userscreens=np.array(c.fetchall())[:,0]
            except:
                userscreens=[]
            print(userscreens)
            return render_template("screenlist.html",popularscreens=popularscreens,userscreens=userscreens)
    except:
        flash('Need to login first')
        return redirect(url_for("login"))
"""
@app.route('/screenlist/',methods=['GET','POST'])
def test():
    print('gg')
    pass
"""

@app.route('/addtowatchlist/<comp>/',methods=['GET','POST'])
def addtowatchlist(comp):
    c,conn=connection()
    try:
        if session["logged_in"]==True:
            c.execute("select compId from nifty200 where compname='"+comp+"';")
            compId=c.fetchone()[0]
            c.execute("select uid from users where username='"+session['username']+"';")
            userId=c.fetchone()[0]
            c.execute("insert into watchlist (compId,userId) values("+str(compId)+","+str(userId)+");")
            conn.commit()
            flash("added to watchlist")
            return redirect(url_for("Technical",comp=comp))
    except:
        flash('Need to login first')
        return redirect(url_for("login"))

@app.route('/addtoscreenlist/<screenname>/',methods=['GET','POST'])
def addtoscreenlist(screenname):
    c,conn=connection()
    if session["logged_in"]==True:
        c.execute("select screenId from screens where screenname='"+screenname+"';")
        screenId=c.fetchone()[0]
        c.execute("select uid from users where username='"+session['username']+"';")
        userId=c.fetchone()[0]
        c.execute("insert into screenlist (screenId,userId) values("+str(screenId)+","+str(userId)+");")
        conn.commit()
        c.execute("select rating from screens where screenname='"+screenname+"';")
        rating=np.array(c.fetchone())[0]
        rating+=1
        c.execute("update screens set rating="+str(rating)+" where screenname='"+screenname+"';")
        conn.commit()
        flash("added to screenlist")
        return redirect(url_for('existingscreenreasults',screenname=screenname))

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

@app.route('/removefromscreenlist/<screenname>/',methods=['GET','POST'])
def removefromscreenlist(screenname):
    c,conn=connection()
    if session["logged_in"]==True:
        c.execute("select screenId from screens where screenname='"+screenname+"';")
        screenId=c.fetchone()[0]
        c.execute("select uid from users where username='"+session['username']+"';")
        userId=c.fetchone()[0]
        c.execute("delete from screenlist where screenId="+str(screenId)+" and userId = "+str(userId)+";")
        conn.commit()
        c.execute("select rating from screens where screenname='"+screenname+"';")
        rating=np.array(c.fetchone())[0]
        rating-=1
        c.execute("update screens set rating="+str(rating)+" where screenname='"+screenname+"';")
        conn.commit()
        flash("deleted from screenlist")
        return redirect(url_for("existingscreenreasults",screenname=screenname))


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
    try:
        if session["logged_in"]==True:
            pass
    except:
        flash('Need to login first')
        return redirect(url_for("login"))
    
    if request.method == "POST":
        try:
            QUERY = request.form["writescreen"]
            dfs = []
            CHUNKS = QUERY.split("AND")
            for chunk in CHUNKS:
                chunk = chunk.lstrip()
                chunk = chunk.split(" ")
                dfs.append(screen(chunk))
            output=dfs[0]
            for q in dfs:
                output=set.intersection(q,output)
            print(output)
            #return redirect(url_for("screenreasults",compnames=output,query=QUERY))
            return render_template("screenreasults.html",compnames=output,query=QUERY)
        except:
            screenname = request.form["existingscreens"]
            print(screenname)
            c.execute("select screenname from screens where screenname like '%"+str(screenname)+"%';")
            try:
                screens=np.array(c.fetchall())[:,0]
            except:
                screens=[]
            #return redirect(url_for("screenreasults",compnames=output,query=QUERY))
            return render_template("searchreasultsscreens.html",screens=screens,screenname=screenname)

    else:
        return render_template("screens.html")


@app.route('/existingscreenreasults/<screenname>/',methods=['GET','POST'])
def existingscreenreasults(screenname):
    c,conn=connection()
    c.execute("select definition from screens where screenname='"+screenname+"';")
    QUERY=np.array(c.fetchone())[0]
    dfs = []
    CHUNKS = QUERY.split("AND")
    for chunk in CHUNKS:
        chunk = chunk.lstrip()
        chunk = chunk.split(" ")
        dfs.append(screen(chunk))
    output=dfs[0]
    for q in dfs:
        output=set.intersection(q,output)
    print(output)
    #return redirect(url_for("screenreasults",compnames=output,query=QUERY))
    return render_template("existingscreenreasults.html",compnames=output,screenname=screenname,QUERY=QUERY)

@app.route('/screenreasults/',methods=['GET','POST'])
def screenreasults(compnames,query):
    return render_template("screenreasults.html",compnames=output,query=QUERY)



if __name__ == "__main__":
    app.secret_key = 'randshit'
    app.run()
