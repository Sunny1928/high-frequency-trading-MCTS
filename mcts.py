from abc import ABC, abstractmethod
from collections import defaultdict
import math
import xgboost as xgb

class MCTS:
    "Monte Carlo tree searcher. First rollout the tree then choose a move."

    def __init__(self, exploration_weight=1):
        self.Q = defaultdict(int) # reward of each node
        self.N = defaultdict(int) # count for each node
        self.P = defaultdict(float) # probility for each node
        self.children = dict()
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
        
        return max(self.children[node], key = score)
    
    def policy_network(self, node):
        xgb_model = xgb.XGBClassifier()
        test = [[node.bidask[1]]+list(node.bidask[7:12])+list(node.bidask[17:23])]

        if node.buy_or_sell == 0:
            weight_path = "./model_weight/bid_using.model"
        elif node.buy_or_sell == 1:
            weight_path = "./model_weight/ask_using.model"
            
        xgb_model.load_model(weight_path)
        pred_prob = xgb_model.predict_proba(test)

        return pred_prob[0]
    
    def do_rollout(self, node):
        "Make the tree one layer better. "
        print("do_rollout")
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
            # print(node)
            if node not in self.children or not self.children[node]:
                # node is either unexplored or terminal
                return path
            
            unexplored = self.children[node] - self.children.keys()
            if unexplored:
                n = unexplored.pop()
                path.append(n)
                return path
            node = self._uct_select(node)

    def _uct_select(self, node):
        # P: policy network probability
        "Select a child of node, balancing exploration & exploitation"

        # All children of node should already be expended
        assert all(n in self.children for n in self.children[node])
            

        return max(self.children[node], key=self.uct)

    def _expend(self, node):
        "Update the children dict with the children of node"
        if node in self.children:
            return

        self.children[node] = node.find_children()
        
        # policy_network = [0.7, 0.3]
        policy_network = self.policy_network(node)
        for n, p in zip(self.children[node], policy_network):
            self.P[n] = p

    def _simulate(self, node):
        "Resturns the reward for a random simlation (to completion) of node"
        while True:
            if node.is_terminal():
                reward = node.reward()
                return reward
            node = node.find_random_child()

    def _backpropagate(self, path, reward):
        "Send the reward back up to the ancestors of the leaf"
        for node in reversed(path):
            self.N[node] += 1
            self.Q[node] += reward

    

    def recursive(self, k, level=0):
        strin = " "
        if k in self.children:
            # print(k)
            strin += "|----" * level
            # strin += str(self.N[k])+ ' ' + str(self.Q[k])
            strin += str(self.N[k])+ ' ' + str(self.uct(k)) + ' ' + str(self.Q[k])

            print(strin)
            keys= self.children[k]
            level += 1
            for i in keys:
                self.recursive(i, level)
        return
            
    
    def _print_tree_children(self, node):
        print(node)
        self.recursive(node)




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
