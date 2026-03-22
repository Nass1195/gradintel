from datasets import load_dataset
from app.services.summarization.summary import summarize_file
from app.models import bertEvaluation
from bert_score import score


async def summary_eval() -> list[bertEvaluation]:
    dataset = load_dataset("ccdv/pubmed-summarization", "section", split="test")

    evaluations: list[bertEvaluation] = [] 

    for data in dataset:
        article = data.get("article")
        abstract = data.get("abstract")
        summary = await summarize_file(article)

        evaluation = bert_evaluation(abstract, summary)
        evaluations.append(evaluation)
        print(evaluation)


    return evaluations



def bert_evaluation(original_text: str, generated_summary: str) -> bertEvaluation:
    P, R, F1 = score([generated_summary], [original_text], lang="en")

    return bertEvaluation(precision=P.item(), recall=R.item(), f1_score=F1.item())
