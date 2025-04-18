import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def plot_output_throughput(dataframes, output_file):
    plt.figure(figsize=(12, 8))
    
    # Get all concurrencies and sort them
    concurrencies = sorted(dataframes.keys())
    
    # Get the first dataframe to get column names (token patterns)
    first_df = next(iter(dataframes.values()))
    token_patterns = first_df.columns
    
    # Create x-axis values (concurrencies)
    x = np.array(concurrencies)
    
    # Plot each token pattern
    for pattern in token_patterns:
        # Collect throughput values for each concurrency
        y = [df.loc['output_throughput', pattern] for df in dataframes.values()]
        line = plt.plot(x, y, marker='o', label=pattern)
        
        # Add labels for concurrencies 64 and 128
        for concurrency in [64, 128]:
            if concurrency in concurrencies:
                idx = concurrencies.index(concurrency)
                plt.annotate(f'{y[idx]:.0f}',
                            xy=(x[idx], y[idx]),
                            xytext=(5, 5),
                            textcoords='offset points',
                            color=line[0].get_color())
    
    plt.title('Output Throughput vs Concurrency')
    plt.xlabel('Concurrency')
    plt.ylabel('Output Throughput')
    
    # Set x-axis ticks to actual concurrency values
    plt.xticks(concurrencies)
    
    # Set y-axis ticks in increments of 100
    y_min, y_max = plt.ylim()
    y_min = 0  # Start from 0
    y_max = int((y_max // 100) + 1) * 100  # Round up to nearest 100
    y_ticks = np.arange(y_min, y_max + 100, 100)  # Create ticks every 100 units
    plt.yticks(y_ticks)
    plt.ylim(y_min, y_max)  # Set the y-axis limits
    plt.grid(True, which='both', linestyle='--', alpha=0.7)
    
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    # Save the plot to a file
    plt.savefig(output_file, bbox_inches='tight', dpi=300)
    plt.close()


def plot_mean_ttft(dataframes, output_file):
    plt.figure(figsize=(12, 8))
    
    # Get all concurrencies and sort them
    concurrencies = sorted(dataframes.keys())
    
    # Get the first dataframe to get column names (token patterns)
    first_df = next(iter(dataframes.values()))
    token_patterns = first_df.columns
    
    # Create x-axis values (concurrencies)
    x = np.array(concurrencies)
    
    # Plot each token pattern
    for pattern in token_patterns:
        # Collect mean_ttft_ms values for each concurrency
        y = [df.loc['mean_ttft_ms', pattern] for df in dataframes.values()]
        line = plt.plot(x, y, marker='o', label=pattern)
        
        # Add labels for concurrencies 64 and 128
        for concurrency in [64, 128]:
            if concurrency in concurrencies:
                idx = concurrencies.index(concurrency)
                plt.annotate(f'{y[idx]:.0f}',
                            xy=(x[idx], y[idx]),
                            xytext=(5, 5),
                            textcoords='offset points',
                            color=line[0].get_color())
    
    plt.title('Mean Time to First Token vs Concurrency')
    plt.xlabel('Concurrency')
    plt.ylabel('Mean TTFT (ms)')
    
    # Set x-axis ticks to actual concurrency values
    plt.xticks(concurrencies)
    
    # Set y-axis ticks in increments of 50ms
    y_min, y_max = plt.ylim()
    y_min = 0  # Start from 0
    y_max = int((y_max // 50) + 1) * 50  # Round up to nearest 50
    y_ticks = np.arange(y_min, y_max + 50, 50)  # Create ticks every 50ms
    plt.yticks(y_ticks)
    plt.ylim(y_min, y_max)  # Set the y-axis limits
    plt.grid(True, which='both', linestyle='--', alpha=0.7)
    
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    # Save the plot to a file
    plt.savefig(output_file, bbox_inches='tight', dpi=300)
    plt.close() 