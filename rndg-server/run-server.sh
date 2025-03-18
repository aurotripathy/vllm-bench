furiosa-llm serve ./Llama-3.1-8B-Instruct-FP8 \
	    --devices "npu:0" \
	    --enable-auto-tool-choice \
	    --tool-call-parser llama3_json \
	    --chat-template chat-template.txt \
	    --enable-payload-logging
