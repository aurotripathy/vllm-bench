# python benchmarks/benchmark_serving.py \
#        --backend openai \
#        --endpoint /v1/completions \
#        --tokenizer meta-llama/Meta-Llama-3-8B-Instruct \
#        --model meta-llama/Meta-Llama-3-8B-Instruct \
#        --result-dir results \
#        --dataset-name sonnet \
#        --dataset-path benchmarks/sonnet.txt \
#        --sonnet-input-len 200 \
#        --sonnet-output-len 500 \
#        --sonnet-prefix-len 24 \
#        --num-prompts 1

python benchmarks/benchmark_serving.py \
       --backend openai \
       --endpoint /v1/completions \
       --tokenizer meta-llama/Meta-Llama-3-8B-Instruct \
       --model EMPTY \
       --result-dir results \
       --dataset-name sonnet \
       --dataset-path benchmarks/sonnet.txt \
       --sonnet-input-len 200 \
       --sonnet-output-len 500 \
       --sonnet-prefix-len 24 \
       --num-prompts 100
