furiosa-llm serve Llama-3.1-70B-Instruct-FP8 \
            --devices "npu:0,npu:1,npu:2,npu:3" \
            -pp 4 \
            --enable-auto-tool-choice \
            --tool-call-parser llama3_json \
            --chat-template vllm-bench/rndg-server/chat-template.txt
