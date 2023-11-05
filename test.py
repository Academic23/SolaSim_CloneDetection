import os
from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re
import networkx as nx
import joblib

## 首先拆分出所有的subgraph
def split_subgraph(dot):
    length = len(dot)
    i=0
    subgraphs = []
    subgraph = []
    while i < length-1:
        if 'subgraph' in dot[i]:
            subgraph.append(dot[i])
            i += 1
            try:
                while 'subgraph' not in dot[i]:
                    subgraph.append(dot[i])
                    i += 1
            except:
                pass
            subgraphs.append(subgraph)
            subgraph = []
        else:
            i += 1
    return subgraphs

## 解析单个subgraph 过滤没有图的subgraph
## 抽取 具体数据
all_defined_operations = ['drop','branch','assert','signer','context_new','try_accounts',
     'try_from_slice_unchecked','account_deref_mut','deref','accountsexit',
     'deserialize','unpack','pack',"signature","to_account_info","from_residual"
     ,"try_to_vec","alloc",'partialeq','iterator','transfer','validate','withdraw'
    ,'swap','pubkey','unwrap','slice','mint','ok_or','accountinfo','push','serialize'
     ,'key','check','default','initialized','to_tokens','errorcode','decimal','sysvar',
    'error','size_of','option','accountloader','clone','index','vec','string','from_account_info',
    'initialize','uint','spl_token','deposit','try_from','create_account','arithmetic','authority',
            'invoke','hash','state','as_ref','account','write','update','create','run','burn','merkleroll',
    'borrow','increment','balance','print','solana_program','instruction','u_process','initialize',
    'arithmetic','judge','anchor_spl','append','split','pda','panic','x86_instruction','anchor_lang',
    'std','get_change_log','leaf','bytes','iter','data','into','cleanup','V = V','goto','resume','return','unreachable','V = const _']

def instruction_process(inst):
    inst = inst.lower()
    
    inst = re.sub("_[\d]{1,4}","V",inst)
    inst = re.sub("'","",inst)
    inst = re.sub(";::","::",inst)
    inst = re.sub(";::","::",inst)
    inst = re.sub(";::","::",inst)
    inst = re.sub("::;","::",inst)
    inst = re.sub("::;","::",inst)
    inst = re.sub("::;","::",inst)
    inst = re.sub("= ;","= ",inst)
    inst = re.sub("_,","",inst)
    inst = re.sub("\[closure.*?\]","",inst)
    
    if 'drop' in inst:
        inst = 'drop'
    
    if re.findall("clean\(",inst):
        inst = 'cleanup'
        
    if 'switchint' in inst or 'branch' in inst or 'discriminant' in inst:
        inst = 'branch'
        
    if 'assert' in inst:
        inst = 'assert'
        
    if re.findall("signer",inst):
        inst = 'signer'
        
    if re.findall("[anchor_lang::context::context|anchor_lang::context|anchor_lang::cpicontext].*new",inst):
        inst = 'context_new'
    
    if 'try_accounts' in inst:
        inst = 'try_accounts'
    
    if 'try_from_slice_unchecked' in inst:
        inst = 'try_from_slice_unchecked'
    if 'deref_mut' in inst and 'account' in inst:
        inst = 'account_deref_mut'
    if 'deref_mut' in inst or 'deref' in inst:
        inst = 'deref'
    
    if 'accountsexit' in inst:
        inst = 'accountsexit'
        
    if re.findall("deserialize",inst):
        inst = 'deserialize'
        
