from collections import namedtuple, defaultdict
import random
from mcts import MCTS, Node
import pandas as pd

_FB = namedtuple("FinBoard", "allbidask bidask tick terminal buy_or_sell now_invest")

FILE_NAME = './2330/20221202.csv'
ROLLOUT_TIMES = 10
END_TICK = 5 # simulation until END_TICK
TICK_PRICE_GAP = 0.5


ORIGINAL_INVEST = 10000
PROB_LIST = [
    [
        [  # happen  up      up+down
            [0.0019, 0.9978, 0.9978],
            [0.0028, 0.9761, 0.9761],
            [0.9813, 0.3541, 0.3544],
            [0.9879, 0.0120, 0.0816], 
            [1.0000, 0.0034, 0.398] 
        ],
        [   
            [0.0108, 0.0551, 0.0588],
            [0.0142, 0.1318, 0.1382],
            [0.9968, 0.0004, 0.3158],
            [0.9979, 0, 0.9699],
            [1.0000, 0, 0.9982]
        ],
        [
            [0, 0, 0],
            [0.0030, 1, 1],
            [0.6906, 0.9934, 0.9934],
            [0.1357, 0.8876, 0.8876],
            [0.1707, 0.9107, 0.9107],
        ],
        [   
            [0.1570, 0, 0.9189],
            [0.1146, 0, 0.8272],
            [0.7256, 0, 0.9922],
            [0.0014, 0, 1],
            [0.0014, 0, 1],
        ],
        [
            [0, 0, 0],
            [0, 0, 0],
            [1, 1, 1],
            [0, 0, 0],
            [0, 0, 0],
        ],
        [   
            [0, 0, 0],
            [0, 0, 0],
            [1, 0, 1],
            [0, 0, 0],
            [0, 0, 0],
        ]
    ],
    [
        [
            [0.0005, 1, 1],
            [0.0427, 0.4542, 0.4542],
            [0.9496, 0.0004, 0.0004],
            [0.9925, 0.3725, 0.3725],
            [1.0000, 0.0222, 0.0444]
        ],
        [
            [0.0062, 0.0909, 0.0909],
            [0.0753, 0.0028, 0.2992],
            [0.9505, 0.0009, 0.3998],
            [0.9982, 0.0040, 0.3855],
            [1.0000, 0, 1]
        ],
        [
            [0.0030, 1, 1],
            [0.3150, 0.5824, 0.9998],
            [0.6891, 0.5368, 1],
            [0.9957, 0.4485, 0.9941],
            [1.0000, 0, 1]
        ],
        [
            [0, 0, 0],
            [0, 0, 0],
            [0.7273, 1, 1],
            [0.0909, 1, 1],
            [0.1818, 0.5, 0.5]
        ],
        [
            [0.1667, 0, 1],
            [0.1111, 0, 1],
            [0.7223, 0, 1],
            [0, 0, 0],
            [0, 0, 0]
        ],
    ]
]
TICK_QTY_TIMES_MORE = 1.5 # variable for qty to becomes more
TICK_QTY_TIMES_LESS = 0.5 # variable for qty to becomes less
BID_OP_INDEX = 19 # match price of first bidask at bid in allbidask index
ASK_OP_INDEX = 20 # match price of first bidask at ask in allbidask index
MATCH_PRICE_CHANGE = 0.8 # match price chance probility


