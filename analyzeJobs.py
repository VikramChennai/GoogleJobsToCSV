import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
from itertools import combinations

def analyze_tools_frequency():
    # Load the CSV file
    df = pd.read_csv('job_details.csv')
    
    # Check if the 'Tools/Software' column exists
    if 'Tools/Software' not in df.columns:
        print("Error: 'Tools/Software' column not found in the CSV file.")
        return
    
    # Combine all tools/software into a single list
    all_tools = []
    tool_sets = []
    for tools_string in df['Tools/Software'].dropna():
        tools = [tool.strip() for tool in tools_string.split(',')]
        all_tools.extend(tools)
        tool_sets.append(set(tools))
    
    # Count the frequency of each tool
    tool_counts = Counter(all_tools)
    
    # Sort the tools by frequency in descending order
    sorted_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Get the top 20 tools for better visualization
    top_20_tools = dict(sorted_tools[:20])
    
    # Create a bar chart
    plt.figure(figsize=(12, 6))
    plt.bar(top_20_tools.keys(), top_20_tools.values())
    plt.title('Top 20 Tools/Software Frequency in Job Listings')
    plt.xlabel('Tools/Software')
    plt.ylabel('Frequency')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Save the chart as an image file
    plt.savefig('tools_frequency_chart.png')
    print("Chart saved as 'tools_frequency_chart.png'")
    
    # Print the results
    print("\nTool/Software Frequency Analysis:")
    print("----------------------------------")
    for tool, count in sorted_tools:
        print(f"{tool}: {count}")

    # Analyze tool combinations
    combination_counts = Counter()
    max_combo_size = min(5, max(len(tool_set) for tool_set in tool_sets))  # Limit to 5 or max set size
    
    for size in range(2, max_combo_size + 1):
        for tool_set in tool_sets:
            for combo in combinations(tool_set, size):
                combination_counts[tuple(sorted(combo))] += 1
    
    # Sort combinations by frequency
    sorted_combinations = sorted(combination_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Print top 20 tool combinations
    print("\nTop 20 Tool Combinations:")
    print("-------------------------")
    for combo, count in sorted_combinations[:20]:
        print(f"{' + '.join(combo)}: {count}")

    # Create a set of top tools based on individual frequency and combination frequency
    top_tools = set()
    for tool, _ in sorted_tools[:10]:  # Add top 10 individual tools
        top_tools.add(tool)
    for combo, _ in sorted_combinations[:10]:  # Add tools from top 10 combinations
        top_tools.update(combo)
    
    print("\nRecommended Tools for Integration/Support:")
    print("------------------------------------------")
    for i, tool in enumerate(top_tools, 1):
        print(f"{i}. {tool}")

if __name__ == "__main__":
    analyze_tools_frequency()