#     if re.match(".*::instruction.*::errorcode.*",inst): 
#         inst = 'instruction_error'
        
    if re.findall("unpack",inst):
        inst = 'unpack'
        
    if re.findall("pack",inst):
        inst = 'pack'
        
    if re.findall("signature",inst):
        inst = "signature"
    
    if re.findall("to_account_info",inst):
        inst = "to_account_info"
        
    if re.findall("from_residual",inst):
        inst = "from_residual"
        
    if re.findall("try_to_vec",inst):
        inst = "try_to_vec"
    
    if re.findall("alloc",inst):
        inst = "alloc"
    
    if re.findall("partialeq",inst):
        inst = 'partialeq'
    
    if re.findall("iterator",inst):
        inst = 'iterator'
        
    if re.findall("transfer",inst):
        inst = 'transfer'
    
    if re.findall("validate|verify\(",inst):
        inst = 'validate'
    
    if re.findall("withdraw",inst):
        inst = 'withdraw'
    
    if re.findall("swap",inst):
        inst = 'swap'
        
    if re.findall("pubkey",inst):
        inst = 'pubkey'
        
    if re.findall("unwrap",inst):
        inst = 'unwrap'
    
    if re.findall("slice::impl|slice",inst):
        inst = 'slice'
    
    if re.findall("mint",inst):
        inst = 'mint'
        
    if re.findall("ok_or",inst):
        inst = 'ok_or' ## branch
    
    if re.findall("accountinfo",inst):
        inst = 'accountinfo'
        
    if re.findall("push",inst):
        inst = 'push'
    
    if re.findall("serialize",inst):
        inst = 'serialize'
        
    if re.findall("key::key",inst):
        inst = 'key'
        
    if re.findall("check",inst):
        inst = 'check'
        
    if re.findall("default",inst):
        inst = 'default'
        
    if re.findall("initialized",inst):
        inst = 'initialized'
        
    if re.findall("to_tokens",inst):
        inst = 'to_tokens'
    
    if re.findall("errorcode",inst):
        inst = 'errorcode'
        
    if re.findall("decimal",inst):
        inst = 'decimal'
    
    if re.findall("sysvar",inst):
        inst = 'sysvar'
        
    if re.findall("error",inst):
        inst = 'error'
        
    if re.findall("size_of",inst):
        inst = 'size_of'
        
    if re.findall("option",inst):
        inst = 'option'
        
    if re.findall("accountloader",inst):
        inst = "accountloader"
        
    if re.findall("clone",inst):
        inst = 'clone'
    
    if re.findall("index",inst):
        inst = 'index'
        
    if re.findall("vec",inst):
        inst = 'vec'
        
    if re.findall("string|str[;]\(",inst):
        inst = 'string'
        
    if re.findall("from_account_info",inst):
        inst = 'from_account_info'
        
    if re.findall("initialize|init\(",inst):
        inst = 'initialize'
        
    if re.findall("uint",inst):
        inst = 'uint'
        
    if re.findall("spl_token",inst):
        inst = 'spl_token'
        
    if re.findall("deposit",inst):
        inst = 'deposit'
        
    if re.findall("try_from",inst):
        inst = 'try_from'
        
    if re.findall("create.*account",inst):
        inst = 'create_account'
        
    if re.findall("V = u[\d]{1,3}|sub|add|mul|div|precise",inst) and not re.findall("individual\(",inst):
        inst = 'arithmetic'
        
    if re.findall("authority",inst):
        inst = 'authority'
        
    if re.findall("invoke|invoke_signed",inst):
        inst = 'invoke'
        
    if re.findall("hash",inst):
        inst = 'hash'
        
    if re.findall("state",inst):
        inst = 'state'
        
    if re.findall("as_ref",inst):
        inst = 'as_ref'
        
    if re.findall("accounts?\(",inst):
        inst = 'account'
        
    if re.findall("write",inst):
        inst = 'write'
    
    if re.findall("update",inst):
        inst = 'update'
        
    if re.findall("create",inst):
        inst = 'create'
        
    if re.findall("run",inst):
        inst = 'run'
        
    if re.findall("burn",inst):
        inst = 'burn'
        
    if re.findall("merkleroll",inst):
        inst = 'merkleroll'
    
    if re.findall("borrow",inst):
        inst = 'borrow'
        
    if re.findall("increment",inst):
        inst = 'increment'
        
    if re.findall("balance",inst):
        inst = 'balance'
    
    if re.findall("print",inst):
        inst = 'print'
    
    if re.findall("solana_program",inst):
        inst = 'solana_program'
    
    if re.findall("instruction\(",inst):
        inst = 'instruction'
        
    if re.findall("i32|u128|u64|u8",inst):
        inst = 'u_process'
        
    if re.findall("init",inst):
        inst = 'initialize'
        
    if re.findall("math",inst):
        inst = 'arithmetic'
        
    if re.findall("is_",inst):
        inst = 'judge'
        
    if re.findall("anchor_spl",inst):
        inst = 'anchor_spl'
        
    if re.findall("append\(",inst):
        inst = 'append'
        
    if re.findall("split",inst):
        inst = 'split'
        
    if re.findall("pda",inst):
        inst = 'pda'
    
    if re.findall("panic",inst):
        inst = 'panic'
    
    if re.findall("x86",inst):
        inst = 'x86_instruction'
    
    if re.findall("anchor_lang",inst):
        inst = 'anchor_lang'
    
    if re.findall("std",inst):
        inst = 'std'
        
    for rgx in ['get_change_log','leaf\(','bytes\(','iter\(',"::data\(",'into\(']:
        if re.findall(rgx,inst):
            inst = rgx.replace("\(","")
            inst = rgx.replace("::","")
            
    return inst
    

