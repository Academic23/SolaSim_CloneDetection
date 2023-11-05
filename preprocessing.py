import json
import os
import tqdm
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from tqdm import tqdm_notebook as tqdm
import re
import networkx as nx

## 定义特征指令
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

## 拆分dot到function层面的CFG子图
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

## 对所有的指令做统一命名
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
    elif re.findall("clean\(",inst):
        inst = 'cleanup'   
    elif 'switchint' in inst or 'branch' in inst or 'discriminant' in inst:
        inst = 'branch' 
    elif 'assert' in inst:
        inst = 'assert'  
    elif re.findall("signer",inst):
        inst = 'signer'    
    elif re.findall("[anchor_lang::context::context|anchor_lang::context|anchor_lang::cpicontext].*new",inst):
        inst = 'context_new'
    elif 'try_accounts' in inst:
        inst = 'try_accounts'
    elif 'try_from_slice_unchecked' in inst:
        inst = 'try_from_slice_unchecked'
    elif 'deref_mut' in inst and 'account' in inst:
        inst = 'account_deref_mut'
    elif 'deref_mut' in inst or 'deref' in inst:
        inst = 'deref'
    elif 'accountsexit' in inst:
        inst = 'accountsexit'   
    elif re.findall("deserialize",inst):
        inst = 'deserialize'    
    elif re.findall("unpack",inst):
        inst = 'unpack'    
    elif re.findall("pack",inst):
        inst = 'pack'   
    elif re.findall("signature",inst):
        inst = "signature"
    elif re.findall("to_account_info",inst):
        inst = "to_account_info"    
    elif re.findall("from_residual",inst):
        inst = "from_residual"    
    elif re.findall("try_to_vec",inst):
        inst = "try_to_vec"
    elif re.findall("alloc",inst):
        inst = "alloc"
    elif re.findall("partialeq",inst):
        inst = 'partialeq'
    elif re.findall("iterator",inst):
        inst = 'iterator'  
    elif re.findall("transfer",inst):
        inst = 'transfer'
    elif re.findall("validate|verify\(",inst):
        inst = 'validate'
    elif re.findall("withdraw",inst):
        inst = 'withdraw'
    elif re.findall("swap",inst):
        inst = 'swap'    
    elif re.findall("pubkey",inst):
        inst = 'pubkey'    
    elif re.findall("unwrap",inst):
        inst = 'unwrap'
    elif re.findall("slice::impl|slice",inst):
        inst = 'slice'
    elif re.findall("mint",inst):
        inst = 'mint'   
    elif re.findall("ok_or",inst):
        inst = 'ok_or' ## branch
    elif re.findall("accountinfo",inst):
        inst = 'accountinfo'    
    elif re.findall("push",inst):
        inst = 'push'
    elif re.findall("serialize",inst):
        inst = 'serialize'    
    elif re.findall("key::key",inst):
        inst = 'key'    
    elif re.findall("check",inst):
        inst = 'check'    
    elif re.findall("default",inst):
        inst = 'default'    
    elif re.findall("initialized",inst):
        inst = 'initialized'    
    elif re.findall("to_tokens",inst):
        inst = 'to_tokens'
    elif re.findall("errorcode",inst):
        inst = 'errorcode'    
    elif re.findall("decimal",inst):
        inst = 'decimal'
    elif re.findall("sysvar",inst):
        inst = 'sysvar'
    elif re.findall("error",inst):
        inst = 'error'   
    elif re.findall("size_of",inst):
        inst = 'size_of'  
    elif re.findall("option",inst):
        inst = 'option'   
    elif re.findall("accountloader",inst):
        inst = "accountloader"  
    elif re.findall("clone",inst):
        inst = 'clone'
    elif re.findall("index",inst):
        inst = 'index'  
    elif re.findall("vec",inst):
        inst = 'vec'
    elif re.findall("string|str[;]\(",inst):
        inst = 'string'
    elif re.findall("from_account_info",inst):
        inst = 'from_account_info'
    elif re.findall("initialize|init\(",inst):
        inst = 'initialize'
    elif re.findall("uint",inst):
        inst = 'uint'
    elif re.findall("spl_token",inst):
        inst = 'spl_token'
    elif re.findall("deposit",inst):
        inst = 'deposit' 
    elif re.findall("try_from",inst):
        inst = 'try_from'
    elif re.findall("create.*account",inst):
        inst = 'create_account' 
    elif re.findall("V = u[\d]{1,3}|sub|add|mul|div|precise",inst) and not re.findall("individual\(",inst):
        inst = 'arithmetic'
    elif re.findall("authority",inst):
        inst = 'authority'
    elif re.findall("invoke|invoke_signed",inst):
        inst = 'invoke'
    elif re.findall("hash",inst):
        inst = 'hash'
    elif re.findall("state",inst):
        inst = 'state'
    elif re.findall("as_ref",inst):
        inst = 'as_ref'
    elif re.findall("accounts?\(",inst):
        inst = 'account'
    elif re.findall("write",inst):
        inst = 'write'
    elif re.findall("update",inst):
        inst = 'update'
    elif re.findall("create",inst):
        inst = 'create'
    elif re.findall("run",inst):
        inst = 'run'
    elif re.findall("burn",inst):
        inst = 'burn'
    elif re.findall("merkleroll",inst):
        inst = 'merkleroll'
    elif re.findall("borrow",inst):
        inst = 'borrow'
    elif re.findall("increment",inst):
        inst = 'increment'
    elif re.findall("balance",inst):
        inst = 'balance'
    elif re.findall("print",inst):
        inst = 'print'
    elif re.findall("solana_program",inst):
        inst = 'solana_program'
    elif re.findall("instruction\(",inst):
        inst = 'instruction'
    elif re.findall("i32|u128|u64|u8",inst):
        inst = 'u_process'
    elif re.findall("init",inst):
        inst = 'initialize'
    elif re.findall("math",inst):
        inst = 'arithmetic'
    elif re.findall("is_",inst):
        inst = 'judge'
    elif re.findall("anchor_spl",inst):
        inst = 'anchor_spl'
    elif re.findall("append\(",inst):
        inst = 'append'
    elif re.findall("split",inst):
        inst = 'split'
    elif re.findall("pda",inst):
        inst = 'pda'
    elif re.findall("panic",inst):
        inst = 'panic'
    elif re.findall("x86",inst):
        inst = 'x86_instruction'
    elif re.findall("anchor_lang",inst):
        inst = 'anchor_lang'
    elif re.findall("std",inst):
        inst = 'std'
    elif re.findall("V = const true|V = mut V|V = const false|V = move V|V = \(move V, move V\)|\(*V\) = V",inst):
        inst = 'variable asign'
        
    for rgx in ['get_change_log','leaf\(','bytes\(','iter\(',"::data\(",'into\(']:
        if re.findall(rgx,inst):
            inst = rgx.replace("\(","")
            inst = rgx.replace("::","")
    return inst

