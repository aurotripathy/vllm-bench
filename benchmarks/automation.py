"""
This script automates vLLM benchmark testing for LLaMA models (8B and 70B) by running various configurations 
of input/output token ratios (2:1, 3:1, 6:1) and concurrency levels (1-128, in powers of 2). It creates a dated results 
directory, runs benchmarks using the sonnet dataset, and saves the results in JSON format for each configuration.
"""

# automate
from datetime import datetime
import subprocess
import os
import sys
import argparse
from itertools import product

# Define model size to tokenizer mapping
LLAMA_MODELS = {
    "8B": "meta-llama/Meta-Llama-3-8B-Instruct",
    "70B": "meta-llama/Meta-Llama-3-70B-Instruct"
}

def check_results_directory(results_dir):
    """Check if the results directory already exists. If it does, exit the program."""
    if os.path.exists(results_dir):
        print(f"Error: Results directory '{results_dir}' already exists.")
        print("Please move or rename the existing directory before running new benchmarks.")
        sys.exit(1)
    else:
        os.makedirs(results_dir)
        print(f"Created results directory: {results_dir}")

def run_benchmark_with_params(input_len, output_len, concurrency, num_prompts, model_size, results_dir, request_rate):
    if model_size not in LLAMA_MODELS:
        print(f"Error: Invalid model size '{model_size}'. Available sizes: {', '.join(LLAMA_MODELS.keys())}")
        sys.exit(1)

    model_name = LLAMA_MODELS[model_size]
    command = [
        "python", "benchmarks/benchmark_serving.py",
        "--host", "localhost",
        "--port", "8000", 
        "--backend", "openai",
        "--endpoint", "/v1/completions",
        "--request-rate", str(request_rate),
        "--tokenizer", model_name,
        "--model", model_name,
        "--save-result",
        "--result-dir", results_dir,
        "--dataset-name", "sonnet",
        "--dataset-path", "benchmarks/sonnet.txt",
        "--sonnet-input-len", str(input_len),
        "--sonnet-output-len", str(output_len),
        "--max-concurrency", str(concurrency),
        "--num-prompts", str(num_prompts)
    ]

    try:
        print(f"\nRunning benchmark with input_len={input_len}, output_len={output_len}, "
              f"concurrency={concurrency}, num_prompts={num_prompts}, model={model_name}")
        subprocess.run(command, check=True)
        print("Benchmark completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Benchmark failed with error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def run_benchmark(model_size, request_rate):
    # Create results directory with model size and request rate in name
    request_rate_str = "inf" if request_rate == float('inf') else str(request_rate)
    results_dir = f"./results-{model_size}-llama-qps-{request_rate_str}-{datetime.now().strftime('%Y-%m-%d')}"
    check_results_directory(results_dir)
    
    # Define paired input and output lengths in ratios 2:1 and 6:1
    length_pairs = [
        # 2: 1 ratio
        # (2048, 1024),
        (1024, 512),
        (512, 256),
        # 3: 1 ratio
        (1024, 341),
        (512, 170),
        # 6: 1 ratio
        # (512, 85),
        (1536, 256),
        (1024, 170),
    ]
    concurrency_levels = [1, 2, 4, 8, 16, 32, 64, 128,]
    num_prompts_levels = [100]
    
    # Run benchmarks for all combinations
    for (input_len, output_len), concurrency, num_prompts in product(
        length_pairs, concurrency_levels, num_prompts_levels
    ):
        run_benchmark_with_params(input_len, output_len, concurrency, num_prompts, model_size, results_dir, request_rate)

def main():
    parser = argparse.ArgumentParser(description='Run benchmarks for different LLaMA model sizes')
    parser.add_argument('model_size', type=str, choices=['8B', '70B'],
                      help='Size of the LLaMA model to benchmark (8B, or 70B)')
    parser.add_argument('request_rate', type=float,
                      help='Request rate for the benchmark (use "inf" for infinite rate)')
    args = parser.parse_args()
    
    # Convert string "inf" to float('inf') if provided
    request_rate = float('inf') if str(args.request_rate).lower() == 'inf' else args.request_rate
    run_benchmark(args.model_size, request_rate)

if __name__ == "__main__":
    main()
