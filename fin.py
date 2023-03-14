from collections import namedtuple, defaultdict
import random
from mcts import MCTS, Node

_FB = namedtuple("FinBoard", "allbidask bidask tick terminal buy_or_sell original_invest now_invest")

"""
one ticks:
    match bid price:
        probability of bidPri_up: 0.0000 , bidPri_down: 0.0090
        probability of askPri_up: 0.0000 , askPri_down: 0.0067

    match ask price:
        probability of bidPri_up: 0.0064 , bidPri_down: 0.0000
        probability of askPri_up: 0.0084 , askPri_down: 0.0000
two ticks:
    match bid price:
        probability of bidPri_up: 0.0400 , bidPri_down: 0.0068
        probability of askPri_up: 0.0000 , askPri_down: 0.0516
    match ask price:
        probability of bidPri_up: 0.0620 , bidPri_down: 0.0000
        probability of askPri_up: 0.0057 , askPri_down: 0.0430
    match mid price:
        probability of bidPri_up: 0.0003 , bidPri_down: 0.0000
        probability of askPri_up: 0.0000 , askPri_down: 0.0003
"""

PROB_LIST=[[[0, 0.0090, 0, 0.0067],[0.0064, 0, 0.0084, 0]],[[0.04, 0.0068, 0, 0, 0.0516],[0.062, 0, 0.0057, 0.043],[0.0003, 0, 0, 0.0003]]]
END_TICK = 50
TICK_PRICE_GAP = 0.5
TICK_QTY_TIMES_MORE = 1.5 # variable for qty to becomes more
TICK_QTY_TIMES_LESS = 0.5 # variable for qty to becomes less
BID_OP_INDEX = 19 # match price of first bidask at bid in allbidask index
ASK_OP_INDEX = 20 # match price of first bidask at ask in allbidask index
MATCH_PRICE_CHENGE = 0.8 # match price chance probility


