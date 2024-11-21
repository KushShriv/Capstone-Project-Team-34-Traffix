# import os
# import re
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns

# # Define the path to the files
# file_paths = [
#     'C:/Users/kusha/Downloads/Capstone/Everything-Server/simulation/results/5s_label.txt',
#     'C:/Users/kusha/Downloads/Capstone/Everything-Server/simulation/results/10s_label.txt',
#     'C:/Users/kusha/Downloads/Capstone/Everything-Server/simulation/results/15s_label.txt',
#     'C:/Users/kusha/Downloads/Capstone/Everything-Server/simulation/results/30s_label.txt',
#     'C:/Users/kusha/Downloads/Capstone/Everything-Server/simulation/results/manual_label.txt'
# ]

# sns.set_theme(style="whitegrid")

# # Define a function to extract metrics from each file
# def extract_metrics(file_path):
#     metrics = {}
#     with open(file_path, 'r') as file:
#         content = file.read()

#         # Extract key metrics using regular expressions
#         metrics['Dataset'] = os.path.basename(file_path).replace('.txt', '')
#         metrics['Our_Model_Better'] = int(re.search(r"Times Our Model is Better:\s+(\d+)", content).group(1))
#         metrics['Default_Better'] = int(re.search(r"Times Default Timing is Better:\s+(\d+)", content).group(1))
#         metrics['Our_Model_Cleared_Percent'] = float(re.search(r"Percentage Our Model Cleared:\s+([\d.]+)", content).group(1))
#         metrics['Default_Cleared_Percent'] = float(re.search(r"Percentage Default Timing Cleared:\s+([\d.]+)", content).group(1))
#         metrics['Our_Model_Avg_Time_Cleared'] = float(re.search(r"When Our Model Cleared - Average Time Taken:\s+([\d.]+)", content).group(1))
#         metrics['Default_Avg_Time_Cleared'] = float(re.search(r"When Default Timing Cleared - Average Time Taken:\s+([\d.]+)", content).group(1))
#         metrics['Our_Model_Congested'] = int(re.search(r"Times Ours Congested:\s+(\d+)", content).group(1))
#         metrics['Default_Congested'] = int(re.search(r"Times Default Congested:\s+(\d+)", content).group(1))
#         metrics['Our_Score'] = int(re.search(r"Our Score:\s+(\d+)", content).group(1))

#     return metrics

# # Extract metrics from each file and create a DataFrame
# data = [extract_metrics(file_path) for file_path in file_paths]
# df = pd.DataFrame(data)

# # Plot 1: Times Our Model vs Default Better
# plt.figure(figsize=(10, 6))
# sns.barplot(x='Dataset', y='Our_Model_Better', data=df, color='blue', label='Our Model Better')
# sns.barplot(x='Dataset', y='Default_Better', data=df, color='orange', label='Default Better', alpha=0.6)
# plt.ylabel('Times Model Performed Better')
# plt.title('Model Performance Comparison')
# plt.legend()
# plt.show()

# # Plot 2: Clearing Efficiency (Percentage of Times Cleared)
# plt.figure(figsize=(10, 6))
# df_melted = df.melt(id_vars='Dataset', value_vars=['Our_Model_Cleared_Percent', 'Default_Cleared_Percent'],
#                     var_name='Model', value_name='Cleared_Percent')
# sns.barplot(x='Dataset', y='Cleared_Percent', hue='Model', data=df_melted)
# plt.ylabel('Percentage of Times Cleared')
# plt.title('Clearing Efficiency Comparison')
# plt.show()

# # Plot 3: Average Time to Clear (Comparison)
# plt.figure(figsize=(10, 6))
# df_melted_time = df.melt(id_vars='Dataset', value_vars=['Our_Model_Avg_Time_Cleared', 'Default_Avg_Time_Cleared'],
#                          var_name='Model', value_name='Avg_Time_Cleared')
# sns.barplot(x='Dataset', y='Avg_Time_Cleared', hue='Model', data=df_melted_time)
# plt.ylabel('Average Time to Clear')
# plt.title('Average Time to Clear Comparison')
# plt.show()

