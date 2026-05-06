# 🌊 WAVE: Weighted Adaptive Vehicle-to-Vehicle Energy-consensus

---

## 📌 1. Project Overview

**WAVE** is a blockchain-based Vehicle-to-Vehicle (V2V) energy trading system built on **Hyperledger Fabric**. 

The core contribution of this project is a novel **Adaptive Probabilistic Consensus Mechanism** designed to replace traditional deterministic selection models (like Proof-of-Reputation). 

The WAVE architecture focuses on achieving three critical goals for decentralized energy grids:
* **Maximized Decentralization** (High Nakamoto Coefficient)
* **Algorithmic Fairness** (High Jain Index, Low Gini Coefficient)
* **Performance Parity** (Maintained low latency)

---

## 🎯 2. The Core Problem

In standard deterministic models (the Baseline), the system rigidly selects the single validator with the highest reputation. In real-world simulations, this creates severe network vulnerabilities:

* 👑 **The "King of the Hill" Monopoly**: One validator dominates the network traffic until it eventually fails, causing centralization.
* 💀 **Validator Starvation**: In our testing, over 30% of healthy nodes were *never* selected to participate in validation.
* 🔓 **Security Vulnerability**: A low Nakamoto Coefficient means a small cartel of high-reputation nodes can easily control >50% of the network.

---

## 🌊 3. The WAVE Solution

WAVE introduces an intelligent, weighted probabilistic approach to democratize the network and distribute load fairly.

### 🔑 Key Mathematical Components

1. **Dynamic Reputation Update**: Validator reputation dynamically adapts based on validation correctness, participation rate, and simulated network latency.
2. **Latency-Aware Scoring**: Each validator is scored using a multi-variable equation:
   `Score = α(reputation) + β(successRate) + γ(1 / (1 + latency))`
3. **Weighted Probabilistic Selection (MAIN NOVELTY)**: Instead of deterministically picking the absolute highest score, validators are selected *probabilistically* where `Probability ∝ Score`. This ensures even lower-ranked validators participate occasionally, preventing starvation while still heavily rewarding good actors.

---

## ⚙️ 4. System Architecture

* **Platform**: Hyperledger Fabric (permissioned blockchain)
* **Smart Contracts**: Node.js / JavaScript Chaincode (`chaincode/v2v/javascript/v2vContract.js`)
* **Evaluation Suite**: Python 3 Data Analytics & Visualizations (`test-network/results/analyze.py`)
* **Automation**: Bash orchestration for A/B testing (`test-network/run_full_experiment.sh`)

---

## 🔬 5. Experimental Results (4,000 Transactions)

The WAVE consensus was evaluated side-by-side against a deterministic baseline using a 4,000-transaction simulation (2,000 per mode). The simulation injected randomized failure rates (20%) and variable latencies (50ms - 950ms) to exercise the intelligence of the algorithm.

### 🏆 Key Findings:

* **Decentralization (Nakamoto Coefficient)**: Jumped from **8 (Baseline)** to **20 (WAVE)**, representing a massive 150% security upgrade against 51% attacks.
* **Fairness (Gini Coefficient)**: Dropped from **0.639 (Highly Unequal)** to **0.170 (Highly Equal)**. Starvation was completely eliminated (0 starved nodes vs 16 in baseline).
* **Performance Parity**: The algorithmic overhead of probabilistic selection added only **~19ms** to the average transaction latency, proving the system scales without performance degradation.
* **Statistical Significance**: The improvements in workload distribution are mathematically significant (Mann-Whitney U Test: **p < 0.05**).

---

## 🚀 6. How to Reproduce the Experiment (For Researchers)

We have packaged the entire experiment into a standalone repository. You do not need to download the full `fabric-samples` bloat, but you will need the Fabric binaries.

### Prerequisites
* **Docker** & **Docker Compose**
* **Node.js** (v18+)
* **Python 3** (with `pip`)

### Step 1: Clone the Repository & Download Fabric Binaries
```bash
# 1. Clone this repository
git clone https://github.com/YourUsername/YourRepositoryName.git
cd YourRepositoryName

# 2. Download official Hyperledger Fabric binaries (v2.5.0) and Docker images
# (The -s flag skips downloading the bloated fabric-samples repo, as our code is self-contained)
curl -sSL https://bit.ly/2ysbOFE | bash -s -- 2.5.0 1.5.2 -s
```

### Step 2: Run the Automated Pipeline
```bash
# 1. Navigate to the test network
cd test-network

# 2. Start the Fabric network and deploy the WAVE chaincode
bash setup.sh

# 3. Run the full A/B orchestration pipeline (2000 tx per mode)
# Note: This will take approximately ~2.5 hours to run all 4,000 transactions.
bash run_full_experiment.sh 2000
```

Upon completion, all statistical logs and comparative graphs (Lorenz curve, Latency distribution, Validator Rank, etc.) will be automatically generated in the `test-network/results/` directory.

---

## 📁 7. Repository Structure

* `/chaincode/v2v/javascript/` - Core smart contract logic and consensus implementation.
* `/test-network/scripts/` - Transaction generators and network setup utilities.
* `/test-network/results/` - Python analytics suite, raw `.txt` logs, and output `.png` graphs.