class FinBoard(_FB, Node):
    
    # expend
    def find_children(self):
        
        if self.terminal:
            return set()
        
        # transacted, not transacted
        action = (None, None) 

        return {
            # run all the nodes including transacted and not transacted
            self.make_move(i) for i, value in enumerate(action) if value is None
        }
    
    # random choose a node
    def find_random_child(self): 
        
        if self.terminal:
            return None
        
        # random choose a node (transacted and not transacted)
        return self.make_move(random.randint(0,1))
    
    def reward(self):
        
        if not self.terminal:
            raise RuntimeError(f"reward called on nonterminal self {self}")
        
        # ROI
        profit = self.now_invest[0] + self.now_invest[1] * self.bidask[0]
        roi = profit/ORIGINAL_INVEST
        
        return roi
    
    def is_terminal(self):
        
        return self.terminal
    
    def make_move(self, transacted): 
        # transacted = 0, not transacted = 1
        # allbidask [oP,bQ1,aQ1,bQ2,aQ2...bQ10,aQ10...bQ20,aQ20)] P10 = oP
        #            0  1   2   3   4     19   20     39   40
        # bidask [mP,mQ,bP1,bP2...bQ1,bQ2...,aP1,aP2...aQ1,aQ2...]
        #          0  1  2         7          12        17       22

        allbidask = list(self.allbidask)
        bidask = list(self.bidask)
        now_invest = list(self.now_invest)
        buy_or_sell = self.buy_or_sell
        
        # gap between aP1 and bP1
        gap = (bidask[12]-bidask[2])/TICK_PRICE_GAP

        if gap == 1.0: # gap = 1 tick

            # match at bid1
            if bidask[0] == bidask[2]: 
                index = 0

            # match at ask1
            elif bidask[0] == bidask[12]: 
                index = 1

            # match at bid2
            elif bidask[0] == bidask[2] - TICK_PRICE_GAP: 
                index = 2

            # match at ask2
            elif bidask[0] == bidask[12] + TICK_PRICE_GAP: 
                index = 3

            # match at bid3
            elif bidask[0] == bidask[2] - 2*TICK_PRICE_GAP: 
                index = 4

            # match at ask3
            elif bidask[0] == bidask[12] + 2*TICK_PRICE_GAP: 
                index = 5
                

            rand = round(random.random(), 4)
            rand_next_price = round(random.random(), 4)

            # bid五檔 up, ask五檔 up
            if rand < PROB_LIST[0][index][0][0]: 
                allbidask, bidask = bid_price_up(allbidask, bidask)
                allbidask, bidask = ask_price_up(allbidask, bidask)

                # 下一筆成交價 up
                if rand_next_price < PROB_LIST[0][index][0][1]: 
                    bidask, now_invest, buy_or_sell = match_price_up(transacted, bidask, now_invest, buy_or_sell)

                # 下一筆成交價下跌 down
                elif rand_next_price < PROB_LIST[0][index][0][2]: 
                    bidask, now_invest, buy_or_sell = match_price_down(transacted, bidask, now_invest, buy_or_sell)

            # bid五檔 same, ask五檔 up
            elif rand < PROB_LIST[0][index][1][0]: 
                allbidask, bidask = bid_price_same(allbidask, bidask)
                allbidask, bidask = ask_price_up(allbidask, bidask)

                # 下一筆成交價 up
                if rand_next_price < PROB_LIST[0][index][1][1]: 
                    bidask, now_invest, buy_or_sell = match_price_up(transacted, bidask, now_invest, buy_or_sell)

                # 下一筆成交價 down
                elif rand_next_price < PROB_LIST[0][index][1][2]: 
                    bidask, now_invest, buy_or_sell = match_price_down(transacted, bidask, now_invest, buy_or_sell)

            # bid五檔 same, ask五檔 same
            elif rand < PROB_LIST[0][index][2][0]: 
                allbidask, bidask = bid_price_same(allbidask, bidask)
                allbidask, bidask = ask_price_same(allbidask, bidask)

                # 下一筆成交價 up
                if rand_next_price < PROB_LIST[0][index][2][1]: 
                    bidask, now_invest, buy_or_sell = match_price_up(transacted, bidask, now_invest, buy_or_sell)

                # 下一筆成交價 down
                elif rand_next_price < PROB_LIST[0][index][2][2]: 
                    bidask, now_invest, buy_or_sell = match_price_down(transacted, bidask, now_invest, buy_or_sell)

            # bid五檔 down, ask五檔 same
            elif rand < PROB_LIST[0][index][3][0]: 
                allbidask, bidask = bid_price_down(allbidask, bidask)
                allbidask, bidask = ask_price_same(allbidask, bidask)

                # 下一筆成交價 up
                if rand_next_price < PROB_LIST[0][index][3][1]: 
                    bidask, now_invest, buy_or_sell = match_price_up(transacted, bidask, now_invest, buy_or_sell)

                # 下一筆成交價 down
                elif rand_next_price < PROB_LIST[0][index][3][2]: 
                    bidask, now_invest, buy_or_sell = match_price_down(transacted, bidask, now_invest, buy_or_sell)
            
            # bid五檔 down, ask五檔 down
            elif rand < PROB_LIST[0][index][4][0]: 
                allbidask, bidask = bid_price_down(allbidask, bidask)
                allbidask, bidask = ask_price_down(allbidask, bidask)

                # 下一筆成交價 up
                if rand_next_price < PROB_LIST[0][index][4][1]: 
                    bidask, now_invest, buy_or_sell = match_price_up(transacted, bidask, now_invest, buy_or_sell)

                # 下一筆成交價 down
                elif rand_next_price < PROB_LIST[0][index][4][2]: 
                    bidask, now_invest, buy_or_sell = match_price_down(transacted, bidask, now_invest, buy_or_sell)


        # gap = 2 ticks 
        elif gap == 2.0: 

            # match at bid price
            if bidask[0] == bidask[2]:
                index = 0

            # match at ask price
            elif bidask[0] == bidask[12]: 
                index = 1
            
            # match at mid price
            elif bidask[0] == bidask[2]+TICK_PRICE_GAP: 
                index = 2

            # match at bid2
            elif bidask[0] == bidask[2] - TICK_PRICE_GAP: 
                index = 3

            # match at ask2
            elif bidask[0] == bidask[12] + TICK_PRICE_GAP: 
                index = 4


            rand = round(random.random(), 4)
            rand_next_price = round(random.random(), 4)

            # bid五檔 up, ask五檔 up
            if rand < PROB_LIST[1][index][0][0]: 
                allbidask, bidask = bid_price_up(allbidask, bidask)
                allbidask, bidask = ask_price_up(allbidask, bidask)

                # 下一筆成交價 up
                if rand_next_price < PROB_LIST[1][index][0][1]: 
                    bidask, now_invest, buy_or_sell = match_price_up(transacted, bidask, now_invest, buy_or_sell)

                # 下一筆成交價下跌 down
                elif rand_next_price < PROB_LIST[1][index][0][2]: 
                    bidask, now_invest, buy_or_sell = match_price_down(transacted, bidask, now_invest, buy_or_sell)

            # bid五檔 up, ask五檔 same
            elif rand < PROB_LIST[1][index][1][0]: 
                allbidask, bidask = bid_price_up(allbidask, bidask)
                allbidask, bidask = ask_price_same(allbidask, bidask)

                # 下一筆成交價 up
                if rand_next_price < PROB_LIST[1][index][1][1]: 
                    bidask, now_invest, buy_or_sell = match_price_up(transacted, bidask, now_invest, buy_or_sell)

                # 下一筆成交價 down
                elif rand_next_price < PROB_LIST[1][index][1][2]: 
                    bidask, now_invest, buy_or_sell = match_price_down(transacted, bidask, now_invest, buy_or_sell)

            # bid五檔 same, ask五檔 same
            elif rand < PROB_LIST[1][index][2][0]: 
                allbidask, bidask = bid_price_same(allbidask, bidask)
                allbidask, bidask = ask_price_same(allbidask, bidask)

                # 下一筆成交價 up
                if rand_next_price < PROB_LIST[1][index][2][1]: 
                    bidask, now_invest, buy_or_sell = match_price_up(transacted, bidask, now_invest, buy_or_sell)

                # 下一筆成交價 down
                elif rand_next_price < PROB_LIST[1][index][2][2]: 
                    bidask, now_invest, buy_or_sell = match_price_down(transacted, bidask, now_invest, buy_or_sell)

            # bid五檔 same, ask五檔 down
            elif rand < PROB_LIST[1][index][3][0]: 
                allbidask, bidask = bid_price_same(allbidask, bidask)
                allbidask, bidask = ask_price_down(allbidask, bidask)

                # 下一筆成交價 up
                if rand_next_price < PROB_LIST[1][index][3][1]: 
                    bidask, now_invest, buy_or_sell = match_price_up(transacted, bidask, now_invest, buy_or_sell)

                # 下一筆成交價 down
                elif rand_next_price < PROB_LIST[1][index][3][2]: 
                    bidask, now_invest, buy_or_sell = match_price_down(transacted, bidask, now_invest, buy_or_sell)
            
            # bid五檔 down, ask五檔 down
            elif rand < PROB_LIST[1][index][4][0]: 
                allbidask, bidask = bid_price_down(allbidask, bidask)
                allbidask, bidask = ask_price_down(allbidask, bidask)

                # 下一筆成交價 up
                if rand_next_price < PROB_LIST[1][index][4][1]: 
                    bidask, now_invest, buy_or_sell = match_price_up(transacted, bidask, now_invest, buy_or_sell)

                # 下一筆成交價 down
                elif rand_next_price < PROB_LIST[1][index][4][2]: 
                    bidask, now_invest, buy_or_sell = match_price_down(transacted, bidask, now_invest, buy_or_sell)




        # update all bidask
        allbidask = update_all_bidask(allbidask, bidask)

        # next tick
        tick = self.tick + 1
        
        # is it terminal
        is_terminal = tick is END_TICK
        
        return FinBoard(tuple(allbidask), tuple(bidask), tick, is_terminal, buy_or_sell, tuple(now_invest))
    


        