# # Plot 4: Congestion Handling Comparison
# plt.figure(figsize=(10, 6))
# sns.barplot(x='Dataset', y='Our_Model_Congested', data=df, color='blue', label='Our Model Congested')
# sns.barplot(x='Dataset', y='Default_Congested', data=df, color='orange', label='Default Congested', alpha=0.6)
# plt.ylabel('Number of Times Congested')
# plt.title('Congestion Handling Comparison')
# plt.legend()
# plt.show()

# # Plot 5: Total Score Comparison
# plt.figure(figsize=(10, 6))
# sns.barplot(x='Dataset', y='Our_Score', data=df, color='green')
# plt.ylabel('Total Score')
# plt.title('Total Score Comparison for Each Model')
# plt.show()


import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Apply a theme for consistency
sns.set_theme(style="whitegrid")

# Define the path to the files
file_paths = [
    'C:/Users/kusha/Downloads/Capstone/Everything-Server/simulation/results/5s_label.txt',
    'C:/Users/kusha/Downloads/Capstone/Everything-Server/simulation/results/10s_label.txt',
    'C:/Users/kusha/Downloads/Capstone/Everything-Server/simulation/results/15s_label.txt',
    'C:/Users/kusha/Downloads/Capstone/Everything-Server/simulation/results/30s_label.txt',
    'C:/Users/kusha/Downloads/Capstone/Everything-Server/simulation/results/manual_label.txt'
]

# Define a function to extract metrics from each file
def extract_metrics(file_path):
    metrics = {}
    with open(file_path, 'r') as file:
        content = file.read()

        # Extract key metrics using regular expressions
        metrics['Dataset'] = os.path.basename(file_path).replace('.txt', '')
        metrics['Our_Model_Better'] = int(re.search(r"Times Our Model is Better:\s+(\d+)", content).group(1))
        metrics['Default_Better'] = int(re.search(r"Times Default Timing is Better:\s+(\d+)", content).group(1))
        metrics['Our_Model_Cleared_Percent'] = float(re.search(r"Percentage Our Model Cleared:\s+([\d.]+)", content).group(1))
        metrics['Default_Cleared_Percent'] = float(re.search(r"Percentage Default Timing Cleared:\s+([\d.]+)", content).group(1))
        metrics['Our_Model_Avg_Time_Cleared'] = float(re.search(r"When Our Model Cleared - Average Time Taken:\s+([\d.]+)", content).group(1))
        metrics['Default_Avg_Time_Cleared'] = float(re.search(r"When Default Timing Cleared - Average Time Taken:\s+([\d.]+)", content).group(1))
        metrics['Our_Model_Congested'] = int(re.search(r"Times Ours Congested:\s+(\d+)", content).group(1))
        metrics['Default_Congested'] = int(re.search(r"Times Default Congested:\s+(\d+)", content).group(1))
        metrics['Our_Score'] = int(re.search(r"Our Score:\s+(\d+)", content).group(1))

    return metrics

# Extract metrics from each file and create a DataFrame
data = [extract_metrics(file_path) for file_path in file_paths]
df = pd.DataFrame(data)

# Set color palette for consistent colors across plots
palette = sns.color_palette("Paired")
base_path1 = 'C:/Users/kusha/Downloads/Capstone/Everything-Server/simulation/graphs/final/'
base_path2 = 'C:/Users/kusha/Downloads/Capstone/Everything-Server/simulation/results/finalGraphs/'

# Plot 1: Times Our Model vs Default Better
plt.figure(figsize=(10, 6))
sns.barplot(x='Dataset', y='Our_Model_Better', data=df, color=palette[0], label='Our Model Better')
sns.barplot(x='Dataset', y='Default_Better', data=df, color=palette[1], label='Default Better', alpha=0.7)
for i, v in enumerate(df['Our_Model_Better']):
    plt.text(i, v + 50, str(v), ha='center', color=palette[0], fontweight='bold')
for i, v in enumerate(df['Default_Better']):
    plt.text(i, v + 50, str(v), ha='center', color=palette[1], fontweight='bold')
