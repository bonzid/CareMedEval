#Construction du prompt
def build_prompt(full_article,question_data,tokenizer,max_prompt_tokens=31000):
    question=question_data["question"]
    options=question_data["answers"]
    choices="\n".join([f"{k.upper()}) {v}" for k,v in options.items()])

    #Prompt template
    prefix=(
        "Vous êtes un médecin capable d'interpréter rigoureusement les données d'études médicales. "
        "À partir de l'article donné, répondez à la question à choix multiples suivante. "
        "Indiquez uniquement la ou les lettres correspondant aux bonnes réponses parmi : A, B, C, D, E. "
        "Votre réponse doit respecter le format exact suivant : une ou plusieurs lettres, séparées par des virgules (ex. : B, E).\n"
        "Article :\n"
    )
    suffix=f"\n\nQuestion :\n{question}\n\nChoix de réponses :\n{choices}\n\nVotre réponse : "

    #Calculates the tokens for the static parts of the prompt
    static_tokens=tokenizer.encode(prefix+suffix,truncation=False)
    remaining_tokens=max_prompt_tokens-len(static_tokens)

    #Truncates the article if necessary
    article_tokens=tokenizer.encode(full_article,truncation=False)
    truncated_article_tokens=article_tokens[:remaining_tokens]
    truncated_article=tokenizer.decode(truncated_article_tokens,skip_special_tokens=True)

    return prefix+truncated_article+suffix