## 解析subgraphs
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
        processed_basic_blocks4feature = {}
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
            processed_basic_blocks4feature[basic_block_id] = [instruction_process(x) for x in processed_basic_blocks[basic_block_id][1:]]
        
        ## 处理边
        processed_edges = []
        for item in blocks_edges:
            edge_label = re.findall('label=\".*?\"',item)[0].replace('label=','').replace('"',"")
            start_node = item.split(" ")[0]
            end_node = item.split(" ")[2]
            tmp_edge = (start_node,end_node,edge_label)
            processed_edges.append(tmp_edge)        
        
        sbg_dict = {"func_inputs":func_inputs,"func_parameters":func_parameters,"basic_blocks":processed_basic_blocks,"processed_basic_blocks":processed_basic_blocks4feature,"block_edges":processed_edges}
        new_subgraphs[func_name]=sbg_dict
    return new_subgraphs

def feature_select(attributes):
    
    instruction_attributes_frequency=[defaultdict(int) for i in range(len(attributes))]
    
    attribute_set = set()
    for i,attribute_row in enumerate(attributes):
        for j in attribute_row:
            attribute_set.add(j)
            instruction_attributes_frequency[i][j]+=1
     
    attribute_set = list(attribute_set)
    #计算每个attribute的TF值
    instruction_attributes_tf = []
    for attribute_frequency in instruction_attributes_frequency:
        attribute_tf={} 
        for i in attribute_frequency:
            attribute_tf[i]=attribute_frequency[i]/sum(attribute_frequency.values())
        instruction_attributes_tf.append(attribute_tf)
            
    #计算每个attributes的IDF值
    path_num=len(attributes)
    attribute_idf={} 
    attribute_path_frequency = {k:0 for k in attribute_set}
    for att in attribute_set:
        for attribute_row in attributes:
            if att in attribute_row:
                attribute_path_frequency[att] += 1

    for k,v in attribute_path_frequency.items():
        attribute_idf[k]=math.log(path_num/(v+1))
 
    #计算每个attribute的TF*IDF的值
    path_attribute_tf_idf=[]
    for attribute_tf in instruction_attributes_tf:
        attribute_tf_idf={} 
        for k,v in attribute_tf.items():
            attribute_tf_idf[k]=attribute_tf[k]*attribute_idf[k]
        path_attribute_tf_idf.append(attribute_tf_idf)

    return path_attribute_tf_idf


def generate_smart_contract_representations(file_subgraphs):
    all_subgraphs_features_dict = {}

    for file_name,file_body in tqdm(file_subgraphs.items()):
        simple_file_name = file_name.split("@")[-1].replace('_cfg.dot',"")
        if simple_file_name not in ['programs','program']:
            continue
        
        for func_name,func_body in file_body.items():
            func_name = file_name+"@"+func_name
            
            tmp_edges = func_body['block_edges']
            tmp_basic_blocks = func_body['processed_basic_blocks']
            
            ## 删减一部分过长的
            if len(tmp_edges) > 300:
                continue
            
            ## 构建子图
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
                leaf_paths = list(nx.all_simple_paths(func_mdg,root,leaf))
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
    
    return all_subgraphs_features_dict