class FinBoard(_FB, Node):
    
    # abstract method

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
        roi = profit/self.original_invest
        
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
        profit = list(self.now_invest)
        buy_or_sell = self.buy_or_sell
        # gap between aP1 and bP1
        gap = (bidask[12]-bidask[2])/TICK_PRICE_GAP

        if gap == 1.0: # gap = 1 tick
            # print("1 tick")

            if bidask[0] == bidask[2]: # match at bid price
                # print("match at bid price")
                
                rand = round(random.random(), 4)

                # ask price down, bid price down, match price same
                if rand < PROB_LIST[0][0][3]: 
                    bidask = ask_price_down(bidask)
                    allbidask, bidask = bid_price_down(allbidask, bidask)

                # bid price down, which means bQ1 = 0, match price same
                elif rand < PROB_LIST[0][0][1]: 
                    allbidask, bidask = bid_price_down(allbidask, bidask)
                    bidask = ask_price_same(bidask)
                
                # bid price same, ask price same, match price might go up
                else: 
                    bidask = bid_price_same(bidask)
                    bidask = ask_price_same(bidask)

                    rand = round(random.random(), 2)
                    if rand < MATCH_PRICE_CHENGE: # match price up
                        bidask, profit, buy_or_sell = match_price_up(transacted, bidask, profit, buy_or_sell)

            # match at ask price
            elif bidask[0] == bidask[12]: 
                # print("match at ask price")
                
                rand = round(random.random(), 4)

                # bid price up, ask price down, match price same
                if rand < PROB_LIST[0][1][0]: 
                    bidask = bid_price_up(bidask)
                    allbidask, bidask = ask_price_up(allbidask, bidask)

                # ask price up, which means aQ1 = 0, match price same
                elif rand < PROB_LIST[0][1][2]: 
                    bidask = bid_price_same(bidask)
                    allbidask, bidask = ask_price_up(allbidask, bidask)

                # bid price same, ask price same, match price go down
                else: 
                    bidask = bid_price_same(bidask)
                    bidask = ask_price_same(bidask)

                    rand = round(random.random(), 2)
                    if rand < MATCH_PRICE_CHENGE: # match price down
                        bidask, profit, buy_or_sell = match_price_down(transacted, bidask, profit, buy_or_sell)


        # gap = 2 ticks 
        elif gap == 2.0: 
            # print("2 tick")

             # match at bid price
            if bidask[0] == bidask[2]:
                # print("match at bid price")

                rand = round(random.random(), 4) 

                # bid price down, which means bQ1 = 0, match price same
                # ask price down because we only see gap = 2 ticks
                if rand < PROB_LIST[0][2][1]: 
                    allbidask, bidask = bid_price_down(allbidask, bidask)
                    bidask = ask_price_down(bidask) # because we only see gap = 2 ticks
                
                # bid price up, match price up, ask price same
                elif rand < PROB_LIST[0][2][0]: 
                    bidask = bid_price_up(bidask)
                    bidask = ask_price_same(bidask)
                    bidask, profit = match_price_up(transacted, bidask, profit, buy_or_sell) # 一定會上漲，我方想賣都可以賣掉

                
                # ask price down, bid price same
                elif rand < PROB_LIST[0][2][0]+PROB_LIST[0][2][3]: 
                    bidask = ask_price_down(bidask)
                    bidask = bid_price_same(bidask)
                    
                    rand = round(random.random(), 2)

                    # match price might go up or same
                    if rand < MATCH_PRICE_CHENGE: 
                        bidask, profit, buy_or_sell = match_price_up(transacted, bidask, profit, buy_or_sell)
                    
                # bid price same, ask price same
                else: 
                    bidask = bid_price_same(bidask)
                    bidask = ask_price_same(bidask)

                    # match price might go up or same
                    rand = round(random.random(), 2)
                    if rand < MATCH_PRICE_CHENGE: 
                        bidask, profit, buy_or_sell = match_price_up(transacted, bidask, profit, buy_or_sell)

            
            # match at ask price
            elif bidask[0] == bidask[12]: 
                # print("match at ask price")
                
                rand = round(random.random(), 4)

                # ask price up, which means aQ1 = 0, match price same
                # bid price up because we only see gap = 2 ticks
                if rand < PROB_LIST[0][3][2]: 
                    bidask = bid_price_up(bidask)
                    allbidask, bidask = ask_price_up(allbidask, bidask)

                # bid price up, ask price same
                elif rand < PROB_LIST[0][3][0]: 
                    bidask = bid_price_up(bidask)
                    bidask = ask_price_same(bidask)

                    rand = round(random.random(), 2)
                    
                    # match price might go down or same
                    if rand < MATCH_PRICE_CHENGE:
                        bidask, profit, buy_or_sell = match_price_down(transacted, bidask, profit, buy_or_sell) 
                
                # ask price down, bid price same, match price must go down
                elif rand < PROB_LIST[0][3][0]+PROB_LIST[0][3][3]: 
                    bidask = bid_price_same(bidask)
                    bidask = ask_price_down(bidask)
                    bidask, profit, buy_or_sell = match_price_down(transacted, bidask, profit, buy_or_sell) # 一定會下跌，我方想買都可以買到
                
                # bid price same, ask price same
                else: 
                    bidask = bid_price_same(bidask)
                    bidask = ask_price_same(bidask)

                    rand = round(random.random(), 2)
                    
                    # match price might go down or same
                    if rand < MATCH_PRICE_CHENGE:
                        bidask, profit, buy_or_sell = match_price_down(transacted, bidask, profit, buy_or_sell) 

            
            elif bidask[0] == bidask[2]+TICK_PRICE_GAP: # match at mid price
                # print("match at mid price")
                
                rand = round(random.random(), 4)

                # bid price up, ask price same
                if rand < PROB_LIST[0][4][0]: 
                    bidask = bid_price_up(bidask)
                    bidask = ask_price_same(bidask)
                    
                    rand = round(random.random(), 2)

                    # match price might go up or same
                    if rand < MATCH_PRICE_CHENGE: 
                        bidask, profit, buy_or_sell = match_price_up(transacted, bidask, profit, buy_or_sell) 
                
                # ask price down, bid price same
                elif rand < PROB_LIST[0][4][0]+PROB_LIST[0][4][3]: 
                    bidask = bid_price_same(bidask)
                    bidask = ask_price_down(bidask)

                    rand = round(random.random(), 2)

                    # match price might go down or same
                    if rand < MATCH_PRICE_CHENGE:
                        bidask, profit, buy_or_sell, buy_or_sell = match_price_down(transacted, bidask, profit, buy_or_sell) 

                # bid price same, ask price same
                else: 
                    bidask = bid_price_same(bidask)
                    bidask = ask_price_same(bidask)

                rand = round(random.random(), 2)

                # match price might go down
                if rand < 0.33:
                    bidask, profit, buy_or_sell = match_price_down(transacted, bidask, profit, buy_or_sell) 
                
                # match price might go up
                elif rand < 0.66: 
                    bidask, profit, buy_or_sell = match_price_up(transacted, bidask, profit, buy_or_sell) 

        # update all bidask
        allbidask = update_all_bidask(allbidask, bidask)

        # next tick
        tick = self.tick + 1
        
        # is it terminal
        is_terminal = tick is END_TICK
        
        return FinBoard(tuple(allbidask), tuple(bidask), tick, is_terminal, buy_or_sell, self.original_invest, tuple(profit))
    

    def return_node(self):
        
        return (
            self.bidask
        )

        
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
        # print(i)
        # print(all_bidask)
        # print(now_bidask[i+10])
        # print(open_price)
        # print(ASK_OP_INDEX+int((now_bidask[i+10]-open_price)/TICK_PRICE_GAP)*2)
    
    all_bidask = tuple(all_bidask)
    return all_bidask

