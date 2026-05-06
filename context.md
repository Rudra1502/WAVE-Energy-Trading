# 🚗⚡ Adaptive Consensus for V2V Energy Trading (Hyperledger Fabric)

---

## 📌 1. Project Overview

This project implements a **blockchain-based Vehicle-to-Vehicle (V2V) energy trading system** using **Hyperledger Fabric**.

The primary focus is **improving the validator selection mechanism (consensus layer)** to achieve:

* Better **fairness**
* Better **decentralization**
* Without degrading **performance (latency)**

---

## 🎯 2. Core Problem

In decentralized systems, **validator selection** determines:

* Who validates transactions
* How load is distributed
* How fair the system is

---

### 🔴 Issue with Existing Approach (Baseline Model)

The baseline model follows a **Proof-of-Reputation (PoR)-like deterministic approach**:

* Always selects **highest reputation validator**
* No randomness
* No latency consideration

---

### ❌ Problems:

* **Validator Monopoly**

  * Same validator repeatedly selected
* **No Fairness**

  * Other validators starve
* **Centralization**

  * System behaves non-decentralized
* **No Adaptivity**

  * Ignores real-time performance

---

## 🟢 3. Proposed Solution (Your Contribution)

We introduce an **Adaptive Probabilistic Consensus Mechanism**.

---

### 🔑 Key Components

---

#### 1. Dynamic Reputation Update

Validator reputation is updated using:

* correctness of validation
* participation (success rate)
* latency performance

---

#### 2. Latency-Aware Scoring

Each validator is scored using:

[
Score = \alpha \cdot reputation + \beta \cdot successRate + \gamma \cdot \frac{1}{1 + latency}
]

Where:

* α, β, γ are weights
* latency is normalized

---

#### 3. Weighted Probabilistic Selection (MAIN NOVELTY)

Instead of picking the highest score:

* Validators are selected **probabilistically**
* Probability ∝ score

---

👉 Result:

* No monopoly
* Fair participation
* Adaptive behavior

---

#### 4. Minimum Probability Floor

* Ensures **low-score validators still get selected occasionally**
* Prevents starvation

---

## ⚙️ 4. System Architecture (Fabric-Based)

---

### 🔹 Platform

* Hyperledger Fabric (permissioned blockchain)
* Chaincode written in **JavaScript**

---

### 🔹 Core Components

---

#### Chaincode File

```
chaincode/v2v/javascript/v2vContract.js
```

---

### 🔹 Key Functions

---

#### `registerEV(evId)`

* Registers Electric Vehicles
* Initializes:

  * reputation
  * trade stats

---

#### `registerValidator(validatorId, energy)`

* Registers validators
* Initializes:

  * reputation
  * success rate
  * latency tracking

---

#### `updateValidatorMetrics(validatorId, latency, isCorrect)`

* Updates:

  * success rate
  * avg latency
  * dynamic reputation

---

#### `selectValidator()`

👉 **MOST IMPORTANT FUNCTION**

Two modes:

---

##### 🔴 Baseline Mode

```js
sort by reputation → pick highest
```

---

##### 🟢 Proposed Mode

```js
weighted probabilistic selection
```

---

#### `completeTransaction()`

Workflow:

1. Select validator
2. Finalize trade
3. Update validator metrics
4. Store transaction

---

## 🧪 5. Experiment Setup

---

### 🔹 Data Generation

Script used:

```
test-network/scripts/experiment.sh
```

---

### 🔹 Process

For each transaction:

1. Invoke `completeTransaction`
2. Measure:

   * validator used
   * latency
3. Log results

---

### 🔹 Output Logs

```
baseline_log.txt
proposed_log.txt
```

---

### 🔹 Log Format

```
Tx X | Validator: Vx | Latency(ms): Y
```

---

## 📊 6. Evaluation Metrics

---

### 🔹 1. Validator Distribution

* Count of how many times each validator is selected

---

### 🔹 2. Jain Fairness Index

[
J = \frac{(\sum x_i)^2}{n \cdot \sum x_i^2}
]

Where:

* (x_i) = validator selection count

---

### 🔹 3. Latency

* Average latency
* Variance
* Stability

---

### 🔹 4. Load Distribution

* % of transactions handled by each validator

---

### 🔹 5. Rank Distribution (NEW)

* Validators sorted by usage
* Shows **drop-off vs smoothness**

---

### 🔹 6. Lorenz Curve (NEW)

* Measures inequality
* Used for fairness validation

---

## 📈 7. Visualization Strategy

---

### 🔹 Graphs Used

---

#### 1. Rank Plot (Primary)

* Shows validator usage vs rank
* Baseline → steep drop
* Proposed → smooth curve

---

#### 2. Lorenz Curve

* Shows fairness
* Baseline → highly skewed
* Proposed → near diagonal

---

#### 3. Latency Comparison

* Smoothed time series
* Shows performance similarity

---

#### 4. Cumulative Curve (optional)

* Shows distribution spread

---

## 🔥 8. Observed Results

---

### 🔴 Baseline

* One validator dominates (~100%)
* Jain Index → very low (~0.02–0.05)
* Centralized behavior

---

### 🟢 Proposed

* Validators distributed evenly
* Jain Index → high (~0.8–0.9)
* Balanced load
* No starvation

---

### ⚡ Latency

* Nearly identical for both models
* No significant overhead introduced

---

## 🧠 9. Key Insight

> Deterministic selection → centralization
> Probabilistic selection → fairness + decentralization

---

## 🎯 10. Final Conclusion

The proposed adaptive consensus mechanism:

* Eliminates validator monopoly
* Improves fairness significantly
* Maintains system performance
* Achieves better decentralization

---

## ⚠️ 11. Limitations

* Small-scale simulation (limited transactions)
* Synthetic latency values
* No adversarial behavior tested

---

## 🚀 12. Future Work

* Larger network simulation
* Real-world latency modeling
* Security integration
* Dynamic weight tuning

---

## 📁 13. Files Required for Reproduction

```
v2vContract.js
experiment.sh
baseline_log.txt
proposed_log.txt
analyze.py
```

---

## 🎯 One-Line Summary

Adaptive probabilistic consensus improves fairness in V2V blockchain systems without degrading performance.
