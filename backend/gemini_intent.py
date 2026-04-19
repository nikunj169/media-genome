from google import genai

client = genai.Client(
    api_key="AIzaSyAqgLC2ctHbRTqdu4LddE0Nkf7dIjMMWn0",
    http_options={"api_version": "v1"}
    )

def classify_intent(caption, views, duration, similarity):

    prompt = f"""
    You are detecting piracy in sports videos.

    Similarity Score: {similarity}

    Caption: {caption}
    Views: {views}
    Duration: {duration}

    Rules:
    - If similarity < 0.75 → be cautious (possible false match)
    - If similarity >= 0.75 → strong evidence of duplication

    Classify into:
    - Fan Engagement
    - Active Piracy
    - Ambiguous

    Return ONLY JSON:
    {{
        "intent": "...",
        "confidence": 0-1,
        "reason": "..."
    }}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=prompt,
    )

    return response.text


if __name__ == "__main__":
    result = classify_intent(
        caption="Watch full match HD link in bio",
        views=50000,
        duration=5400
    )

    print(result)