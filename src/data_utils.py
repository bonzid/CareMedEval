import json
import os

#Loading questions
def load_questions(path="data/questions.json"):
    with open(path,"r",encoding="utf-8") as f:
        return json.load(f)

#Loading articles (txt only)
def load_article_text(article_id,base_path="data/articles/"):
    filepath=os.path.join(base_path,f"{article_id}.txt")
    if os.path.exists(filepath):
        with open(filepath,"r",encoding="utf-8") as f:
            return f.read()
    return ""