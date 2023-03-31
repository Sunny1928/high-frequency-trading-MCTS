from abc import ABC, abstractmethod
from collections import defaultdict
import math
import xgboost as xgb
import numpy as np

# model
xgb_model_ask = xgb.XGBClassifier()
xgb_model_bid = xgb.XGBClassifier()      
xgb_model_ask.load_model("./model_weight/ask_using.model")
xgb_model_bid.load_model("./model_weight/bid_using.model")

class MCTS:
    "Monte Carlo tree searcher. First rollout the tree then choose a move."

    def __init__(self, exploration_weight=1):

        # reward of each node
        self.Q = defaultdict(int) 
        
        # count for each node
        self.N = defaultdict(int)

        # probility for each node
        self.P = defaultdict(float) 

        # children of each node
        self.children = dict()

        # exploration_weight
        self.exploration_weight = exploration_weight

    

    def uct(self, n):
        "Upper confidence bound trees"
        return self.Q[n] / self.N[n] + self.exploration_weight*(self.P[n]/self.N[n])

    def choose(self, node):

        if node.is_terminal():
            raise RuntimeError(f"choose called on terminal node {node}")
        
        def score(n):
            if self.N[n] == 0:
                return float("-inf") # the most min value
            return self.Q[n] / self.N[n] # avg
        
        # choose the node having max score
        children_list = self.children[node]
        max_index = children_list.index(max(children_list, key = score))

        return max_index
    
    def policy_network(self, node):
        test = [[node.bidask[1]]+list(node.bidask[7:12])+list(node.bidask[17:23])]
        
        # buy
        if node.buy_or_sell == 0:
            pred_prob = xgb_model_ask.predict_proba(test) # pridict down

        # sell
        elif node.buy_or_sell == 1:
            pred_prob = xgb_model_bid.predict_proba(test) # pridict up

        return [pred_prob[0][1], pred_prob[0][0]]
    
    def do_rollout(self, node):
        "Make the tree one layer better. "
        # print("do_rollout")
        path = self._select(node) 
        leaf = path[-1]
        self._expend(leaf)
        reward = self._simulate(leaf)
        self._backpropagate(path, reward)

    def _select(self, node):
        "Find an unexplored descendent of node"
        path=[]
        while True:
            path.append(node)
            if node not in self.children or not self.children[node]:
                # node is either unexplored or terminal
                return path
            
            # select unexplored node
            unexplored = self.children[node] - self.children.keys()
            if unexplored:
                n = unexplored.pop()
                path.append(n)
                return path
            node = self._uct_select(node)

    def _uct_select(self, node):
        "Select a child of node, balancing exploration & exploitation"

        # All children of node should already be expended
        assert all(n in self.children for n in self.children[node])
            
        # find node have max uct
        return max(self.children[node], key=self.uct)

    def _expend(self, node):
        "Update the children dict with the children of node"
        if node in self.children:
            return

        self.children[node] = node.find_children()
        
        policy_network = self.policy_network(node)

        # update happening probility of nodes
        for n, p in zip(self.children[node], policy_network):
            self.P[n] = p

    def _simulate(self, node):
        "Resturns the reward for a random simlation (to completion) of node"
        while True:
            if node.is_terminal():
                reward = node.reward()
                return reward
            
            # randomly choose a node
            node = node.find_random_child()

    def _backpropagate(self, path, reward):
        "Send the reward back up to the ancestors of the leaf"
        for node in reversed(path):
            self.N[node] += 1
            self.Q[node] += reward
    

    # for _print_tree_children to print MCTS tree
    def recursive(self, k, level=0):
        strin = " "
        if k in self.children:
            # print(k)
            strin += "|----" * level
            strin += str(self.N[k])+ ' ' + str(self.uct(k))  + ' ' + str(self.Q[k]) + ' ' + str(self.P[k])
            print(strin)
            keys= self.children[k]
            level += 1
            for i in keys:
                self.recursive(i, level)
        return
            
    
    def _print_tree_children(self, node):
        print(node)
        self.recursive(node)



# using abstractmethod to 繼承 node
class Node(ABC):

    @abstractmethod
    def find_children(self):
        "All possible successors of this board state"
        return set()
    
    @abstractmethod
    def find_random_child(self):
        "Random successor of this board state (for more efficient simulation)"
        return None
    
    @abstractmethod
    def is_terminal(self):
        return True
    
    @abstractmethod
    def __hash__(self):
        return 123456789
    
    @abstractmethod
    def __eq__(node1, node2):
        return True
