from tqdm import tqdm
import similarity_computation

def generate_similar_clusters(thrd,all_funcs,database):
    length =len(all_funcs)
    visited = [0]*len(all_funcs)
    func_cluster = {}
    for i in tqdm(range(length)):
        if visited[i] == 1:
            continue

        func1_name = all_funcs[i]
        func1_feature_vec = database[func1_name]
        func_cluster[func1_name] = []
        for j in range(i+1,length):
            if visited[j] == 1:
                continue
            func2_name = all_funcs[j]
            func2_feature_vec = database[func2_name]

            ## 如果两个差距太大，则排除
            if len(func2_feature_vec) != len(func1_feature_vec):
                continue
            if len(func2_feature_vec) ==0 or len(func1_feature_vec)==0:
                continue

            ## 直接对比 阈值设置为0.7
            is_sim = True
            sims = []
            for a,b in zip(func1_feature_vec,func2_feature_vec):
                sim = similarity_computation.compute_instruction_similarity(a,b)
                sims.append(sim)
                if sim < thrd:
                    is_sim = False
                    break

            if is_sim:
                visited[j] = 1
                try:
                    mean_sim = sum(sims)/len(sims)
                    func_cluster[func1_name].append([func2_name,mean_sim])
                except:
                    print(sims)
                    print(func2_feature_vec)
                    print(func1_feature_vec)
                    raise
    return func_cluster