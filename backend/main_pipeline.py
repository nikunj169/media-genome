from search_index import search_video, classify_similarity
from gemini_intent import classify_intent


def analyze_video(video_path, caption, views, duration):

    asset_id, score = search_video(video_path)
    match_type = classify_similarity(score)

    # ❌ No match → ignore
    if match_type == "NO_MATCH":
        return {
            "match": False,
            "reason": "No similar master asset"
        }

    # ⚠️ Weak match → downgrade confidence
    if match_type == "WEAK_MATCH":
        intent_result = classify_intent(caption, views, duration, score)

        return {
            "match": True,
            "match_type": "WEAK",
            "asset_id": asset_id,
            "similarity": score,
            "note": "Low confidence match",
            "intent_analysis": intent_result
        }

    # ✅ Strong match → full confidence
    if match_type == "MATCH":
        intent_result = classify_intent(caption, views, duration, score)

        return {
            "match": True,
            "match_type": "STRONG",
            "asset_id": asset_id,
            "similarity": score,
            "intent_analysis": intent_result
        }


if __name__ == "__main__":
    result = analyze_video(
        video_path="videos/edited_clip.mp4",
        caption="Watch full match HD link in bio",
        views=50000,
        duration=5400
    )

    print(result)