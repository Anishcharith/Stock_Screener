import dbconnect
import pandas as pd

# COMP_NAMES = 'nifty200.csv'
c,conn=dbconnect.connection()
# NSE=pd.read_csv(COMP_NAMES)['Symbol'].values
# for comp in NSE:
c.execute("DROP TABLE IF EXISTS nse200_F;")
c.execute("CREATE TABLE nse200_F (Comp_ID varchar(20), Year DATE, Sales FLOAT, Depreciation FLOAT, Interest FLOAT, Profit_before_tax FLOAT, Tax FLOAT, Net_profit FLOAT, Dividend_Amount FLOAT, Equity_Share_Capital FLOAT, Reserves FLOAT, Borrowings FLOAT, Other_Liabilities FLOAT, Net_Block FLOAT, Capital_Work_in_Progress FLOAT, Investments FLOAT, Other_Assets FLOAT, Receivables FLOAT, Inventory FLOAT, Cash_and_Bank FLOAT, No_of_Equity_Shares DOUBLE, primary key(Comp_ID, Year));")
    # c.execute("DROP TABLE %s_F;"%str(comp))
