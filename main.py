import os
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
from urllib.parse import urlparse, parse_qs
import time

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
    with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get('title', 'video')

video_urls = [
    "https://www.youtube.com/watch?v=aircAruvnKk",
    "https://www.youtube.com/watch?v=wjZofJX0v4M",
    "https://www.youtube.com/watch?v=fHF22Wxuyw4",
    "https://www.youtube.com/watch?v=C6YtPJxNULA"
]

# Set your desired interval
INTERVAL = 15 
# Delay between requests to avoid IP blocking (in seconds)
REQUEST_DELAY = 5

for url in video_urls:
    video_id = get_video_id(url)
    print(f"\nFetching transcript for: {video_id}")
    
    # Add delay between requests to avoid rate limiting
    time.sleep(REQUEST_DELAY)

    try:
        title = get_video_title(url)
        safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "_")).strip().replace(" ", "_")

        # FIX: Use fetch() method instead of get_transcript()
        transcript_list = YouTubeTranscriptApi().fetch(video_id, languages=['en', 'hi'])

        file_path = os.path.join(OUTPUT_DIR, f"{safe_title}_{video_id}.txt")

        with open(file_path, "w", encoding="utf-8") as f:
            current_interval_limit = INTERVAL
            current_text_batch = []
            
            # Start time for the very first block
            block_start_time = 0

            for entry in transcript_list:
                # If this entry starts after our current 15s window
                while entry.start >= current_interval_limit:
                    if current_text_batch:
                        timestamp = format_timestamp(block_start_time)
                        combined_text = " ".join(current_text_batch).replace('\n', ' ').strip()
                        f.write(f"[{timestamp}] {combined_text}\n")
                        current_text_batch = []
                    
                    # Move to the next 15s window
                    block_start_time = current_interval_limit
                    current_interval_limit += INTERVAL

                current_text_batch.append(entry.text)

            # Write the final remaining batch if it exists
            if current_text_batch:
                timestamp = format_timestamp(block_start_time)
                combined_text = " ".join(current_text_batch).replace('\n', ' ').strip()
                f.write(f"[{timestamp}] {combined_text}\n")

        print(f"Saved to: {file_path}")

    except Exception as e:
        print(f"Error for {video_id}: {e}")