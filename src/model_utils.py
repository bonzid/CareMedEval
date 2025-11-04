from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

def load_model():
    model_name="Qwen/Qwen3-8B"
    print("Loading tokenizer...",flush=True)
    tokenizer=AutoTokenizer.from_pretrained(model_name)

    print("Initializing the model with vLLM...",flush=True)
    sampling_params=SamplingParams(temperature=0.0,top_p=1.0,max_tokens=8000)
    llm=LLM(model=model_name,dtype="float16",enforce_eager=True)

    print("vLLM model ready",flush=True)
    return llm,tokenizer,sampling_params