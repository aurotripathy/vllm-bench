

# uses AsyncOpenAI(base_url="http://localhost:8000/v1/", api_key="EMPTY")

prompt = """<|begin_of_text|><|start_header_id|>user<|end_header_id|>

Pick as many lines as you can from these poem lines:
These poor rude lines of thy deceased lover,
When, in disgrace with fortune and men's eyes,
Much liker than your painted counterfeit:
O, change thy thought, that I may change my mind!
Yet, do thy worst, old Time: despite thy wrong,
As he takes from you, I engraft you new.
When to the sessions of sweet silent thought
And sable curls all silver'd o'er with white;
But thy eternal summer shall not fade
O, therefore, love, be of thyself so wary
Nor can thy shame give physic to my grief;
Nor draw no lines there with thine antique pen;
Without this, folly, age and cold decay:
And night doth nightly make grief's strength seem stronger.
O, learn to read what silent love hath writ:<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
    
print(f'Prompt:\n {prompt}')
print(f'\n\nPrompt length (in characters): {len(prompt)}')

#count the imput tokens
import tiktoken
encoding = tiktoken.encoding_for_model("gpt-4o")
print(f"\n\nInput tokens count reported by tiktoken: {len(encoding.encode(prompt))}")

from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B")
tokens = tokenizer.tokenize(prompt)
num_input_tokens = len(tokens)
print(f"Input tokens count reported by HF transformers: {num_input_tokens}")

import asyncio
from openai import AsyncOpenAI
client = AsyncOpenAI(base_url="http://localhost:8000/v1/", api_key="EMPTY")

async def main():
    async_response = await client.completions.create(
        model="EMPTY",
        prompt=prompt,
        max_tokens=600,
        temperature=1.0,
        stream=True,
        stream_options={"include_usage": True},
        # logprobs=False,
        # early_stopping=False,
    )

    output_tokens_count = 0
    gen_tokens = []
    async for chunk in async_response:
        gen_tokens.append(chunk.choices[0].text)
        output_tokens_count += 1
        if chunk.usage is not None:
            print(f'usage: {chunk.usage}')
    print(f"\n\nOutput tokens count: {output_tokens_count}")  
    print(f"\n\nGenerated tokens: {''.join(gen_tokens)}")
asyncio.run(main())