def path_bicosin_sim(path1,path2):
    a = np.array(path1)
    b = np.array(path2)

    long = a if a.size > b.size else b 
    short = a if a.size <= b.size else b 

    min_len = short.size

    ## 头部对齐
    long_cut = long[:min_len]
    assert(long_cut.size == short.size)
    sim = cosine_similarity(long_cut.reshape(1,-1),short.reshape(1,-1))

    ## 尾部对齐
    long_cut = long[long.size-min_len:]
    assert(long_cut.size == short.size)
    sim2 = cosine_similarity(long_cut.reshape(1,-1),short.reshape(1,-1))
    
    return max(sim,sim2)

def parse_subgraphs(subgraphs):
    if len(subgraphs) == 0:
        return []
    new_subgraphs = {}
    for sbg in subgraphs:
        
        # 函数名匹配
        label = sbg[4]
        func_name = re.findall("^label=<fn.*?\(",label)[0]
            
        # 如果不存在图结构，则删除
        basic_blocks = [item for item in sbg[5:] if "->" not in item and item not in ["}",' ',''] ]
        blocks_edges = [item for item in sbg[5:] if "->" in item]
        
        # 设置边的数量 少于5就取出
        if len(blocks_edges) <= 5:
            continue   
        if re.findall("closure#|&lt|error",func_name):
            continue
            
        func_name = func_name.replace("label=<fn ","")
        func_name = func_name.replace("(","")
        
        # 输入参数匹配
        label_split = label.split('<br align="left"/>')
        func_inputs = []
        func_parameters = {}
        for kv in re.findall("\(.*?\)",label_split[0])[0][1:-1].split(","):
            k = kv.split(":")[0]
            v = ":".join(kv.split(":")[1:])
            func_inputs.append(k)
            func_parameters[k] = v.strip()

        for lsp in label_split:
            if "let" in lsp and 'debug' not in lsp:
                kv = lsp.split(":")
                k = kv[0].replace("let","").strip()
                v = ":".join(kv[1:])
                func_parameters[k] = v.strip()
                
        ## basic block 处理
        processed_basic_blocks = {}
        for bk in basic_blocks:
            basic_block_id = re.findall("^.*?\[",bk)[0].replace("[","").strip()
            processed_basic_blocks[basic_block_id] = []

            items = bk.replace(basic_block_id,"").strip()[1:-2]
            items = items.replace('shape="none", label=<','')
            items = items.replace('<table border="0" cellborder="1" cellspacing="0">','')
            items = items.replace('<td bgcolor="gray" align="center" colspan="1">','')
            items = items.replace('</td>','')
            items = items.replace('</tr>','')
            items = items.replace('<tr>','')
            items = items.replace('</table>>','')
            items = items.replace('td bgcolor="lightblue" align="center" colspan="1"','')

            items = items.split('td align="left"')
            for item in items:
                item = item.replace("<","")
                item = item.replace(">","")
                item = item.replace('balign="left"',"")
                item = item.replace('&amp',"")
                item = item.replace('&quot',"")
                item = item.replace('&lt',"")
                item = item.replace('&gt',"")
                item = item.replace("'","")
                item = item.split("br/")
                item = [x.strip() for x in item if x != '']
                if item != []:            
                    processed_basic_blocks[basic_block_id].extend(item)
            processed_basic_blocks[basic_block_id] = [instruction_process(x) for x in processed_basic_blocks[basic_block_id][1:]]
        
        ## 处理边
        processed_edges = []
        for item in blocks_edges:
            edge_label = re.findall('label=\".*?\"',item)[0].replace('label=','').replace('"',"")
            start_node = item.split(" ")[0]
            end_node = item.split(" ")[2]
            tmp_edge = (start_node,end_node,edge_label)
            processed_edges.append(tmp_edge)        
        
        sbg_dict = {"func_inputs":func_inputs,"func_parameters":func_parameters,"basic_blocks":processed_basic_blocks,"block_edges":processed_edges}
        new_subgraphs[func_name]=sbg_dict
    return new_subgraphs

