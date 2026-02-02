
import matplotlib.pyplot as plt
import numpy as np

# Data for Vulnerability Distribution
labels = ['SQL Injection', 'XSS', 'Path Traversal', 'Hardcoded Secrets']
sizes = [35, 25, 20, 20]
colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']

# Create Pie Chart
plt.figure(figsize=(6, 4))
plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
plt.axis('equal') 
plt.title('Vulnerability Distribution')
plt.tight_layout()
plt.savefig('vulnerability_distribution.png', dpi=300)
print("Generated vulnerability_distribution.png")

# Data for Severity Breakdown
severity_labels = ['Critical', 'High', 'Medium', 'Low']
severity_counts = [5, 12, 8, 3]
severity_colors = ['#d62728', '#ff7f0e', '#f7b731', '#2ca02c']

# Create Bar Chart
plt.figure(figsize=(6, 4))
bars = plt.bar(severity_labels, severity_counts, color=severity_colors)
plt.ylabel('Count')
plt.title('Severity Level Breakdown')
plt.bar_label(bars)
plt.tight_layout()
plt.savefig('severity_breakdown.png', dpi=300)
print("Generated severity_breakdown.png")