plt.ylabel('Times Model Performed Better')
plt.title('Model Performance Comparison', fontsize=14)
plt.legend()
plt.tight_layout()
plt.savefig(base_path1 + 'Model_Performance_Comparison.png')
plt.savefig(base_path2 + 'Model_Performance_Comparison.png')

# Plot 2: Clearing Efficiency (Percentage of Times Cleared)
plt.figure(figsize=(10, 6))
df_melted = df.melt(id_vars='Dataset', value_vars=['Our_Model_Cleared_Percent', 'Default_Cleared_Percent'],
                    var_name='Model', value_name='Cleared_Percent')
sns.barplot(x='Dataset', y='Cleared_Percent', hue='Model', data=df_melted, palette=palette[:2])
for i, v in enumerate(df['Our_Model_Cleared_Percent']):
    plt.text(i, v + 0.02, f"{v:.2f}", ha='right', color=palette[0], fontweight='bold')
for i, v in enumerate(df['Default_Cleared_Percent']):
    plt.text(i, v + 0.02, f"{v:.2f}", ha='left', color=palette[1], fontweight='bold')
plt.ylabel('Percentage of Times Cleared')
plt.title('Clearing Efficiency Comparison', fontsize=14)
plt.legend(title='Model')
plt.tight_layout()
plt.savefig(base_path1 + 'Clearing_Efficiency_Comparison.png')
plt.savefig(base_path2 + 'Clearing_Efficiency_Comparison.png')

# Plot 3: Average Time to Clear (Comparison)
plt.figure(figsize=(10, 6))
df_melted_time = df.melt(id_vars='Dataset', value_vars=['Our_Model_Avg_Time_Cleared', 'Default_Avg_Time_Cleared'],
                         var_name='Model', value_name='Avg_Time_Cleared')
sns.barplot(x='Dataset', y='Avg_Time_Cleared', hue='Model', data=df_melted_time, palette=palette[:2])
for i, v in enumerate(df['Our_Model_Avg_Time_Cleared']):
    plt.text(i, v + 100, f"{int(v)}", ha='right', color=palette[0], fontweight='bold')
for i, v in enumerate(df['Default_Avg_Time_Cleared']):
    plt.text(i, v + 100, f"{int(v)}", ha='left', color=palette[1], fontweight='bold')
plt.ylabel('Average Time to Clear')
plt.title('Average Time to Clear Comparison', fontsize=14)
plt.legend(title='Model')
plt.tight_layout()
plt.savefig(base_path1 + 'Average_Time_to_Clear_Comparison.png')
plt.savefig(base_path2 + 'Average_Time_to_Clear_Comparison.png')

# Plot 4: Congestion Handling Comparison
plt.figure(figsize=(10, 6))
sns.barplot(x='Dataset', y='Our_Model_Congested', data=df, color=palette[0], label='Our Model Congested')
sns.barplot(x='Dataset', y='Default_Congested', data=df, color=palette[1], label='Default Congested', alpha=0.7)
for i, v in enumerate(df['Our_Model_Congested']):
    plt.text(i, v + 10, str(v), ha='center', color=palette[0], fontweight='bold')
for i, v in enumerate(df['Default_Congested']):
    plt.text(i, v + 10, str(v), ha='center', color=palette[1], fontweight='bold')
plt.ylabel('Number of Times Congested')
plt.title('Congestion Handling Comparison', fontsize=14)
plt.legend()
plt.tight_layout()
plt.savefig(base_path1 + 'Congestion_Handling_Comparison.png')
plt.savefig(base_path2 + 'Congestion_Handling_Comparison.png')

# Plot 5: Total Score Comparison
plt.figure(figsize=(10, 6))
sns.barplot(x='Dataset', y='Our_Score', data=df, color=palette[2])
for i, v in enumerate(df['Our_Score']):
    plt.text(i, v + 100, str(v), ha='center', color=palette[2], fontweight='bold')
plt.ylabel('Total Score')
plt.title('Total Score Comparison for Each Model', fontsize=14)
plt.tight_layout()
plt.savefig(base_path1 + 'Total_Score_Comparison.png')
plt.savefig(base_path2 + 'Total_Score_Comparison.png')
