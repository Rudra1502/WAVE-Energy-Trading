import re
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
import sys

# ==============================
# PARSE LOGS
# ==============================

def parse_log(file):
    validators, latencies = [], []
    with open(file, 'r') as f:
        for line in f:
            m = re.search(r'Validator: (V\d+) \| Latency\(ms\): (\d+)', line)
            if m:
                validators.append(m.group(1))
                latencies.append(int(m.group(2)))
    return validators, latencies

baseline_v, baseline_l = parse_log("baseline_log.txt")
proposed_v, proposed_l = parse_log("proposed_log.txt")

if len(baseline_v) == 0 or len(proposed_v) == 0:
    print("ERROR: No data found in log files!")
    sys.exit(1)

print(f"Parsed {len(baseline_v)} baseline txs, {len(proposed_v)} proposed txs")

# ==============================
# COUNTS
# ==============================

b_counts = Counter(baseline_v)
p_counts = Counter(proposed_v)

all_vals = sorted(set(b_counts) | set(p_counts), key=lambda x: int(x[1:]))

b_vals = np.array([b_counts.get(v, 0) for v in all_vals], dtype=float)
p_vals = np.array([p_counts.get(v, 0) for v in all_vals], dtype=float)

# ==============================
# METRIC FUNCTIONS
# ==============================

def jain(x):
    """Jain Fairness Index: 1/n (worst) to 1.0 (perfect)"""
    if len(x) == 0 or np.sum(x) == 0:
        return 0
    return (np.sum(x)**2) / (len(x) * np.sum(x**2))

def gini(x):
    """Gini Coefficient: 0 (equal) to 1 (monopoly)"""
    x = np.sort(x)
    n = len(x)
    if np.sum(x) == 0:
        return 0
    index = np.arange(1, n + 1)
    return (2 * np.sum(index * x) - (n + 1) * np.sum(x)) / (n * np.sum(x))

def shannon_entropy(x):
    """Shannon Entropy in bits"""
    total = np.sum(x)
    if total == 0:
        return 0
    p = x[x > 0] / total
    return -np.sum(p * np.log2(p))

def normalized_entropy(x):
    """Normalized Shannon Entropy: 0 to 1"""
    n_total = len(x)
    if n_total <= 1:
        return 0
    max_ent = np.log2(n_total)
    return shannon_entropy(x) / max_ent if max_ent > 0 else 0

def nakamoto_coefficient(x):
    """Min validators controlling >50% of selections"""
    sorted_x = np.sort(x)[::-1]
    total = np.sum(x)
    if total == 0:
        return 0
    cumsum = np.cumsum(sorted_x)
    for i, val in enumerate(cumsum):
        if val > total * 0.5:
            return i + 1
    return len(x)

def hhi(x):
    """Herfindahl-Hirschman Index: 1/n (equal) to 1.0 (monopoly)"""
    total = np.sum(x)
    if total == 0:
        return 0
    shares = x / total
    return np.sum(shares ** 2)

def coefficient_of_variation(x):
    """CV = std / mean: 0 (equal) to high (unequal)"""
    x = x[x > 0]
    if len(x) == 0 or np.mean(x) == 0:
        return 0
    return np.std(x) / np.mean(x)

def max_load_ratio(x):
    """max(selections) / mean(selections)"""
    if np.mean(x) == 0:
        return 0
    return np.max(x) / np.mean(x) if np.mean(x) > 0 else 0

def starvation_count(x):
    """Number of validators with 0 selections"""
    return int(np.sum(x == 0))

def validator_rotation(validators):
    """Fraction of consecutive txs using a different validator"""
    if len(validators) <= 1:
        return 0
    changes = sum(1 for i in range(1, len(validators)) if validators[i] != validators[i-1])
    return changes / (len(validators) - 1)

# ==============================
# COMPUTE ALL METRICS
# ==============================

metrics = {
    "Jain Fairness Index": (jain(b_vals), jain(p_vals)),
    "Gini Coefficient": (gini(b_vals), gini(p_vals)),
    "Shannon Entropy (bits)": (shannon_entropy(b_vals), shannon_entropy(p_vals)),
    "Normalized Entropy": (normalized_entropy(b_vals), normalized_entropy(p_vals)),
    "Nakamoto Coefficient": (nakamoto_coefficient(b_vals), nakamoto_coefficient(p_vals)),
    "HHI": (hhi(b_vals), hhi(p_vals)),
    "Coeff. of Variation": (coefficient_of_variation(b_vals), coefficient_of_variation(p_vals)),
    "Max Load Ratio": (max_load_ratio(b_vals), max_load_ratio(p_vals)),
    "Starvation Count": (starvation_count(b_vals), starvation_count(p_vals)),
    "Validator Rotation": (validator_rotation(baseline_v), validator_rotation(proposed_v)),
    "Avg Latency (ms)": (np.mean(baseline_l), np.mean(proposed_l)),
    "Latency Std Dev (ms)": (np.std(baseline_l), np.std(proposed_l)),
}

