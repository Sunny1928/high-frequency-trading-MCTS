import os 
import pandas as pd 
import numpy as np 
from tqdm import tqdm


# 檔案位置處理
filepath = "./stock_dataset"
day = 59
# tick = 474457 
symbols_list = os.listdir(filepath)

for symbol  in symbols_list:
    symbol = "2330"
    
    symbol_path = os.path.join(filepath,symbol)
    dates_list = os.listdir(symbol_path)
    # 排序 .csv 之前的名稱
    dates_list.sort(key=lambda x:int(x[:-4]))
    
    # 建立計算數量的list 
    # 買1的變化(上漲、平盤、下跌) 配 賣1的變化(上漲、平盤、下跌)，對應下筆成交價上漲、平盤、下跌 , 3 * 3 * 3 = 27個
    prob = list()
    for _ in range(99):
        # [上漲、平盤、下跌]
        prob.append([0,0,0])

    # 目前這筆 買1 和 賣1 的價差
    gap = 1

    match_bid = [0,0,0]
    match_ask = [0,0,0]

    for date in dates_list :

        data = pd.read_csv(os.path.join(symbol_path,date))
        loop = tqdm(range(len(data)-1))
        loop.set_description(f"Stock :{symbol} , Date : {date}")


        for i in loop:

    

            if data.iloc[i]["bidPri1"] == data.iloc[i]["matchPri"]:

                if data.iloc[i+1]["matchPri"] > data.iloc[i]["matchPri"]:
                    match_bid[2]+=1
                elif data.iloc[i+1]["matchPri"] == data.iloc[i]["matchPri"]:
                    match_bid[1]+=1
                elif data.iloc[i+1]["matchPri"] < data.iloc[i]["matchPri"]:
                    match_bid[0]+=1

            elif data.iloc[i]["askPri1"] == data.iloc[i]["matchPri"]:

                if data.iloc[i+1]["matchPri"] > data.iloc[i]["matchPri"]:
                    match_ask[2]+=1
                elif data.iloc[i+1]["matchPri"] == data.iloc[i]["matchPri"]:
                    match_ask[1]+=1
                elif data.iloc[i+1]["matchPri"] < data.iloc[i]["matchPri"]:
                    match_ask[0]+=1

        day -=1
        if not day :break
    if not day :break

state = ["down","sta","up"]
for i in range(3):
    print("bid {}: {:%} , {}".format(state[i],match_bid[i]/sum(match_bid),match_bid[i]))

print()
for i in range(3):
    print("ask {}: {:%} , {}".format(state[i],match_ask[i]/sum(match_ask),match_ask[i]))