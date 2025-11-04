import re

#Evaluation metrics for multiple-choice questions with multiple correct answers
def exact_match(pred,gold):
    return set(pred.lower())==set(gold.lower())


def f1_score(pred,gold):
    pred_tokens=set(pred.lower())
    gold_tokens=set(gold.lower())
    tp=len(pred_tokens & gold_tokens)
    precision=tp/len(pred_tokens) if pred_tokens else 0
    recall=tp/len(gold_tokens) if gold_tokens else 0
    return 2*precision*recall/(precision+recall) if (precision+recall) else 0

def clean_model_answer(response):
    #Extracts letters A-E from the model response
    extracted=re.findall(r"\b([a-eA-E])\b",response)
    #Normalizes and removes duplicates
    return "".join(sorted(set(letter.lower() for letter in extracted)))

#Adjusted LCA score for multiple-choice questions
def lca_score(pred,gold,essential=None,unacceptable=None):
    """
    Computes an adjusted LCA score for a multiple-choice question.

    - If an unacceptable answer is present => score = 0
    - If an essential answer is missing => score = 0
    - Otherwise, penalize proportionally for divergences (false positives and false negatives)

    Inputs:
        pred: str, model's answers as a string (e.g., "ace")
        gold: list of str, correct answers (e.g., ["a", "c", "e"])
        essential: list of str, essential answers (e.g., ["c"])
        unacceptable: list of str, unacceptable answers (e.g., ["b"])
    Returns:
        float, score between 0.0 and 1.0
    """
    if not pred.strip():
        return 0.0

    pred_set=set(pred.lower())
    gold_set=set(a.lower() for a in gold)
    essential_set=set(a.lower() for a in (essential or []))
    unacceptable_set=set(a.lower() for a in (unacceptable or []))

    #Unacceptable answers check
    if pred_set & unacceptable_set:
        return 0.0

    #Essential answers check
    if not essential_set.issubset(pred_set):
        return 0.0

    #Divergences count
    false_positives=pred_set-gold_set
    false_negatives=gold_set-pred_set
    divergences=len(false_positives)+len(false_negatives)

    if divergences==0:
        return 1.0
    elif divergences==1:
        return 0.5
    elif divergences==2:
        return 0.2
    else:
        return 0.0

#Hamming score for multiple-choice questions: intersection over union gold/pred
def hamming_score(pred,gold):
    pred_set=set(pred.lower())
    gold_set=set(gold.lower())
    union=pred_set | gold_set
    if not union:
        return 1.0  #Both empty
    return len(pred_set & gold_set)/len(union)