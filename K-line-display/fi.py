import pandas_datareader.data as web
import pandas as pd
import datetime
import csv
import json
import sys
start = datetime.datetime(2017, 1, 1)
end = datetime.datetime(2017, 1, 9)
f = web.DataReader('XOM', 'yahoo', start, end)
data = []
for i, row in f.iterrows():
    # print(i,row)
    data.append([int(i.date().strftime("%s"))*1000, row['Open'], row['High'],row['Low'],row['Close'],row['Volume']])
j = json.dumps(data)
print(j)
