import pandas_datareader.data as web
import pandas as pd
import datetime
import csv
import json
import sys
symbol = sys.argv[1]
start = datetime.datetime(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
end = datetime.datetime(int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7]))
f = web.DataReader(symbol, 'yahoo', start, end)
data = []
for i, row in f.iterrows():
    data.append([int(i.date().strftime("%s"))*1000, row['Open'], row['High'],row['Low'],row['Close'],row['Volume']])
j = json.dumps(data)
print(j)
