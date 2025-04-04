import requests as rq
import time
import numpy as np
from datetime import datetime
from json import loads

header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Connection': 'keep-alive',
        }

def pchange(old, new):
    return (new - old) / old

def convert_to_unix_timestamp(date_str=None):
    try:
        if date_str is None:
            # If date_str is null, use today's date
            date_obj = datetime.today()
        else:
            # Parse the date string into a datetime object
            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
        # Convert the datetime object to a Unix timestamp
        unix_timestamp = int(time.mktime(date_obj.timetuple()))
        return unix_timestamp
    except ValueError as e:
        raise ValueError(f"Invalid date string: {date_str}") from e
    
def ts2date(timestamp):
    # Convert the timestamp to a datetime object
    dt_object = datetime.fromtimestamp(timestamp)
    # Format the datetime object to the desired format
    formatted_date = dt_object.strftime('%d %b %Y')
    return formatted_date

p1 = convert_to_unix_timestamp("1/1/2011") + 86400
p2 = convert_to_unix_timestamp("31/12/2025")
resp = rq.get(f"PASTE YAHOO FINANCE API (V8) ENDPOINT HERE, param: {stock code}?period1={p1}&period2={p2}&interval=1mo&indicators=quote&includeTimestamps=true", headers=header)
dat = loads(resp.text)
txn = dat['chart']['result'][0]['indicators']['quote'][0]
opens = list(txn['open']) #open prices of i-th day
lows = list(txn['low']) #low prices of i-th day
cloeses = list(txn['close'])
ts = list(dat['chart']['result'][0]['timestamp']) #timestamp of i-th day


cur_open_p = None
cur_low_p = None
bullish = []
for i in range(len(opens)):
    open_price = opens[i]
    low_price = lows[i]
    timestamp = ts[i]
    date = datetime.fromtimestamp(timestamp)
    if cur_low_p:
        cur_low_p = min(cur_low_p, low_price)
    else: cur_low_p = low_price

    if date.month == 1:
        cur_open_p = open_price
    if date.month == 12 or i == len(opens) - 1:
        print(f'As of: {date} Open price: {round(cur_open_p, 2)} Low price: {round(cur_low_p, 2)} Rate: {round(pchange(cur_open_p, cur_low_p) * 100, 2)}%')
        if cur_open_p <= cloeses[i]:
            bullish.append(round(pchange(cur_open_p, cur_low_p) * 100, 2))
        cur_open_p = None
        cur_low_p = None

min_chg = np.min(bullish)
max_chg = np.max(bullish)
norm_bullish = []
for i in range(len(bullish)):
    if min_chg != None and bullish[i] == min_chg:
        print(f'Filtered one anomaly: {bullish[i]}')
        min_chg = None
        continue

    if max_chg != None and bullish[i] == max_chg:
        print(f'Filtered one anomaly: {bullish[i]}')
        max_chg = None
        continue

    norm_bullish.append(bullish[i])

min_after_norm = np.min(norm_bullish)
mean_after_norm = np.mean(norm_bullish)
print(f'Summary of {len(norm_bullish)} BULLish years -> Norm. minimum loss to average: {round(min_after_norm, 1)}%/{round(mean_after_norm, 1)}%, Suggested SL: {round((min_after_norm + mean_after_norm)/2, 2)}%')