# ==============================
# PRINT METRICS TABLE
# ==============================

print("\n" + "=" * 65)
print(f"{'Metric':<28} {'Baseline':>15} {'Proposed':>15}")
print("=" * 65)
for name, (bv, pv) in metrics.items():
    bv_f = float(bv)
    pv_f = float(pv)
    if name in ("Starvation Count", "Nakamoto Coefficient"):
        print(f"{name:<28} {int(bv_f):>15d} {int(pv_f):>15d}")
    else:
        print(f"{name:<28} {bv_f:>15.4f} {pv_f:>15.4f}")
print("=" * 65)

# ==============================
# STATISTICAL TEST
# ==============================

try:
    from scipy.stats import mannwhitneyu
    stat, p_value = mannwhitneyu(b_vals, p_vals, alternative='two-sided')
    print(f"\nMann-Whitney U Test:")
    print(f"  U-statistic: {stat:.2f}")
    print(f"  p-value: {p_value:.6e}")
    if p_value < 0.05:
        print("  Result: SIGNIFICANT (p < 0.05) ✅")
    else:
        print("  Result: Not significant (p >= 0.05)")
except ImportError:
    print("\n[WARN] scipy not installed — skipping statistical test")
    print("  Install with: pip install scipy")
    p_value = None

# ==============================
# SORT FOR RANK PLOT
# ==============================

b_sorted = np.sort(b_vals)[::-1]
p_sorted = np.sort(p_vals)[::-1]

b_pct = b_sorted / np.sum(b_sorted) * 100 if np.sum(b_sorted) > 0 else b_sorted
p_pct = p_sorted / np.sum(p_sorted) * 100 if np.sum(p_sorted) > 0 else p_sorted

# ==============================
# GRAPH 1: RANK PLOT
# ==============================

plt.figure(figsize=(8, 4))
plt.plot(b_pct, label="Baseline", linewidth=1.8, marker='o', markersize=3, color='#e74c3c')
plt.plot(p_pct, label="Proposed", linewidth=1.8, marker='o', markersize=3, color='#2ecc71')
plt.xlabel("Validator Rank (sorted by usage)")
plt.ylabel("Selection Share (%)")
plt.title("Validator Selection Rank Distribution")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("rank_plot.png", dpi=150, bbox_inches='tight')
plt.close()

# ==============================
# GRAPH 2: LORENZ CURVE
# ==============================

def lorenz_curve(values):
    sorted_vals = np.sort(values)
    cum_vals = np.cumsum(sorted_vals)
    return np.insert(cum_vals / cum_vals[-1], 0, 0) if cum_vals[-1] > 0 else cum_vals

b_lorenz = lorenz_curve(b_vals)
p_lorenz = lorenz_curve(p_vals)

x_b = np.linspace(0, 1, len(b_lorenz))
x_p = np.linspace(0, 1, len(p_lorenz))

plt.figure(figsize=(5, 5))
plt.plot(x_b, b_lorenz, label=f"Baseline (Gini={gini(b_vals):.3f})", linewidth=1.8, color='#e74c3c')
plt.plot(x_p, p_lorenz, label=f"Proposed (Gini={gini(p_vals):.3f})", linewidth=1.8, color='#2ecc71')
plt.plot([0, 1], [0, 1], linestyle='--', color='gray', label="Perfect Equality", alpha=0.7)
plt.fill_between(x_b, b_lorenz, np.linspace(0, 1, len(b_lorenz)), alpha=0.1, color='#e74c3c')
plt.xlabel("Cumulative Validators (fraction)")
plt.ylabel("Cumulative Selection Share")
plt.title("Lorenz Curve — Fairness Comparison")
plt.legend(loc='upper left')
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("lorenz.png", dpi=150, bbox_inches='tight')
plt.close()

# ==============================
# GRAPH 3: LATENCY COMPARISON
# ==============================

def moving_avg(x, w=20):
    return np.convolve(x, np.ones(w) / w, mode='valid')

b_smooth = moving_avg(baseline_l)
p_smooth = moving_avg(proposed_l)

plt.figure(figsize=(9, 4))
plt.plot(b_smooth, label="Baseline", linestyle='--', linewidth=1.5, color='#1f77b4', alpha=0.9)
plt.plot(p_smooth, label="Proposed", linestyle='-', linewidth=1.5, color='#ff7f0e', alpha=0.9)
plt.axhline(np.mean(baseline_l), linestyle=':', color='#1f77b4', alpha=0.4, label=f"Baseline Mean ({np.mean(baseline_l):.0f}ms)")
plt.axhline(np.mean(proposed_l), linestyle=':', color='#ff7f0e', alpha=0.4, label=f"Proposed Mean ({np.mean(proposed_l):.0f}ms)")
plt.xlabel("Transaction (smoothed, window=20)")
plt.ylabel("End-to-End Latency (ms)")
plt.title("Latency Comparison (Fabric Round-Trip)")
plt.legend()
plt.grid(alpha=0.25)
plt.tight_layout()
plt.savefig("latency.png", dpi=150, bbox_inches='tight')
plt.close()

