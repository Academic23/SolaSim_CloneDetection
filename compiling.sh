#!/bin/bash

# for line in $(cat ../command.txt)
# do
#     echo $line
# done

# cd /home/solana/train_data/wangc/solana-new/programs/config && cargo rustc -- --emit mir -Z dump-mir=F -Z dump-mir-dataflow -Z unpretty=mir-cfg -o config_cfg.dot

while read rows
do {
    echo $rows | sh 
}||{
    time2=$(date "+%Y%m%d%H%M%S")
    echo "Error path: "$? $time2 $rows >> "/home/solana/error_path.txt"
}
cd /home/solana
rustup default nightly
done < command.txt