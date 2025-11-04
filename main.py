from src.model_utils import load_model
from src.data_utils import load_questions
from src.evaluate import evaluate

if __name__=="__main__":
    llm,tokenizer,sampling_params=load_model()
    questions=load_questions("data/questions.json")

    print("=== Model evaluation ===",flush=True)
    evaluate(
        llm,
        tokenizer,
        sampling_params,
        questions,
        article_path="data/articles/",
        with_think=False #Set to True to enable <think> justification extraction, for reasoning models
    )