# ==============================
# GRAPH 4: VALIDATOR DISTRIBUTION BAR CHART
# ==============================

x_idx = np.arange(len(all_vals))
width = 0.35

fig, ax = plt.subplots(figsize=(14, 5))
ax.bar(x_idx - width/2, b_vals, width, label='Baseline', color='#e74c3c', alpha=0.8)
ax.bar(x_idx + width/2, p_vals, width, label='Proposed', color='#2ecc71', alpha=0.8)
ax.set_xlabel('Validator')
ax.set_ylabel('Selection Count')
ax.set_title('Validator Selection Distribution')
ax.set_xticks(x_idx)
ax.set_xticklabels(all_vals, rotation=90, fontsize=7)
ax.legend()
ax.grid(alpha=0.2, axis='y')
plt.tight_layout()
plt.savefig("distribution.png", dpi=150, bbox_inches='tight')
plt.close()

# ==============================
# GRAPH 5: CUMULATIVE DISTRIBUTION
# ==============================

b_cum = np.cumsum(b_sorted) / np.sum(b_sorted) if np.sum(b_sorted) > 0 else b_sorted
p_cum = np.cumsum(p_sorted) / np.sum(p_sorted) if np.sum(p_sorted) > 0 else p_sorted

plt.figure(figsize=(8, 4))
plt.step(range(len(b_cum)), b_cum, where='post', linestyle='--', linewidth=1.5, label="Baseline", color='#e74c3c')
plt.plot(p_cum, linewidth=1.5, label="Proposed", color='#2ecc71')
plt.xlabel("Validators (sorted by usage)")
plt.ylabel("Cumulative Share")
plt.title("Cumulative Validator Selection")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("cumulative.png", dpi=150, bbox_inches='tight')
plt.close()

# ==============================
# GRAPH 6: METRICS COMPARISON BAR CHART
# ==============================

fig, axes = plt.subplots(2, 3, figsize=(14, 8))

comparison_metrics = [
    ("Jain Fairness\nIndex", "Jain Fairness Index", "higher=better"),
    ("Gini\nCoefficient", "Gini Coefficient", "lower=better"),
    ("Normalized\nEntropy", "Normalized Entropy", "higher=better"),
    ("Nakamoto\nCoefficient", "Nakamoto Coefficient", "higher=better"),
    ("HHI", "HHI", "lower=better"),
    ("Validator\nRotation", "Validator Rotation", "higher=better"),
]

for idx, (label, key, note) in enumerate(comparison_metrics):
    ax = axes[idx // 3][idx % 3]
    bv, pv = metrics[key]
    bars = ax.bar(["Baseline", "Proposed"], [bv, pv], color=['#e74c3c', '#2ecc71'], alpha=0.85)
    ax.set_title(f"{label}\n({note})", fontsize=10)
    ax.grid(alpha=0.2, axis='y')
    
    # Add headroom so text doesn't hit the ceiling
    max_val = max(bv, pv)
    ax.set_ylim(0, max_val * 1.25 if max_val > 0 else 1)
    
    for bar, val in zip(bars, [bv, pv]):
        fmt = f"{val:.4f}" if isinstance(val, float) else f"{val}"
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02 * max_val,
                fmt, ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.suptitle("Evaluation Metrics Comparison", fontsize=14, fontweight='bold')
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig("metrics_comparison.png", dpi=150, bbox_inches='tight')
plt.close()

# ==============================
# SAVE METRICS TO FILE
# ==============================

with open("metrics_summary.txt", "w") as f:
    f.write("=" * 65 + "\n")
    f.write(f"{'Metric':<28} {'Baseline':>15} {'Proposed':>15}\n")
    f.write("=" * 65 + "\n")
    for name, (bv, pv) in metrics.items():
        bv_f = float(bv)
        pv_f = float(pv)
        if name in ("Starvation Count", "Nakamoto Coefficient"):
            f.write(f"{name:<28} {int(bv_f):>15d} {int(pv_f):>15d}\n")
        else:
            f.write(f"{name:<28} {bv_f:>15.4f} {pv_f:>15.4f}\n")
    f.write("=" * 65 + "\n")
    if p_value is not None:
        f.write(f"\nMann-Whitney U p-value: {p_value:.6e}\n")
    f.write(f"\nBaseline transactions: {len(baseline_v)}\n")
    f.write(f"Proposed transactions: {len(proposed_v)}\n")
    f.write(f"Total validators registered: {len(all_vals)}\n")

print("\n✅ All graphs saved:")
print("  - rank_plot.png")
print("  - lorenz.png")
print("  - latency.png")
print("  - distribution.png")
print("  - cumulative.png")
print("  - metrics_comparison.png")
print("  - metrics_summary.txt")