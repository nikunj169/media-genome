from main_pipeline import analyze_video
import json
import re


def analyze_video_intent(platform_name):
    """
    FULL AI PIPELINE (temporary demo version)
    """

    print(f"🤖 [REAL AI] Processing {platform_name} video...")

    try:
        # 🔥 TEMP HARD-CODED INPUT (for demo)
        video_path = "videos/edited_clip.mp4"
        caption = "Watch full match HD link in bio"
        views = 50000
        duration = 5400

        result = analyze_video(
            video_path=video_path,
            caption=caption,
            views=views,
            duration=duration
        )

        # 🔹 No match
        if not result["match"]:
            return "Fan Engagement"

        # 🔹 Extract Gemini JSON
        json_text = re.search(r"\{.*\}", result["intent_analysis"], re.DOTALL).group()
        data = json.loads(json_text)

        intent = data.get("intent", "Ambiguous")

        print(f"✅ Final Decision: {intent}")
        return intent

    except Exception as e:
        print("❌ AI Error:", e)
        return "Ambiguous"