import evaluate

def evaluate_summary(original_text: str, generated_summary: str):

    rouge = evaluate.load("rouge")

    results = rouge.compute(
        predictions=[generated_summary],
        references=[original_text],
        use_stemmer=True
    )

    return results
