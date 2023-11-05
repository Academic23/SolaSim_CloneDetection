import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

import numpy as np
import math

## 路径双向 consine similarity计算
def path_bicosin_sim(path1,path2):
    a = np.array(path1)
    b = np.array(path2)

    long = a if a.size > b.size else b 
    short = a if a.size <= b.size else b 

    min_len = short.size

    long_cut = long[:min_len]
    assert(long_cut.size == short.size)
    sim = cosine_similarity(long_cut.reshape(1,-1),short.reshape(1,-1))

    long_cut = long[long.size-min_len:]
    assert(long_cut.size == short.size)
    sim2 = cosine_similarity(long_cut.reshape(1,-1),short.reshape(1,-1))
    
    return max(sim,sim2)

# 匈牙利算法最优二分图匹配
class KMAlgorithm:
    def __init__(self, graph):
        self.graph = graph
        self.num_paths_a = len(graph)
        self.num_paths_b = len(graph[0])
        self.match = [-1] * self.num_paths_b
        self.visited_paths_a = [False] * self.num_paths_a
        self.visited_paths_b = [False] * self.num_paths_b
        self.label_paths_a = [0] * self.num_paths_a
        self.label_paths_b = [0] * self.num_paths_b

    def km_algorithm(self):
        for i in range(self.num_paths_a):
            while True:
                self.visited_paths_a = [False] * self.num_paths_a
                self.visited_paths_b = [False] * self.num_paths_b
                if self.dfs(i):
                    break
                delta = float('inf')
                for j in range(self.num_paths_a):
                    if self.visited_paths_a[j]:
                        for k in range(self.num_paths_b):
                            if not self.visited_paths_b[k]:
                                delta = min(delta, self.visited_paths_a[j] + self.label_paths_b[k] - self.graph[j][k])
                if delta == float('inf'):
                    return
                for j in range(self.num_paths_a):
                    if self.visited_paths_a[j]:
                        self.label_paths_a[j] -= delta
                for k in range(self.num_paths_b):
                    if self.visited_paths_b[k]:
                        self.label_paths_b[k] += delta

    def dfs(self, a):
        self.visited_paths_a[a] = True
        for b in range(self.num_paths_b):
            if not self.label_paths_b[b] and self.graph[a][b] == self.label_paths_a[a] + self.label_paths_b[b]:
                self.visited_paths_b[b] = True
                if self.match[b] == -1 or self.dfs(self.match[b]):
                    self.match[b] = a
                    return True
        return False

def compute_instruction_similarity(ia,ib,database):
    ia_feature_vec = database[ia]
    ib_feature_vec = database[ib]
    
    ## 如果两个path不一致，则排除
    if abs(len(ia_feature_vec) - len(ib_feature_vec))>2:
        return None
    if len(ia_feature_vec) ==0 or len(ib_feature_vec)==0:
        return None
    
    ia_length = len(ia_feature_vec)
    ib_length = len(ib_feature_vec)
    # 构建相似度矩阵
    path_pairwise_matrix = [[0] for i in range(ia_length)]*ib_length
    for i,fea1 in enumerate(ia_feature_vec):
        for j,fea2 in enumerate(ib_feature_vec):
            path_sim = path_bicosin_sim(fea1,fea2)
            path_pairwise_matrix[i][j] = path_sim
    
    path_array = np.array(path_pairwise_matrix)
    km = KMAlgorithm(path_array)
    optimal_match = km.km_algorithm()
    
    optimal_match_score = []
    for i,j in eumerate(optimal_match):
        optimal_match_score.append(path_array[i][j])
        
    optimal_score = math.avg(optimal_match_score)
    return optimal_score,optimal_match

def compute_best_match(query, target):
    best = -100
    H0 = 0
    for b in target.keys():
        H0_score = compute_instruction_similarity(query, target[b])
        H0 += sigmoid(H0_score)
    if len(target.keys()) == 0:
        p_H0 = 1
    else:
        p_H0 = H0 / float(len(target.keys()))

    for b in target.keys():
        score = compute_instruction_similarity(query, target[b])
        p = sigmoid(score)
        if p > best:
            best = p

    if best <= 0 or p_H0 <= 0:
        return 0

    return math.log(best / float(p_H0))

def generate_contract_similarity(contract1, contract2):
    similarity_1_1 = 0
    similarity_2_2 = 0
    similarity_1_2 = 0
    similarity_2_1 = 0

    for b1 in contract1.keys():
        similarity_1_1 += compute_best_match(contract1[b1], contract1)

    for b2 in contract2.keys():
        similarity_2_2 += compute_best_match(contract2[b2], contract2)

    for b1 in contract1.keys():
        similarity_1_2 += compute_best_match(contract1[b1], contract2)

    for b2 in contract2.keys():
        similarity_2_1 += compute_best_match(contract2[b2], contract1)

    return max(similarity_1_2, similarity_2_1), max(similarity_1_1, similarity_2_2)