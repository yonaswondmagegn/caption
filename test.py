import yt_dlp
import requests
import json

video_url = "https://www.youtube.com/watch?v=vdzyESNzlQg"

# Options for yt-dlp


options = {
    'proxy': proxy,
    "writesubtitles": True, 
    "writeautomaticsub": True, 
    "skip_download": True,    
    "quiet": True
}

# Extract subtitles
with yt_dlp.YoutubeDL(options) as ydl:
    info = ydl.extract_info(video_url, download=False)
    subtitles = info.get("subtitles") or {}
    print(subtitles, 'original subtitles')
    auto_captions = info.get("automatic_captions") or {}

    if "en" in auto_captions:
        subtitle_url = auto_captions["en"][0]["url"]
        response = requests.get(subtitle_url)

        if response.status_code == 200:
            subtitle_data = response.json()

            # Save as JSON
            json_data = subtitle_data
            with open("subtitles.json", "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=4, ensure_ascii=False)

            print("Subtitles saved as subtitles.json")
        else:
            print("Failed to download subtitles.")
    else:
        print("No auto-generated subtitles found!")



