# SolaSim: Clone Detection for Solana Smart Contracts via Program Representation

The first clone detection tool in Solana smart contracts, leveraging program representation at different granularities. This tool is designed to utilize both semantic and structural attributes, effectively representing reachable paths derived from attributed control flow graphs. 

## Framework of SolaSim
## ![image](https://github.com/Academic23/SolaSim_CloneDetection/blob/main/framework.png)

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

## Experiments
Supplemental experiment results and analysis are provided in supplementary material: https://github.com/Academic23/SolaSim_CloneDetection/blob/main/Supplementary%20Material.pdf

## Dataset
### Rules for labeling the ground truth test dataset:
We established the ground truth through random sampling of pairs of smart contracts and instruction-level functions from the entire dataset. The dataset was labeled according to the following criteria: 
https://github.com/Academic23/SolaSim_CloneDetection/blob/main/Supplementary%20Material.pdf
#### For function-level assessment:
Rule 1 for Type 1 clones: If the function codes pairs are strictly identical, they were categorized as true (Type 1 clones); otherwise, they were labeled as false.

Rule 2 for Type 2 clones: If the function codes pairs are strictly identical except for variable names, they were categorized as true (Type 2 clones); otherwise, they were labeled as false.

Rule 3 for Type 3 clones:
a) Whether the two function codes pairs implement the same functionality, such as "deposit" and "withdraw."
b) Whether the two function codes pairs merely reorder logic sequences without altering the logical structure.
c) Whether the two function codes pairs introduce additional code statements that do not affect the implementation of other code.
d) Whether the two function codes pairs delete code statements that do not affect the implementation of other code.

If the function codes pairs fulfill above sub-rules of Type-3 clones, then they were labeled as true; otherwise, they were labled as false. In addition, we provided an example of Type 3 code clones in Figure 6 of the paper.

#### For smart contract-level assessment:
We first analyze the business purpose of pairs of smart contracts. If two smart contracts served different business purposes, they were directly labeled as false (not related). Otherwise, we scrutinized the functions within each smart contract. We allowed for some differences in functions between pairs of smart contracts, as long as approximately 70% of the functions were similar. The criteria for assessing function pairs remained consistent with the aforementioned rules. Therefore, if the above requirements were met, we labeled the pair of smart contracts as true (related); otherwise, they were considered unrelated.

### Open dataset
Since the size of the dataset (more than 50 GB) exceeds the limit of GitHub. Thus we only upload the project name that we crawled from GitHub, and uploaded the cfg dot file zip and **ground truth test dataset** to Google driver for downloaded.

https://drive.google.com/file/d/1HQdByXsx0tbdeGYQ6prJa_RtQFWHawYD/view?usp=drive_link

https://drive.google.com/file/d/12drDJz-MIQG6PxEuVd1LwMKYAWR_RcUb/view?usp=drive_link

In the following, we will upload our raw data set to Cloud for future researches.

## How to compile smart contract and visualize cfg dot:
  1. cargo rustc -- --emit mir -Z dump-mir=F -Z dump-mir-dataflow -Z unpretty=mir-cfg -o mir.dot
  2. dot -T svg -o simple_mir.svg simple_mir.dot
