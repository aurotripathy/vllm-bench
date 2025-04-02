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

def run_benchmark_with_params(input_len, output_len, concurrency, num_prompts, model_size, results_dir):
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
        "--request-rate", "10",
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

def run_benchmark(model_size):
    # Create results directory with model size in name
    results_dir = f"./results-{model_size}-llama-date-{datetime.now().strftime('%Y-%m-%d')}"
    check_results_directory(results_dir)
    
    # Define paired input and output lengths in ratios 2:1 and 6:1
    length_pairs = [
        # 2: 1 ratio
        (1024, 512),
        (512, 256),
        # 3: 1 ratio
        (1024, 341),
        (512, 170),
        # 6: 1 ratio
        (1024, 170),
        (512, 85)
    ]
    concurrency_levels = [1, 2, 4, 8, 16, 32, 64, 128,]
    num_prompts_levels = [100]
    
    # Run benchmarks for all combinations
    for (input_len, output_len), concurrency, num_prompts in product(
        length_pairs, concurrency_levels, num_prompts_levels
    ):
        run_benchmark_with_params(input_len, output_len, concurrency, num_prompts, model_size, results_dir)

def main():
    parser = argparse.ArgumentParser(description='Run benchmarks for different LLaMA model sizes')
    parser.add_argument('model_size', type=str, choices=['8B', '70B'],
                      help='Size of the LLaMA model to benchmark (8B, or 70B)')
    args = parser.parse_args()
    
    run_benchmark(args.model_size)

if __name__ == "__main__":
    main()
