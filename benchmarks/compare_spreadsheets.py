import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os
import re

def extract_label(filename):
    # Extract the configuration part from the filename
    # Example: FP8-1xH100-results-8B-llama-date-2025-03-26 -> FP8-1xH100
    match = re.search(r'([A-Z0-9-]+-\d+x[A-Z0-9]+)', filename)
    if match:
        return match.group(1)
    return os.path.basename(filename)

def get_row_with_higher_input(df, target_concurrency):
    # Get all rows with target concurrency
    matching_rows = df[df['concurrency'] == target_concurrency]
    if len(matching_rows) == 0:
        raise ValueError(f"No rows found with concurrency = {target_concurrency}")
    
    # Return the row with highest total_input_tokens
    return matching_rows.loc[matching_rows['total_input_tokens'].idxmax()]

def compare_spreadsheets(file1, file2, target_concurrency=256):
    # Read the spreadsheets
    df1 = pd.read_excel(file1)
    df2 = pd.read_excel(file2)
    
    # Find rows with target concurrency and highest input tokens
    row1 = get_row_with_higher_input(df1, target_concurrency)
    row2 = get_row_with_higher_input(df2, target_concurrency)
    
    # Get all columns
    columns = df1.columns.tolist()
    
    # Create bar plot
    plt.figure(figsize=(12, 6))
    
    # Set up bar positions
    x = range(len(columns))
    width = 0.35
    
    # Extract labels from filenames
    label1 = extract_label(file1)
    label2 = extract_label(file2)
    
    # Create bars
    plt.bar([i - width/2 for i in x], [row1[col] for col in columns], width, label=label1)
    plt.bar([i + width/2 for i in x], [row2[col] for col in columns], width, label=label2)
    
    # Customize the plot
    plt.xlabel('Metrics')
    plt.ylabel('Values')
    plt.title(f'Performance Comparison: {label1} vs {label2}\nConcurrency = {target_concurrency}')
    plt.xticks(x, columns, rotation=45)
    plt.legend(title='Configuration')
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # Save the plot
    output_dir = os.path.dirname(file1)
    plt.savefig(os.path.join(output_dir, f'comparison_{label1}_vs_{label2}_concurrency_{target_concurrency}.png'))
    plt.close()
    
    # Print the comparison
    print(f"\nComparison at Concurrency = {target_concurrency}:")
    print("-" * 100)
    print(f"{'Metric':<20} {label1:<15} {label2:<15} {'Difference':<15}")
    print("-" * 100)
    
    # List of metrics to show differences for
    diff_metrics = ['mean_ttft_ms', 'mean_tpot_ms', 'mean_itl_ms', 'output_throughput']
    
    for col in columns:
        val1 = row1[col]
        val2 = row2[col]
        if col in diff_metrics:
            diff = val1 - val2
            diff_str = f"{diff:.1f}"
        else:
            diff_str = ''
        print(f"{col:<20} {val1:<15.2f} {val2:<15.2f} {diff_str:<15}")

def main():
    parser = argparse.ArgumentParser(description='Compare rows with specific concurrency from two spreadsheets')
    parser.add_argument('file1', type=str, help='First spreadsheet file path')
    parser.add_argument('file2', type=str, help='Second spreadsheet file path')
    parser.add_argument('--concurrency', type=int, default=256, help='Target concurrency value (default: 256)')
    args = parser.parse_args()
    
    compare_spreadsheets(args.file1, args.file2, args.concurrency)

if __name__ == "__main__":
    main() 