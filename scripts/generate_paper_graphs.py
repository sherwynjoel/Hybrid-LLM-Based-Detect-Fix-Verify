import matplotlib.pyplot as plt
import numpy as np
import os

# Ensure the output directory exists
output_dir = "paper_images"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# ==========================================
# Graph 1: Accuracy Comparison
# ==========================================
def plot_accuracy():
    frameworks = ['VulnRepairEval', 'SecureFixAgent', 'LLM4CVE', 'CodeLlama Only', 'Our Hybrid', 'ChatGPT-4 Only']
    accuracy = [21.7, 32.5, 37.5, 40.0, 55.0, 58.0]
    colors = ['#bdc3c7', '#bdc3c7', '#95a5a6', '#7f8c8d', '#2ecc71', '#3498db'] # Highlight ours in Green

    plt.figure(figsize=(10, 6))
    bars = plt.bar(frameworks, accuracy, color=colors, width=0.6)
    
    # Add values on top
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 1, f'{yval}%', ha='center', va='bottom', fontweight='bold')

    plt.ylabel('Repair Accuracy (%)', fontsize=12)
    plt.title('Framework Accuracy Comparison on CVE Benchmark', fontsize=14, fontweight='bold')
    plt.axhline(y=55.0, color='green', linestyle='--', alpha=0.3) # Reference line for our score
    plt.ylim(0, 70)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    
    # Save
    plt.tight_layout()
    plt.savefig(f"{output_dir}/accuracy_comparison.png", dpi=300)
    print(f"[+] Generated {output_dir}/accuracy_comparison.png")

# ==========================================
# Graph 2: Cost vs Accuracy Trade-off
# ==========================================
def plot_cost_efficiency():
    frameworks = ['CodeLlama (Local)', 'Our Hybrid', 'ChatGPT-4 (Cloud)']
    costs = [0.0, 7.50, 20.00] # Cost per 1000 fixes
    accuracy = [40.0, 55.0, 58.0]
    
    plt.figure(figsize=(10, 6))
    
    # Plot points
    plt.scatter(costs, accuracy, s=1000, c=['#95a5a6', '#2ecc71', '#3498db'], alpha=0.9, edgecolors='black')
    
    # Connect them to show the trend
    plt.plot(costs, accuracy, color='gray', linestyle='--', alpha=0.5, zorder=0)

    # Label points
    for i, txt in enumerate(frameworks):
        plt.annotate(txt, (costs[i], accuracy[i]), xytext=(0, -40), textcoords='offset points', ha='center', fontweight='bold', fontsize=11)
        plt.annotate(f"${costs[i]}", (costs[i], accuracy[i]), xytext=(0, 0), textcoords='offset points', ha='center', color='white', fontweight='bold')

    plt.xlabel('Operational Cost per 1000 Fixes (USD)', fontsize=12)
    plt.ylabel('Accuracy (%)', fontsize=12)
    plt.title('Cost-Efficiency Analysis', fontsize=14, fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xlim(-2, 25)
    plt.ylim(30, 65)

    # Save
    plt.tight_layout()
    plt.savefig(f"{output_dir}/cost_efficiency.png", dpi=300)
    print(f"[+] Generated {output_dir}/cost_efficiency.png")

if __name__ == "__main__":
    plot_accuracy()
    plot_cost_efficiency()
