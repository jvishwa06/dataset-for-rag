import os
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
from urllib.parse import urlparse, parse_qs

OUTPUT_DIR = "transcripts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            p = parse_qs(parsed_url.query)
            return p.get('v', [None])[0]
    return url

def format_timestamp(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def get_video_title(url):
    with yt_dlp.YoutubeDL({'quiet': True,  'no_warnings': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get('title', 'video')
    
video_urls = [
    "https://www.youtube.com/watch?v=aircAruvnKk",
    "https://www.youtube.com/watch?v=wjZofJX0v4M",
    "https://www.youtube.com/watch?v=fHF22Wxuyw4",
    "https://www.youtube.com/watch?v=C6YtPJxNULA"
]

ytt_api = YouTubeTranscriptApi()

for url in video_urls:
    video_id = get_video_id(url)
    print(f"\nFetching transcript for: {video_id}")

    try:
        title = get_video_title(url)

        safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "_")).strip()
        safe_title = safe_title.replace(" ", "_")

        fetched_transcript = ytt_api.fetch(video_id, languages=['en', 'hi'])
        transcript = fetched_transcript.to_raw_data()

        file_path = os.path.join(OUTPUT_DIR, f"{safe_title}_{video_id}.txt")

        with open(file_path, "w", encoding="utf-8") as f:
            for entry in transcript:
                timestamp = format_timestamp(entry['start'])
                text = entry['text'].replace('\n', ' ').strip()
                f.write(f"[{timestamp}] {text}\n")

        print(f"Saved to: {file_path}")

    except Exception as e:
        print(f"Error for {video_id}: {e}")