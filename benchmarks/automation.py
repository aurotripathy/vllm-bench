# automate
import subprocess
import os
import sys
from itertools import product

# Define the results directory
RESULTS_DIR = "./results-6i-1o-ratio"

def check_results_directory():
    if os.path.exists(RESULTS_DIR):
        print(f"Error: Results directory '{RESULTS_DIR}' already exists.")
        print("Please move or rename the existing directory before running new benchmarks.")
        sys.exit(1)
    else:
        os.makedirs(RESULTS_DIR)
        print(f"Created results directory: {RESULTS_DIR}")

def run_benchmark_with_params(input_len, output_len, concurrency, num_prompts):
    command = [
        "python", "benchmarks/benchmark_serving.py",
        "--host", "localhost",
        "--port", "8000", 
        "--backend", "openai",
        "--endpoint", "/v1/completions",
        "--request-rate", "10",
        "--tokenizer", "meta-llama/Meta-Llama-3-8B-Instruct",
        "--model", "Meta-Llama-3-8B-Instruct",
        "--save-result",
        "--result-dir", RESULTS_DIR,
        "--dataset-name", "sonnet",
        "--dataset-path", "benchmarks/sonnet.txt",
        "--sonnet-input-len", str(input_len),
        "--sonnet-output-len", str(output_len),
        "--max-concurrency", str(concurrency),
        "--num-prompts", str(num_prompts)
    ]

    try:
        print(f"\nRunning benchmark with input_len={input_len}, output_len={output_len}, "
              f"concurrency={concurrency}, num_prompts={num_prompts}")
        subprocess.run(command, check=True)
        print("Benchmark completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Benchmark failed with error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def run_benchmark():
    # Check results directory first
    check_results_directory()
    
    # Define paired input and output lengths
    length_pairs = [
        # (512, 80),
        # (1024, 170),
        (1024+64, 181),
    ]
    concurrency_levels = [1,]
    # concurrency_levels = [1, 2, 4, 8, 16, 32, 64, 128, 256]
    # concurrency_levels = [16, 32, 64, 128, 256]
    num_prompts_levels = [100]
    
    # Run benchmarks for all combinations
    for (input_len, output_len), concurrency, num_prompts in product(
        length_pairs, concurrency_levels, num_prompts_levels
    ):
        run_benchmark_with_params(input_len, output_len, concurrency, num_prompts)

if __name__ == "__main__":
    run_benchmark()