# update bidask qty        
def update_all_bidask(all_bidask, now_bidask):
    all_bidask = list(all_bidask)
    now_bidask = list(now_bidask)
    open_price = all_bidask[0]

    # update current bidask qty into all_bidask 
    # the price of the center of all_bidask(index = 19, 20) is the first match price
    # all_bidask  0 1 2 3 4 5 6 7 8 ... 19 20 ...
    #             b a b a b a b a b      b  a

    for i in range(2, 7):
        all_bidask[BID_OP_INDEX+int((now_bidask[i]-open_price)/TICK_PRICE_GAP)*2] = now_bidask[i+5] # bid
        all_bidask[ASK_OP_INDEX+int((now_bidask[i+10]-open_price)/TICK_PRICE_GAP)*2] = now_bidask[i+15] # ask
    
    all_bidask = tuple(all_bidask)
    return all_bidask

def bid_price_up(allbidask, bidask):
    # price
    bidask[3:7] = bidask[2:6]
    bidask[2] += TICK_PRICE_GAP
    
    # qty
    bidask[8:12] = bidask[7:11]
    bidask[7] = round(bidask[7] * TICK_QTY_TIMES_LESS)    
    
    return allbidask, bidask

def bid_price_down(allbidask, bidask):
    # print("Bid Price DOWN")
    open_price = allbidask[0]
    allbidask[BID_OP_INDEX+int((bidask[2]-open_price)/TICK_PRICE_GAP)*2] = 0 # bQ1 = 0
    
    # price
    bidask[2:6] = bidask[3:7]
    bidask[6] -= TICK_PRICE_GAP
    
    # qty
    bidask[7:11] = bidask[8:12]
    bQ5 = allbidask[BID_OP_INDEX+int((bidask[6]-open_price)/TICK_PRICE_GAP)*2]
    bidask[11] = bQ5 if bQ5 != 0 else round(bidask[11] * TICK_QTY_TIMES_MORE) 
    
    return allbidask, bidask

