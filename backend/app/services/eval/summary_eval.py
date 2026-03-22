import evaluate
from datasets import load_dataset
from app.services.summarization.summary import summarize_file
from bert_score import score


async def summary_eval():
    dataset = load_dataset("ccdv/pubmed-summarization", "section", split="test")

    for data in dataset:
        article = data.get("article")
        abstract = data.get("abstract")
        summary = await summarize_file(article)

        score = rouge_evaluation(abstract, summary)
        bert_evaluation(abstract, summary)

        print(score)
        break


def rouge_evaluation(original_text: str, generated_summary: str):

    rouge = evaluate.load("rouge")

    results = rouge.compute(
        predictions=[generated_summary],
        references=[original_text],
        use_stemmer=True
    )

    return results

def bert_evaluation(original_text: str, generated_summary: str):
    P, R, F1 = score([generated_summary], [original_text], lang="en")

    print("Precision:", P.mean().item())
    print("Recall:", R.mean().item())
    print("F1:", F1.mean().item())