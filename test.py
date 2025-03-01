import yt_dlp
import requests
import re
import json

video_url = "https://www.youtube.com/watch?v=CevxZvSJLk8&pp=ygUNZW5nbGlzaCBtdXNpYw%3D%3D"

# Options for yt-dlp
options = {
    "writesubtitles": True,
    "writeautomaticsub": True,
    "skip_download": True,
    "quiet": True,
}

# Extract subtitles
with yt_dlp.YoutubeDL(options) as ydl:
    info = ydl.extract_info(video_url, download=False)
    subtitles = info.get("subtitles") or {}
    auto_captions = info.get("automatic_captions") or {}

    key_lists = list(subtitles.keys())
    pattern = r"en-[\w-]+"
    matches = [word for word in key_lists if re.match(pattern, word)]

    subtitle_url = None
    if "en" in subtitles:
        subtitle_url = subtitles["en"][0]["url"]
    elif matches:
        subtitle_url = subtitles[matches[0]][0]["url"]
    elif "en" in auto_captions:
        subtitle_url = auto_captions["en"][0]["url"]

    if subtitle_url:
        print(f"Subtitle URL: {subtitle_url}")

        response = requests.get(subtitle_url)
        if response.status_code == 200:
            subtitle_data = None
            try:
                subtitle_data = response.json()
                with open("sub.json", "w", encoding="utf-8") as f:
                    json.dump(subtitle_data,f,indent=4, ensure_ascii=False)
                print(json.dumps(subtitle_data,indent=4, ensure_ascii=False))
            except:
                with open("subtitles.vtt", "w", encoding="utf-8") as f:
                    f.write(subtitle_data)
                    print("✅ subtitles.vtt created successfully.")

                # Save VTT data as JSON
                json_data = {"vtt_content": subtitle_data}  
                with open("sub.json", "w", encoding="utf-8") as f:
                    json.dump(json_data, f, indent=4, ensure_ascii=False)
                  # Display the raw subtitle content
                    print("Subtitles saved as subtitles.vtt")
    else:
        print("No subtitles found.")
