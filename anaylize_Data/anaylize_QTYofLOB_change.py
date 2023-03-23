import os 
import pandas as pd
import numpy as np
from tqdm import tqdm

# 判斷成交價的變化 , num : prob的idx ,prob :機率list
def Count(next_matchPri,cur_matchPri,num,prob):
    # 下一筆上漲
    if next_matchPri > cur_matchPri:
        prob[num][0]+=1
    # 下一筆平盤
    elif next_matchPri == cur_matchPri:
        prob[num][1]+=1
    # 下一筆下跌
    elif next_matchPri < cur_matchPri:
        prob[num][2]+=1


# 處理除以0
def div(x, y):
    try:
        return x/y
    except:
        return 0.0
    

# 檔案位置處理
filepath = "./stock_dataset"
day = 59
tick = 474457 
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

    for date in dates_list :

        data = pd.read_csv(os.path.join(symbol_path,date))
        loop = tqdm(range(len(data)-1))
        loop.set_description(f"Stock :{symbol} , Date : {date}")
        
        for i in loop:
            # 判斷 gap         
            if ((data.iloc[i]["askPri1"] - data.iloc[i]["bidPri1"]) == gap):
                
                # 如果是 目前成交價 = 買1
                if data.iloc[i]["bidPri1"] == data.iloc[i]["matchPri"]:
                    padding = 0
                # 如果是 目前成交價 = 賣1
                elif data.iloc[i]["askPri1"] == data.iloc[i]["matchPri"]:
                    padding = 9
                # 如果是 目前成交價 = 中間價
                elif data.iloc[i]["askPri1"] > data.iloc[i]["matchPri"]  and data.iloc[i]["matchPri"] > data.iloc[i]["bidPri1"]:
                    padding = 18
                # 如果是 目前成交價 = 買2
                elif data.iloc[i]["bidPri2"] == data.iloc[i]["matchPri"]:
                    padding = 27
                # 如果是 目前成交價 = 賣2
                elif data.iloc[i]["askPri2"] == data.iloc[i]["matchPri"]:
                    padding = 36
                # 如果是 目前成交價 = 買3
                elif data.iloc[i]["bidPri3"] == data.iloc[i]["matchPri"]:
                    padding = 45
                # 如果是 目前成交價 = 賣3
                elif data.iloc[i]["askPri3"] == data.iloc[i]["matchPri"]:
                    padding = 54
                # 如果是 目前成交價 = 買4
                elif data.iloc[i]["bidPri4"] == data.iloc[i]["matchPri"]:
                    padding = 63
                # 如果是 目前成交價 = 賣4
                elif data.iloc[i]["askPri4"] == data.iloc[i]["matchPri"]:
                    padding = 72
                # 如果是 目前成交價 = 買5
                elif data.iloc[i]["bidPri5"] == data.iloc[i]["matchPri"]:
                    padding = 81
                # 如果是 目前成交價 = 賣5
                elif data.iloc[i]["askPri5"] == data.iloc[i]["matchPri"]:
                    padding = 90
                # 其他的不考慮
                else :
                    continue
                
                # 下筆 買1上漲 , 賣1上漲
                if data.iloc[i+1]["bidPri1"] > data.iloc[i]["bidPri1"] and  data.iloc[i+1]["askPri1"] > data.iloc[i]["askPri1"]:
                    Count(data.iloc[i+1]["matchPri"],data.iloc[i]["matchPri"],0+padding,prob)

                # 下筆 買1上漲 , 賣1不變
                elif data.iloc[i+1]["bidPri1"] > data.iloc[i]["bidPri1"] and  data.iloc[i+1]["askPri1"] == data.iloc[i]["askPri1"]:
                    Count(data.iloc[i+1]["matchPri"],data.iloc[i]["matchPri"],1+padding,prob)

                # 下筆 買1上漲 , 賣1下跌
                elif data.iloc[i+1]["bidPri1"] > data.iloc[i]["bidPri1"] and  data.iloc[i+1]["askPri1"] < data.iloc[i]["askPri1"]:
                    Count(data.iloc[i+1]["matchPri"],data.iloc[i]["matchPri"],2+padding,prob)
                
                # 下筆 買1不變 , 賣1上漲
                elif data.iloc[i+1]["bidPri1"] == data.iloc[i]["bidPri1"] and  data.iloc[i+1]["askPri1"] > data.iloc[i]["askPri1"]:
                    Count(data.iloc[i+1]["matchPri"],data.iloc[i]["matchPri"],3+padding,prob)
                
                # 下筆 買1不變 , 賣1不變
                elif data.iloc[i+1]["bidPri1"] == data.iloc[i]["bidPri1"] and  data.iloc[i+1]["askPri1"] == data.iloc[i]["askPri1"]:
                    Count(data.iloc[i+1]["matchPri"],data.iloc[i]["matchPri"],4+padding,prob)
                
                # 下筆 買1不變 , 賣1下跌
                elif data.iloc[i+1]["bidPri1"] == data.iloc[i]["bidPri1"] and  data.iloc[i+1]["askPri1"] < data.iloc[i]["askPri1"]:
                    Count(data.iloc[i+1]["matchPri"],data.iloc[i]["matchPri"],5+padding,prob)
                
                # 下筆 買1下跌 , 賣1上漲
                elif data.iloc[i+1]["bidPri1"] < data.iloc[i]["bidPri1"] and  data.iloc[i+1]["askPri1"] > data.iloc[i]["askPri1"]:
                    Count(data.iloc[i+1]["matchPri"],data.iloc[i]["matchPri"],6+padding,prob)
                
                # 下筆 買1下跌 , 賣1不變
                elif data.iloc[i+1]["bidPri1"] < data.iloc[i]["bidPri1"] and  data.iloc[i+1]["askPri1"] == data.iloc[i]["askPri1"]:    
                    Count(data.iloc[i+1]["matchPri"],data.iloc[i]["matchPri"],7+padding,prob)
                
                # 下筆 買1下跌 , 賣1下跌
                elif data.iloc[i+1]["bidPri1"] < data.iloc[i]["bidPri1"] and  data.iloc[i+1]["askPri1"] < data.iloc[i]["askPri1"]:
                    
                    Count(data.iloc[i+1]["matchPri"],data.iloc[i]["matchPri"],8+padding,prob)
            tick-=1
            if not tick : break
        # 計算天數
        
        #day -=1
        #if not day : break
        if not tick : break
    break