def bid_price_same(allbidask, bidask):
    # print("Bid Price SAME")
    
    # qty
    bidask[7] = round(bidask[7]*random.uniform(1.5, 0.5)) 
    
    return allbidask, bidask

def ask_price_up(allbidask, bidask):
    # print("Ask Price UP")
    open_price = allbidask[0]
    allbidask[ASK_OP_INDEX+int((bidask[12]-open_price)/TICK_PRICE_GAP)*2] = 0 # aQ1 = 0
    
    # price
    bidask[12:16] = bidask[13:17]
    bidask[16] += TICK_PRICE_GAP
    
    # qty
    bidask[17:21]= bidask[18:22]
    aQ5 = allbidask[ASK_OP_INDEX+int((bidask[16]-open_price)/TICK_PRICE_GAP)*2]
    bidask[21] = aQ5 if aQ5 != 0 else round(bidask[21] * TICK_QTY_TIMES_MORE)
    
    return allbidask, bidask

def ask_price_down(allbidask, bidask):
    # print("Ask Price DOWN")
    
    # price
    bidask[13:17] = bidask[12:16]
    bidask[12] -= TICK_PRICE_GAP
    
    # qty
    bidask[18:22]= bidask[17:21]
    bidask[17] = round(bidask[17] * TICK_QTY_TIMES_LESS)
    
    return allbidask, bidask

