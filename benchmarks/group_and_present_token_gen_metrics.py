"""
This script processes JSON benchmark files from a specified folder, grouping them by token patterns 
(e.g., 'itkns-1024-otkns-170'). It extracts key metrics (throughput, latency, token counts) for each 
concurrency level (1-128) and organizes them into an Excel file with separate tabs for each concurrency, 
making it easy to compare performance across different configurations.
"""

import glob
import os
import sys
import json
import pandas as pd
import argparse
from collections import defaultdict

def extract_metrics_from_json(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
        # Extract metrics from the JSON structure
        metrics = {
            'total_input_tokens': data.get('total_input_tokens', 0),
            'total_output_tokens': data.get('total_output_tokens', 0),
            'mean_ttft_ms': data.get('mean_ttft_ms', 0),
            'mean_tpot_ms': data.get('mean_tpot_ms', 0),
            'mean_itl_ms': data.get('mean_itl_ms', 0),
            'output_throughput': data.get('output_throughput', 0),
            'total_token_throughput': data.get('total_token_throughput', 0)
        }
        
        # Print the file name and metrics for debugging
        print(f"\nProcessing file: {os.path.basename(json_file)}")
        for metric, value in metrics.items():
            print(f"{metric}: {value}")
        
        return metrics

def group_files_by_token_ratios(folder_path):
    # Define the token patterns to look for
    token_patterns = [
        'itkns-1024-otkns-170',
        'itkns-1024-otkns-341',
        'itkns-1024-otkns-512',
        'itkns-512-otkns-170',
        'itkns-512-otkns-256',
        'itkns-512-otkns-85'
    ]
    
    # Initialize a dictionary to store file groups
    file_groups = defaultdict(list)
    
    # Scan the folder for JSON files
    json_files = glob.glob(os.path.join(folder_path, '*.json'))
    
    # Group files by token pattern
    for pattern in token_patterns:
        matching_files = [f for f in json_files if pattern in os.path.basename(f)]
        if len(matching_files) != 8:
            print(f"Warning: Found {len(matching_files)} files for pattern {pattern}, expected 8")
        file_groups[pattern] = sorted(matching_files)
    
    return file_groups

def create_metrics_dataframe(file_groups, concurrency):
    # Define metrics to extract
    metrics = [
        'total_input_tokens',
        'total_output_tokens',
        'mean_ttft_ms',
        'mean_tpot_ms',
        'mean_itl_ms',
        'output_throughput',
        'total_token_throughput'
    ]
    
    # Create DataFrame with metrics as rows and token patterns as columns
    df = pd.DataFrame(index=metrics)
    
    # Extract metrics for each token pattern
    for pattern, files in file_groups.items():
        # Find file with matching concurrency
        matching_file = next((f for f in files if f'concurrency{concurrency}' in os.path.basename(f)), None)
        if matching_file:
            print(f"Found matching file: {matching_file}")
            metrics_data = extract_metrics_from_json(matching_file)
            # Format values to two decimal places
            df[pattern] = [round(metrics_data[metric], 2) for metric in metrics]
    
    return df

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Process benchmark JSON files and create metrics comparison Excel file.')
    parser.add_argument('folder_path', type=str, help='Path to the folder containing JSON benchmark files')
    args = parser.parse_args()
    
    # Check if folder exists
    if not os.path.exists(args.folder_path):
        print(f"Error: Folder '{args.folder_path}' does not exist")
        sys.exit(1)
    
    # Group the files
    file_groups = group_files_by_token_ratios(args.folder_path)
    for pattern, files in file_groups.items():
        print(f"{pattern}:")
        for file in files:
            print(f"    {file}")
    
    # Create Excel writer
    output_file = os.path.join(args.folder_path, '2-to-1_3-to-1_6-to-1_metrics_comparison.xlsx')
    writer = pd.ExcelWriter(output_file, engine='openpyxl')
    
    # Create a sheet for each concurrency
    concurrencies = [1, 2, 4, 8, 16, 32, 64, 128]
    for concurrency in concurrencies:
        df = create_metrics_dataframe(file_groups, concurrency)
        df.to_excel(writer, sheet_name=f'concurrency={concurrency}')
    
    # Save the Excel file
    writer.close()
    print(f"\nMetrics comparison saved to: {output_file}")

if __name__ == "__main__":
    main() 