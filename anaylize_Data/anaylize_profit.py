import os 
import pandas as pd 
import numpy as np 
from tqdm import tqdm




def next_transaction(cur_matchPri ,bidPri1 ,askPri1,tick_gap):
    # 成交在買 , 上漲 , 下筆要賣
    if cur_matchPri == bidPri1:
        return 0 , cur_matchPri + tick_gap
    # 成交在賣 , 下跌 , 下筆要買
    elif cur_matchPri == askPri1:
        return 1 , cur_matchPri - tick_gap
    else :
        return -1 , -1




filepath = "./stock_dataset"
simulation_day = 1
symbols_list = os.listdir(filepath)
tick_gap = 0.5 

fee =0 
tax =0
# 手續費
# fee = 0.001425
# 稅金
# tax = 0.003
# 起始資產
capital = 10000
# 持股
hold_stock = 0
Date = "20221107.csv"

for symbol  in symbols_list:
    symbol ="2330"
    symbol_path = os.path.join(filepath,symbol)
    dates_list = os.listdir(symbol_path)
    # 排序 .csv 之前的名稱
    dates_list.sort(key=lambda x:int(x[:-4]))
    
    # -1 : 不操作 , 0 : 賣 , 1:買
    transaction = -1 
    want_price = -1
    
    for date in dates_list :
        date = Date
        data = pd.read_csv(os.path.join(symbol_path,date))
        loop = tqdm(range(len(data)-1))
        loop.set_description(f"{date}")
        for i in loop:
            cur_matchPri = data.iloc[i,2]
            next_price = data.iloc[i+1,2]

            if want_price == cur_matchPri:
                # 這筆要買
                if transaction == 1 :
                    # 增加量
                    new_hold = capital/cur_matchPri
                    # 計算費用
                    pay = new_hold * cur_matchPri
                    # 考慮手續費時用
                    if (pay+ pay*fee) > capital:
                        if pay != 0 :
                            while (pay+ pay*fee ) > capital:
                                new_hold -=1 
                                pay = new_hold * cur_matchPri
                        else :
                            transaction , want_price= next_transaction(cur_matchPri=cur_matchPri , bidPri1=data.iloc[i,6] ,askPri1=data.iloc[i,16] ,tick_gap= tick_gap)
                            # 買不了就下一個
                            continue 
                    # 扣錢
                    capital -= pay+ pay*fee
                    # 加上去總持有
                    hold_stock += new_hold
                    #print(f"成交價: {cur_matchPri} ,買 {new_hold}股 , capital become -> {capital} ,hold_stock -> {hold_stock}")
                
                # 這筆要賣 
                elif transaction == 0 :
                    
                    # 計算賣出後獲利
                    gain = hold_stock * cur_matchPri
                    # 考慮手續費時用
                    gain = gain - gain*fee - gain*tax
                    # 資金增加
                    
                    capital += gain
                
                    #print(f"成交價: {cur_matchPri} ,賣 {hold_stock}股 , capital become -> {capital} ,hold_stock become -> 0")
                    # 持有歸零
                    hold_stock = 0 

            transaction , want_price = next_transaction(cur_matchPri=cur_matchPri , bidPri1=data.iloc[i,6],askPri1=data.iloc[i,16],tick_gap=tick_gap)
        
        simulation_day -=1
        if not simulation_day:
            capital += cur_matchPri *hold_stock
            break
    if not simulation_day:break

print(f"final capital {capital}")