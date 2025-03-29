import os
from glob import glob
import argparse
import json
import pandas as pd
from openpyxl.utils import get_column_letter

def analyze_and_present_results(json_files, output_prefix, results_dir):
    if not json_files:
        print(f"No files to analyze for {output_prefix}")
        return
    
    # List to store all results
    results_data = []
    
    # Read each JSON file
    for json_file in json_files:
        with open(json_file, 'r') as f:
            data = json.load(f)
            
            # Calculate token ratio (input/output)
            token_ratio = round(data['total_input_tokens'] / data['total_output_tokens'], 2)
            
            # Extract the metrics we want and round numeric values
            result = {
                'total_input_tokens': data['total_input_tokens'],
                'total_output_tokens': data['total_output_tokens'],
                'token_ratio': token_ratio,
                'concurrency': int(data['max_concurrency']),  # Ensure concurrency is integer
                'mean_ttft_ms': round(data['mean_ttft_ms'], 2),
                'mean_tpot_ms': round(data['mean_tpot_ms'], 2),
                'mean_itl_ms': round(data['mean_itl_ms'], 2),
                'output_throughput': round(data['output_throughput'], 2)
            }
            results_data.append(result)
    
    # Convert to DataFrame
    df = pd.DataFrame(results_data)
    
    # Sort DataFrame by concurrency only (as integer)
    df = df.sort_values('concurrency')
    
    # Create spreadsheets directory if it doesn't exist
    spreadsheets_dir = os.path.join(os.path.dirname(results_dir), 'spreadsheets')
    os.makedirs(spreadsheets_dir, exist_ok=True)
    
    # Get the directory name for the prefix
    dir_name = os.path.basename(os.path.normpath(results_dir))
    
    # Create output filename using both prefixes
    output_file = os.path.join(spreadsheets_dir, f"{output_prefix}_{dir_name}_benchmark_results.xlsx")
    
    # Create Excel writer object
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Write only the raw data
        df.to_excel(writer, sheet_name='Raw Data', index=False, float_format="%.2f")
        
        # Auto-adjust Raw Data sheet
        worksheet = writer.sheets['Raw Data']
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(str(col))
            )
            column_letter = get_column_letter(idx + 1)
            worksheet.column_dimensions[column_letter].width = max_length + 2
    
    print(f"Results have been written to {output_file}")

def categorize_measurement_files(results_dir):
    # Get all JSON files in the results directory
    json_files = glob(os.path.join(results_dir, "*.json"))
    
    if not json_files:
        print(f"No JSON files found in directory: {results_dir}")
        return
    
    # Lists to store categorized files
    list1_files = []  # 1024/512 and 512/256 combinations
    list2_files = []  # 1024/170 and 512/85 combinations
    
    # Categorize files based on their names
    for json_file in json_files:
        filename = os.path.basename(json_file)
        
        # Check for list1 combinations
        if ("1024" in filename and "512" in filename) or \
           ("512" in filename and "256" in filename):
            list1_files.append(json_file)
        
        # Check for list2 combinations
        if ("1024" in filename and "170" in filename) or \
           ("512" in filename and "85" in filename):
            list2_files.append(json_file)
    
    # Sort both lists
    list1_files.sort()
    list2_files.sort()
    
    return list1_files, list2_files

def main():
    parser = argparse.ArgumentParser(description='Categorize benchmark result files based on token combinations')
    parser.add_argument('results_dir', type=str, help='Directory containing the JSON result files')
    args = parser.parse_args()
    
    # Categorize the files
    list1_files, list2_files = categorize_measurement_files(args.results_dir)
    
    print("\nList 1 files:")
    print('\n'.join(f"- {file}" for file in list1_files))
    
    print("\nList 2 files:")
    print('\n'.join(f"- {file}" for file in list2_files))
    
    # Analyze and present results for each list
    print("\nAnalyzing List 1 results...")
    analyze_and_present_results(list1_files, "1024_512_512_256", args.results_dir)
    
    print("\nAnalyzing List 2 results...")
    analyze_and_present_results(list2_files, "1024_170_512_85", args.results_dir)

if __name__ == "__main__":
    main() 