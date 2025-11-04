import json
import re
from collections import defaultdict
from .data_utils import load_article_text
from .prompt_utils import build_prompt
from .metrics import exact_match,f1_score,hamming_score,lca_score,clean_model_answer

#Model evaluation
def evaluate(llm,tokenizer,sampling_params,questions,article_path,with_think=False):
    emr_total=0
    f1_total=0
    lca_total=0
    hamming_total=0
    count=0
    invalid_count=0
    extracted_from_invalid=0

    label_scores=defaultdict(lambda: {"emr":[],"f1":[],"lca":[],"hamming":[]})
    results_list=[]

    for q in questions:
        article=load_article_text(q["id_article"],article_path)
        if not article:
            continue

        prompt=build_prompt(article,q,tokenizer)
        if with_think:
            prompt=prompt
        else:
            prompt="/no_think\n"+prompt
            
        outputs=llm.generate(prompts=[prompt],sampling_params=sampling_params)
        model_raw_output=outputs[0].outputs[0].text.strip()
        if with_think:
            justification_match=re.search(r"<think>\s*(.*?)\s*</think>",model_raw_output, re.DOTALL | re.IGNORECASE)
            justification_model=justification_match.group(1).strip() if justification_match else ""
        else:
            justification_model=""

        print(f"\nQuestion {count+1}/{len(questions)} traitée",flush=True)
        print(f"\nRaw model output: {model_raw_output}",flush=True)

        is_valid_format=bool(re.match(r"^([a-eA-E](?:[,\s]+[a-eA-E])*)$",model_raw_output.strip()))
        if not is_valid_format:
            invalid_count+=1
            cleaned=clean_model_answer(model_raw_output)
            if cleaned:
                extracted_from_invalid+=1

        model_answer=clean_model_answer(model_raw_output)
        model_answer=model_answer.lower().strip().replace(",","").replace(" ","")
        gold_answer="".join(q["correct_answers"]).lower()

        emr=exact_match(model_answer,gold_answer)
        f1=f1_score(model_answer,gold_answer)
        hamming=hamming_score(model_answer,gold_answer)
        lca=lca_score(model_answer,gold_answer)

        emr_total+=int(emr)
        f1_total+=f1
        hamming_total+=hamming
        lca_total+=lca
        count+=1

        for label in q["labels"]:
            label=str(label)
            label_scores[label]["emr"].append(int(emr))
            label_scores[label]["f1"].append(f1)
            label_scores[label]["lca"].append(lca)
            label_scores[label]["hamming"].append(hamming)

        print(f"\nQ: {q['question']}\nPredicted: {model_answer} | Gold: {gold_answer} | EMR: {emr} | F1: {f1:.2f} | Hamming: {hamming:.2f} | LCA-score: {lca:.2f}", flush=True)

        #Add results per question
        results_list.append({
        "question_id": q.get("id"),
        "article_id": q.get("id_article"),
        "article_date": q.get("article_date"),
        "exam_date": q.get("date_exam"),
        "question": q["question"],
        "raw_output": model_raw_output,
        "predicted_answers": list(model_answer.lower()),
        "gold_answers": q["correct_answers"],
        "justification_model": justification_model,
        "justification_human": q.get("justification"),
        "emr": round(emr,2),
        "f1": round(f1,2),
        "hamming": round(hamming,2),
        "lca": lca
    })

    #Results summary
    summary={
        "summary_global":{
            "total_evaluated": count,
            "emr_avg": round(emr_total/count,2) if count>0 else 0,
            "f1_avg": round(f1_total/count,2) if count>0 else 0,
            "hamming_avg": round(hamming_total/count,2) if count>0 else 0,
            "lca_avg": round(lca_total/count,2) if count>0 else 0,
            "malformatted_percentage": round((invalid_count/count)*100,2) if count>0 else 0,
            "extraction_rate": round((extracted_from_invalid/invalid_count*100),2) if invalid_count>0 else 0
        },
        "summary_by_label": {}
    }

    for label in sorted(label_scores.keys()):
        label_emr_avg=sum(label_scores[label]["emr"])/len(label_scores[label]["emr"])
        label_f1_avg=sum(label_scores[label]["f1"])/len(label_scores[label]["f1"])
        label_lca_avg=sum(label_scores[label]["lca"])/len(label_scores[label]["lca"])
        label_hamming_avg=sum(label_scores[label]["hamming"])/len(label_scores[label]["hamming"])
        summary["summary_by_label"][label] = {
            "emr_avg": round(label_emr_avg,2),
            "f1_avg": round(label_f1_avg,2),
            "hamming_avg": round(label_hamming_avg,2),
            "lca_avg": round(label_lca_avg,2)
        }

    #Save results to a JSON file
    with open("evaluation_results.json","w",encoding="utf-8") as f:
        json.dump({
            "results": results_list,
            "summary": summary
        }, f,indent=2,ensure_ascii=False)

    print("\n=== Results saved in 'evaluation_results.json' ===",flush=True)