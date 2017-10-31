import dbconnect
import pandas as pd
from datetime import datetime
COMP_NAMES = 'ind_nifty200list.csv'
SQL_NAME = 'nifty200.csv'
DATA = '../../Stock_Screener_Data/Fundamental_Data/'
c,conn=dbconnect.connection()
NSE=pd.read_csv(COMP_NAMES)['Symbol'].values
NSE1 = pd.read_csv(SQL_NAME)['Symbol'].values
for comp, comp1 in zip(NSE, NSE1):
    if comp == "CONCOR":
        continue
    comp_data = pd.read_csv(DATA+comp+'.csv')
    comp_data.fillna(0, inplace = True)
    print(comp)
    # print(comp_data)

    # comp_data_path = DATA+comp+'.csv'
    # print(comp)
    # c.execute("LOAD DATA LOCAL INFILE '%s' INTO TABLE nifty200_F FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\r\n' IGNORE 1 LINES;"%(comp_data_path))
    # conn.commit()
    for index,row in comp_data.iterrows():
        try:
            row.ix[0] = datetime.strptime(row.ix[0,0], "%d-%m-%Y").strftime("%Y-%m-%d")
        except:
            pass
        c.execute("INSERT INTO nse200_F values('%s','%s',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);" %(comp1, row.ix[0], row.ix[1], row.ix[2], row.ix[3], row.ix[4], row.ix[5], row.ix[6], row.ix[7], row.ix[8], row.ix[9], row.ix[10], row.ix[11], row.ix[12], row.ix[13], row.ix[14], row.ix[15], row.ix[16], row.ix[17], row.ix[18], row.ix[19]))
        print(row.ix[0])
            # # c.execute("INSERT INTO nse200_F values('%s','%s',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);" %(comp1, row.ix[0,0], row['Sales'], row['Depreciation'], row['Interest'], row['Profit_before_tax'], row['Tax'], row['Net_profit'], row['Dividend_Amount'], row['Equity_Share_Capital'], row['Reserves'], row['Borrowings'], row['Other_Liabilities'], row['Net_Block'], row['Capital_Work_in_Progress'], row['Investments'], row['Other_Assets'], row['Receivables'], row['Inventory'], row['Cash_and_Bank'], row['No_of_Equity_Shares']))
            # # conn.commit()
            # c.execute("INSERT INTO nse200_F values('%s','%s',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);" %(comp1, row.ix[0], row.ix[1], row.ix[2], row.ix[3], row.ix[4], row.ix[5], row.ix[6], row.ix[7], row.ix[8], row.ix[9], row.ix[10], row.ix[11], row.ix[12], row.ix[13], row.ix[14], row.ix[15], row.ix[16], row.ix[17], row.ix[18], row.ix[19]))
            # # print("NO")
            # pass
        conn.commit()