def bid_price_up(bidask):
    # print("Bid Price UP")
    
    # price
    bidask[3:7] = bidask[2:6]
    bidask[2] += TICK_PRICE_GAP
    
    # qty
    bidask[8:12] = bidask[7:11]
    bidask[7] = round(bidask[7] * TICK_QTY_TIMES_LESS)    
    
    return bidask

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

def bid_price_same(bidask):
    # print("Bid Price SAME")
    
    # qty
    bidask[7] = round(bidask[7]*random.uniform(1.5, 0.5)) 
    
    return bidask

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

def ask_price_down(bidask):
    # print("Ask Price DOWN")
    
    # price
    bidask[13:17] = bidask[12:16]
    bidask[12] -= TICK_PRICE_GAP
    
    # qty
    bidask[18:22]= bidask[17:21]
    bidask[17] = round(bidask[17] * TICK_QTY_TIMES_LESS)
    
    return bidask

def ask_price_same(bidask):
    # print("Ask Price SAME")
    bidask[17] = round(bidask[17]*random.uniform(1.5, 0.5))
    
    return bidask

def match_price_up(move, bidask, profit, buy_or_sell):
    # print("Match Price UP")
    bidask[0] += TICK_PRICE_GAP # 上漲
    if move == 0 and buy_or_sell == 1: # 我方想賣都可以賣掉
        profit[0] = profit[1]*bidask[0]
        profit[1] = 0
        buy_or_sell ^= 1
    
    return bidask, profit, buy_or_sell

def match_price_down(move, bidask, profit, buy_or_sell):
    # print("Match Price DOWN")
    bidask[0] -= TICK_PRICE_GAP # 下跌
    
    if move == 0 and buy_or_sell == 0: # 我方想買都可以買到
        profit[1] = profit[0]/bidask[0]
        profit[0] = 0
        buy_or_sell ^= 1
    
    return bidask, profit, buy_or_sell

def play_game():
    tree = MCTS()
    board = new_fin_board()

    # print node
    print(board.return_node())

    for _ in range(30):
        tree.do_rollout(board)
        tree._print_tree_children(board)

    # final choice after all the rollout
    board = tree.choose(board)

def new_fin_board():
    
    # 一開始的買賣五檔
    fbidask = (495.0,2987,495.0,494.5,494.0,493.5,493.0,19.0,17.0,132.0,47.0,193.0,495.5,496.0,496.5,497.0,497.5,193,365,175,318,151)
    
    # 所有的買賣五檔
    allbidask = (fbidask[0],)+(0,)*40
    allbidask = update_all_bidask(allbidask, fbidask)
    
    # 現在的操作要買或是賣
    buy_or_sell = 0 # buy = 0, sell = 1
    
    # 投資
    original_invest = 10000
    
    # (現有的錢, 持股)
    now_invest = (10000, 0)
    
    # allbidask=所有的買賣五檔, bidask=現在的買賣五檔, tick=現在的tick量, terminal=結束, buy_or_sell=買或是賣, original_invest=一開始的投資價格, now_invest=現在的投資價格
    return FinBoard(allbidask=allbidask, bidask=fbidask, tick=0, terminal=False, buy_or_sell=buy_or_sell, original_invest=original_invest, now_invest=now_invest)

if __name__ == "__main__":
    play_game()

