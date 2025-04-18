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
import openpyxl.styles
from datetime import datetime
from utils.plot_utils import plot_output_throughput, plot_mean_ttft

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
    
    # Mapping of original patterns to display names
    pattern_display_names = {
        'itkns-1024-otkns-170': 'in 1024 : out 170',
        'itkns-1024-otkns-341': 'in 1024 : out 341',
        'itkns-1024-otkns-512': 'in 1024 : out 512',
        'itkns-512-otkns-170': 'in 512 : out 170',
        'itkns-512-otkns-256': 'in 512 : out 256',
        'itkns-512-otkns-85': 'in 512 : out 85'
    }
    
    # Extract metrics for each token pattern
    for pattern, files in file_groups.items():
        # Find file with matching concurrency
        matching_file = next((f for f in files if f'concurrency{concurrency}' in os.path.basename(f)), None)
        if matching_file:
            print(f"Found matching file: {matching_file}")
            metrics_data = extract_metrics_from_json(matching_file)
            # Format values to two decimal places and use display name for column
            df[pattern_display_names[pattern]] = [round(metrics_data[metric], 2) for metric in metrics]
    
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
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(args.folder_path, f'2-to-1_3-to-1_6-to-1_metrics_comparison_{timestamp}.xlsx')
    writer = pd.ExcelWriter(output_file, engine='openpyxl')
    
    # Create a sheet for each concurrency
    dataframes = {}
    concurrencies = [1, 2, 4, 8, 16, 32, 64, 128]
    for concurrency in concurrencies:
        df = create_metrics_dataframe(file_groups, concurrency)
        df.to_excel(writer, sheet_name=f'concurrency={concurrency}')
        dataframes[concurrency] = df
        
        # Get the worksheet
        worksheet = writer.sheets[f'concurrency={concurrency}']
        
        # Add concurrency value in cell A1
        worksheet.cell(row=1, column=1, value=f'Concurrency = {concurrency}')
        
        # Set column widths
        worksheet.column_dimensions['A'].width = 25  # Metric names column
        for col in range(2, len(df.columns) + 2):  # Data columns
            worksheet.column_dimensions[chr(64 + col)].width = 20
            
        # Set row heights
        worksheet.row_dimensions[1].height = 40  # Header row
        for row in range(2, len(df.index) + 2):  # Data rows
            worksheet.row_dimensions[row].height = 20
            
        # Enable text wrapping for header cells
        for col in range(1, len(df.columns) + 2):
            cell = worksheet.cell(row=1, column=col)
            cell.alignment = openpyxl.styles.Alignment(wrap_text=True, vertical='center')
    
    # Save the Excel file
    writer.close()
    print(f"\nMetrics comparison saved to: {output_file}")
    
    # Create and save the throughput plot as a separate PNG file
    plot_file = os.path.join(args.folder_path, f'throughput_plot_{timestamp}.png')
    plot_output_throughput(dataframes, plot_file)
    print(f"\nThroughput plot saved to: {plot_file}")
    
    # Create and save the TTFT plot as a separate PNG file
    ttft_plot_file = os.path.join(args.folder_path, f'ttft_plot_{timestamp}.png')
    plot_mean_ttft(dataframes, ttft_plot_file)
    print(f"\nTTFT plot saved to: {ttft_plot_file}")

if __name__ == "__main__":
    main() 