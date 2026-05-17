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

* **Platform**: Hyperledger Fabric v2.5 (permissioned blockchain)
* **Smart Contracts**: Node.js / JavaScript Chaincode (`chaincode/v2v/javascript/v2vContract.js`)
* **Evaluation Suite**: Python 3 Data Analytics & Visualizations (`test-network/results/analyze.py`)
* **Automation**: Bash orchestration for A/B testing (`test-network/run_full_experiment.sh`)

---

## 🔬 5. Experimental Results (4,000 Transactions)

The WAVE consensus was evaluated side-by-side against a deterministic baseline using a 4,000-transaction simulation (2,000 per mode). The simulation injected randomized failure rates (20%) and variable latencies (50ms - 950ms) to exercise the intelligence of the algorithm.

> **Note:** Absolute latency values (ms) will vary based on your hardware and system load. The **relative differences** between baseline and proposed are what matter for the research conclusions.

### 🏆 Key Findings:

* **Decentralization (Nakamoto Coefficient)**: Jumped from **1 (Baseline)** to **6+ (WAVE)**, representing a significant security upgrade against 51% attacks.
* **Fairness (Gini Coefficient)**: Dropped from **~0.95 (near monopoly)** to **~0.43 (substantially equal)**. Starvation was drastically reduced.
* **Performance Parity**: The algorithmic overhead of probabilistic selection adds only a negligible latency delta (~10-20ms), proving the system scales without performance degradation.
* **Statistical Significance**: The improvements in workload distribution are mathematically significant (Mann-Whitney U Test: **p < 0.05**).

---

## 🚀 6. How to Reproduce the Experiment (For Researchers)

We have packaged the entire experiment into a standalone repository. You do not need to download the full `fabric-samples` repo, but you will need the Fabric binaries and Docker images.

### 📋 Prerequisites

Before starting, ensure you have the following installed on your system:

| Software | Version | Purpose |
|----------|---------|---------|
| **Docker Desktop** | v4.x+ | Runs Fabric containers (peers, orderers, CAs) |
| **Git Bash** | Latest (bundled with Git for Windows) | Shell to execute all bash scripts |
| **Node.js** | v18+ | Required for chaincode (smart contract) execution |
| **Python 3** | 3.8+ with `pip` | For result analysis and graph generation |
| **curl** | Any | For downloading Fabric binaries |
| **jq** | 1.6+ | For JSON processing in anchor peer scripts |

> **⚠️ Important Notes:**
> - All commands below must be run in **Git Bash**, not PowerShell or CMD.
> - Make sure **Docker Desktop is running** before proceeding.
> - On Windows, Docker Desktop must have **WSL 2 backend** enabled (Settings → General → "Use the WSL 2 based engine").

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/Rudra1502/WAVE-Energy-Trading.git
cd WAVE-Energy-Trading
```

---

### Step 2: Download Hyperledger Fabric Binaries & Docker Images

This command downloads the official Fabric v2.5.15 binaries and pulls the matching Docker images:

```bash
curl -sSL https://bit.ly/2ysbOFE | bash -s -- 2.5.15 1.5.12 -s
```

> **What this does:**
> - Downloads `peer`, `orderer`, `configtxgen`, `configtxlator`, `fabric-ca-client`, and other binaries into a `bin/` folder.
> - Pulls Hyperledger Docker images (`fabric-peer`, `fabric-orderer`, `fabric-ca`, `fabric-ccenv`, `fabric-baseos`) and tags them as `latest`.
> - The `-s` flag skips downloading the bloated `fabric-samples` repo (our code is self-contained).

After this completes, verify the images are tagged correctly:

```bash
docker images | grep hyperledger
```

You should see images tagged as both `2.5.15` and `latest`.

---

### Step 3: Install `jq` (JSON Processor)

`jq` is required by the anchor peer configuration scripts. 

**On Windows (Git Bash):**

Download the binary and place it in your `bin/` folder:
```bash
curl -sL https://github.com/jqlang/jq/releases/download/jq-1.7.1/jq-windows-amd64.exe -o bin/jq.exe
```

**On Linux/macOS:**
```bash
# Ubuntu/Debian
sudo apt install jq

# macOS
brew install jq
```

Verify:
```bash
jq --version
```

---

### Step 4: Install Python Dependencies

```bash
cd test-network/results
pip install numpy matplotlib
cd ../..
```

---

### Step 5: Set Up and Deploy the Fabric Network

```bash
cd test-network

# Add Fabric binaries to PATH
export PATH=$(pwd)/../bin:$PATH

