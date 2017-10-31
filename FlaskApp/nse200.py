import dbconnect
import pandas as pd

c,conn=dbconnect.connection()
NSE=pd.read_csv('nifty200.csv')
compid=NSE['Symbol'].values
company=NSE['Company Name'].values
for i in range(len(compid)):
    c.execute('INSERT INTO nse200 (Comp_ID,Company) values("%s","%s");'%(compid[i],company[i]))
    conn.commit()