## 读取当前的dot文件，生成所有subgraphs的feature vectors
# dot_files = os.listdir("./generated_dot/")
# for file in tqdm.tqdm(dot_files):
#     print(file)
#     file_path = f"./generated_dot/{file}"
#     try:
#         with open(file_path,'r') as f:
#             tmp_dot = f.read().split("\n")
#     except:
#         print("open error:",file)
#         continue
        
#     tmp_dot = [x.strip() for x in tmp_dot]
#     tmp_subgraphs = split_subgraph(tmp_dot)
#     try:
#         tmp_processed_subgraphs = parse_subgraphs(tmp_subgraphs)
#     except:
#         print("error:",file_path)
#         break

#     if not tmp_processed_subgraphs:
#         continue

print("读取dict数据")
file_subgraphs = joblib.load("program_file_subgraphs.m")
print("读取成功")

all_subgraphs_features_dict = {}
for file_name,file_body in tqdm(file_subgraphs.items()):
    # simple_file_name = file_name.split("@")[-1].replace('_cfg.dot',"")
    # if simple_file_name not in ['programs','program']:
    #     continue
    for func_name,func_body in file_body.items():
        func_name = file_name+"@"+func_name
        tmp_edges = func_body['block_edges']
        tmp_basic_blocks = func_body['basic_blocks']

        ## 删减一部分过长的
        if len(tmp_edges) > 100:
            continue

        func_mdg = nx.MultiDiGraph()
        func_mdg.add_edges_from(tmp_edges)
        
        ## 其中一个function的subgraphs
        tmp_basic_blocks_feature_vec = {}
        for k,v in tmp_basic_blocks.items():
            operations_counter = {k:0 for k in all_defined_operations}
            for fea in v:
                if fea in operations_counter.keys():
                    operations_counter[fea] += 1
            tmp_basic_blocks_feature_vec[k] = list(operations_counter.values())

        root = tmp_edges[0][0]
        leafs = []
        for edges in tmp_edges:
            if edges[2] == 'return':
                leafs.append(edges[1])
                
        all_subgraph_paths = []
        for leaf in leafs:
            leaf_paths = list(nx.all_simple_paths(func_mdg,root,leaf,cutoff=50))
            all_subgraph_paths.extend(leaf_paths)

        ## 设置路径的长度要大于3
        all_subgraph_paths = [x for x in all_subgraph_paths if len(x)>3]
        
        all_subgraph_paths_feature_vec = []
        for path in all_subgraph_paths:
            path_vec = []
            for node in path:
                path_vec.extend(tmp_basic_blocks_feature_vec[node])
            all_subgraph_paths_feature_vec.append(path_vec)
        all_subgraphs_features_dict[func_name] = all_subgraph_paths_feature_vec


import joblib
joblib.dump(all_subgraphs_features_dict,'programs_subgraph.m')