# Start the Fabric network (CAs, peers, orderer) and deploy WAVE chaincode
bash setup.sh
```

> **What `setup.sh` does:**
> 1. Tears down any existing network
> 2. Starts 3 Certificate Authority containers (Org1, Org2, Orderer)
> 3. Generates cryptographic certificates for all organizations
> 4. Starts peer and orderer containers
> 5. Creates a channel (`mychannel`) and joins all peers
> 6. Packages, installs, approves, and commits the WAVE chaincode (`v2v`)

**Expected output (last lines):**
```
Committed chaincode definition for chaincode 'v2v' on channel 'mychannel':
Version: 1.0, Sequence: 1, Endorsement Plugin: escc, Validation Plugin: vscc, Approvals: [Org1MSP: true, Org2MSP: true]
✅ All steps completed successfully!
```

---

### Step 6: Run the Full A/B Experiment

```bash
bash run_full_experiment.sh 2000
```

> **What this does:**
> 1. Registers 6 Electric Vehicles (EV1-EV6) on the blockchain
> 2. Registers 50 Validators (V1-V50) with initial reputation scores
> 3. Runs **2,000 Baseline transactions** (deterministic validator selection)
> 4. Resets all validator states for a clean comparison
> 5. Runs **2,000 Proposed WAVE transactions** (adaptive probabilistic selection)
> 6. Generates comparative analysis graphs and statistics
>
> **⏱️ Estimated runtime: ~2-3 hours for 4,000 total transactions**

Results are saved to `test-network/results/`:
- `baseline_log.txt` — Raw transaction logs for baseline mode
- `proposed_log.txt` — Raw transaction logs for proposed WAVE mode
- `metrics_summary.txt` — Comparative statistics table
- `*.png` — Visualization graphs (Lorenz curve, latency distribution, etc.)

---

### Step 7: Tear Down the Network (After Experiments)

```bash
bash network.sh down
```

This stops all Docker containers and removes generated crypto material.

---

## 🔧 7. Troubleshooting

### "Peer binary and configuration files not found"
Make sure you set the PATH before running:
```bash
export PATH=$(pwd)/../bin:$PATH
```

### Docker containers fail to start / "Access is denied"
This is caused by Git Bash's MSYS path conversion. The `network.sh` in this repo already includes the fix (`MSYS_NO_PATHCONV=1` on docker compose commands). If you encounter this, ensure you're using the latest version of `network.sh` from this repository.

### "Error response from daemon: no such volume"
This is a harmless warning during cleanup. It means Docker volumes from a previous run were already removed. Safe to ignore.

### "broken pipe" errors during chaincode install
This indicates a version mismatch between Fabric binaries and Docker images. Make sure to use the exact command in Step 2:
```bash
curl -sSL https://bit.ly/2ysbOFE | bash -s -- 2.5.15 1.5.12 -s
```
Both binaries and Docker images must be **v2.5.15** (not v2.5.0).

### Experiment latency values seem unrealistic (billions of ms)
If using WSL instead of Git Bash, the `date +%s%3N` command may not work correctly. Ensure you are running experiments from **Git Bash**, not WSL.

---

## 📁 8. Repository Structure

```
WAVE-Energy-Trading/
├── README.md                          # This file
├── .gitignore                         # Excludes runtime artifacts from version control
├── chaincode/
│   └── v2v/javascript/
│       ├── v2vContract.js             # Core smart contract (consensus logic)
│       ├── index.js                   # Chaincode entry point
│       └── package.json               # Node.js dependencies
├── bin/                               # ⚠️ Not in repo — downloaded via curl in Step 2
├── config/                            # ⚠️ Not in repo — downloaded via curl in Step 2
└── test-network/
    ├── setup.sh                       # One-click network + chaincode deployment
    ├── run_full_experiment.sh         # Master A/B experiment orchestrator
    ├── network.sh                     # Fabric network lifecycle manager
    ├── network.config                 # Network configuration (DOCKER_SOCK, defaults)
    ├── configtx/                      # Channel & organization definitions
    ├── compose/                       # Docker Compose files for all containers
    ├── organizations/                 # CA server configs (crypto generated at runtime)
    ├── scripts/
    │   ├── run_experiment.sh          # Per-mode transaction runner (baseline/proposed)
    │   ├── deployCC.sh                # Chaincode lifecycle automation
    │   ├── createChannel.sh           # Channel creation and peer joining
    │   └── envVar.sh                  # Peer environment variable configuration
    └── results/
        ├── analyze.py                 # Python analysis & visualization suite
        ├── baseline_log.txt           # ⚠️ Generated at runtime — not in repo
        ├── proposed_log.txt           # ⚠️ Generated at runtime — not in repo
        └── metrics_summary.txt        # ⚠️ Generated at runtime — not in repo
```

---

## 📜 9. License

This project is developed for academic research purposes.

---

## 👥 10. Contributors

- **Rudra1502 (Rudra Suthar)** — Lead Developer & Researcher