# 輸出
print(f"tick 相差 {gap}")
item = ["bid1","ask1","中間價","bid2","ask2","bid3","ask3","bid4","ask4","bid5","ask5"]
print(len(prob))
for i in range(len(item)):
    total = sum([sum(prob[j+9*i])  for j in range(0,9)])
    print(f"\n目前這筆的 成交價是 目前這筆的 {item[i]} 時")
    print('bid1 下一筆變成 up   ,ask1 下一筆變成 up   : {:.4f} ,下一筆成交價上漲: {:.4f} , 平盤: {:.4f} ,下跌: {:.4f}'.format(
        div(sum(prob[0+9*i]),total),div(prob[0+9*i][0],sum(prob[0+9*i])),div(prob[0+9*i][1],sum(prob[0+9*i])),div(prob[0+9*i][2],sum(prob[0+9*i]))))
    print('bid1 下一筆變成 up   ,ask1 下一筆變成 平   : {:.4f} ,下一筆成交價上漲: {:.4f} , 平盤: {:.4f} ,下跌: {:.4f}'.format(
        div(sum(prob[1+9*i]),total),div(prob[1+9*i][0],sum(prob[1+9*i])),div(prob[1+9*i][1],sum(prob[1+9*i])),div(prob[1+9*i][2],sum(prob[1+9*i]))))
    print('bid1 下一筆變成 up   ,ask1 下一筆變成 down : {:.4f} ,下一筆成交價上漲: {:.4f} , 平盤: {:.4f} ,下跌: {:.4f}'.format(
        div(sum(prob[2+9*i]),total),div(prob[2+9*i][0],sum(prob[2+9*i])),div(prob[2+9*i][1],sum(prob[2+9*i])),div(prob[2+9*i][2],sum(prob[2+9*i]))))
    print('bid1 下一筆變成 平   ,ask1 下一筆變成 up   : {:.4f} ,下一筆成交價上漲: {:.4f} , 平盤: {:.4f} ,下跌: {:.4f}'.format(
        div(sum(prob[3+9*i]),total),div(prob[3+9*i][0],sum(prob[3+9*i])),div(prob[3+9*i][1],sum(prob[3+9*i])),div(prob[3+9*i][2],sum(prob[3+9*i]))))
    print('bid1 下一筆變成 平   ,ask1 下一筆變成 平   : {:.4f} ,下一筆成交價上漲: {:.4f} , 平盤: {:.4f} ,下跌: {:.4f}'.format(
        div(sum(prob[4+9*i]),total),div(prob[4+9*i][0],sum(prob[4+9*i])),div(prob[4+9*i][1],sum(prob[4+9*i])),div(prob[4+9*i][2],sum(prob[4+9*i]))))
    print('bid1 下一筆變成 平   ,ask1 下一筆變成 down : {:.4f} ,下一筆成交價上漲: {:.4f} , 平盤: {:.4f} ,下跌: {:.4f}'.format(
        div(sum(prob[5+9*i]),total),div(prob[5+9*i][0],sum(prob[5+9*i])),div(prob[5+9*i][1],sum(prob[5+9*i])),div(prob[5+9*i][2],sum(prob[5+9*i]))))
    print('bid1 下一筆變成 down ,ask1 下一筆變成 up   : {:.4f} ,下一筆成交價上漲: {:.4f} , 平盤: {:.4f} ,下跌: {:.4f}'.format(
        div(sum(prob[6+9*i]),total),div(prob[6+9*i][0],sum(prob[6+9*i])),div(prob[6+9*i][1],sum(prob[6+9*i])),div(prob[6+9*i][2],sum(prob[6+9*i]))))
    print('bid1 下一筆變成 down ,ask1 下一筆變成 平   : {:.4f} ,下一筆成交價上漲: {:.4f} , 平盤: {:.4f} ,下跌: {:.4f}'.format(
        div(sum(prob[7+9*i]),total),div(prob[7+9*i][0],sum(prob[7+9*i])),div(prob[7+9*i][1],sum(prob[7+9*i])),div(prob[7+9*i][2],sum(prob[7+9*i]))))
    print('bid1 下一筆變成 down ,ask1 下一筆變成 down : {:.4f} ,下一筆成交價上漲: {:.4f} , 平盤: {:.4f} ,下跌: {:.4f}'.format(
        div(sum(prob[8+9*i]),total),div(prob[8+9*i][0],sum(prob[8+9*i])),div(prob[8+9*i][1],sum(prob[8+9*i])),div(prob[8+9*i][2],sum(prob[8+9*i]))))