def ask_price_same(allbidask, bidask):
    # print("Ask Price SAME")
    bidask[17] = round(bidask[17]*random.uniform(1.5, 0.5))
    
    return allbidask, bidask

def match_price_up(move, bidask, now_invest, buy_or_sell):
    # print("Match Price UP")
    bidask[0] += TICK_PRICE_GAP # 上漲
    if move == 0 and buy_or_sell == 1: # 我方想賣都可以賣掉
        now_invest[0] = now_invest[1]*bidask[0]
        now_invest[1] = 0
        buy_or_sell ^= 1
    
    return bidask, now_invest, buy_or_sell

def match_price_down(move, bidask, now_invest, buy_or_sell):
    # print("Match Price DOWN")
    bidask[0] -= TICK_PRICE_GAP # 下跌
    
    if move == 0 and buy_or_sell == 0: # 我方想買都可以買到
        now_invest[1] = now_invest[0]/bidask[0]
        now_invest[0] = 0
        buy_or_sell ^= 1
    
    return bidask, now_invest, buy_or_sell


def play_game():
    # read file
    stock_data = pd.read_csv(FILE_NAME)
    stock_data = stock_data.drop(columns=['openPri','matchTime','matchDate', 'symbol', 'tolMatchQty','highPri','lowPri','refPri','upPri','dnPri','label'])
    stock_data = stock_data.to_records(index=False)

    tree = MCTS()

    index = 0

    # tick
    tick = 0

    # 現在的操作要買或是賣
    buy_or_sell = 0 # buy = 0, sell = 1
    
    # (現有的錢, 持股)
    now_invest = [ORIGINAL_INVEST, 0]

    while True:
        print("index: "+str(index))
        now_bidask = tuple(stock_data[index])
        # print(now_bidask)

        board = new_fin_board(now_bidask, tick, buy_or_sell, now_invest)

        for _ in range(ROLLOUT_TIMES):
            tree.do_rollout(board)

        tree._print_tree_children(board)

        board = tree.choose(board)
        print(board)
        


        # tick = board.tick  
        buy_or_sell = board.buy_or_sell 

        index += 1

        if index >= len(stock_data):
            print("最後持有：")
            if now_invest[1] == 0:
                print(now_invest[0])
            else:
                print(now_invest[1]*now_bidask[0])
            break

        # make move, buy or sell
        next_bidask = tuple(stock_data[index])
        if buy_or_sell != board.buy_or_sell:
            if buy_or_sell == 0 and next_bidask[0] == now_bidask[0]-TICK_PRICE_GAP: # buy
                now_invest[1] = now_invest[0]/(now_bidask[0]-TICK_PRICE_GAP)
                now_invest[0] = 0
            
            elif buy_or_sell == 1 and next_bidask[0] == now_bidask[0]+TICK_PRICE_GAP: # sell
                now_invest[0] = now_invest[1]*(now_bidask[0]+TICK_PRICE_GAP)
                now_invest[1] = 0

def new_fin_board(now_bidask, tick, buy_or_sell, now_invest):
    
    # 紀錄所有可能發生的買賣五檔數量
    allbidask = (now_bidask[0],)+(0,)*40
    allbidask = update_all_bidask(allbidask, now_bidask)
    
    # allbidask=所有的買賣五檔, bidask=現在的買賣五檔, tick=現在的tick量, terminal=結束, buy_or_sell=買或是賣, now_invest=現在的投資價格
    return FinBoard(allbidask=allbidask, bidask=now_bidask, tick=tick, terminal=False, buy_or_sell=buy_or_sell, now_invest=tuple(now_invest))

if __name__ == "__main__":
    play_game()

