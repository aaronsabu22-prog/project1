from transformers import pipeline

summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-12-6"
)


def generate_summary(text):

    if len(text) > 3000:
        text = text[:3000]

    result = summarizer(
        text,
        max_length=180,
        min_length=60,
        do_sample=False
    )

    return result[0]["summary_text"]