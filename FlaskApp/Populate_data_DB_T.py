import dbconnect
import pandas as pd

c,conn=dbconnect.connection()
NSE=pd.read_csv('nifty200.csv')['Symbol'][159:].values
for comp in NSE:
    comp_data=pd.read_csv('../../data/'+comp+'.csv') 
    for index,row in comp_data.iterrows():
        try:
            print(comp)
            c.execute("INSERT INTO nse200_T (Comp_ID,Date,Open,High,Low,Last,Close,Qty,TurnOver) values('%s','%s',%s,%s,%s,%s,%s,%s,%s);"%(comp,row['Date'],row['Open'],row['High'],row['Low'],row['Last'],row['Close'],row['Total Trade Quantity'],row['Turnover (Lacs)']))
            conn.commit()
        except:
            pass
