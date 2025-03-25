
# note the server script 
# furiosa-llm serve ./Llama-3.1-8B-Instruct-FP8 --devices "npu:0" --enable-auto-tool-choice --tool-call-parser llama3_json --chat-template chat-template.txt -tp 8

python benchmarks/pure_client_benchmark_serving.py \
       --host localhost \
       --port 8000 \
       --backend openai \
       --endpoint /v1/completions \
       --request-rate 10 \
       --tokenizer meta-llama/Meta-Llama-3-8B-Instruct \
       --model Meta-Llama-3-8B-Instruct \
       --save-result \
       --result-dir ./results \
       --dataset-name sonnet \
       --dataset-path benchmarks/sonnet.txt \
       --sonnet-input-len 1024 \
       --sonnet-output-len 70 \
       --max-concurrency 1 \
       --num-prompts 1
