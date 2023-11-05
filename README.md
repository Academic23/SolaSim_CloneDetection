# SolaSim: Clone Detection for Solana Smart Contracts via Program Representation

The first clone detection tool in Solana smart contracts, leveraging program representation at different granularities. This tool is designed to utilize both semantic and structural attributes, effectively representing reachable paths derived from attributed control flow graphs. 

## Framework of SolaSim
## ![image](https://github.com/CheWang09/SolanaClone/blob/main/Framework.png)

This project is a prototype implementation of SolaSim, an unsupervised approach to measure Solana smart contract similarity. If you find the tool useful in your work, please cite our paper:
"SolaSim: Clone Detection for Solana Smart Contracts via Program Representation"

## Setup
Our experiments are performed on a Linux-WSL2 virtual machine with Intel Core i9 processors, 64GRAM, and 1.8T SSD.

The dependency packages are listed below:
  1. Python3.8
  2. Cargo/rustup
  3. GCC >=7.1.0
  4. LLVM
  5. NetworkX
  6. All the other packages required by the above packages

## Dataset
Since the size of the dataset (more than 50 GB) exceeds the limit of GitHub. Thus we only upload the project name that we crawled from GitHub, and uploaded the cfg dot file zip to Google driver for downloaded. The link is https://drive.google.com/file/d/1HQdByXsx0tbdeGYQ6prJa_RtQFWHawYD/view?usp=drive_link
In the following, we will store our raw data set on the Cloud for future research.

## How to compile smart contract and visualize cfg dot:
  1. cargo rustc -- --emit mir -Z dump-mir=F -Z dump-mir-dataflow -Z unpretty=mir-cfg -o mir.dot
  2. dot -T svg -o simple_mir.svg simple_mir.dot
