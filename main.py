import yt_dlp
from utils import is_valid_youtube_url, search_video, loggerOutputs, sanitize_filename
from download import download_audio
from metadata import add_metadata_to_mp3
import json
import sys
import os
import asyncio
import re

TEMP_JSON_PATH = "./temp.json"
downloading = False

dataLock = asyncio.Lock()
 
async def search_and_save(keyword):
    global downloading
    try:
        if is_valid_youtube_url(keyword):
            ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'http_chunk_size': 1024 * 1024,
            'concurrent_fragments': 10,
            'format': 'bestaudio/best',
            "logger": loggerOutputs,
            'noplaylist': True,
            }
            video_url = keyword
            video_info = yt_dlp.YoutubeDL(ydl_opts).extract_info(video_url, download=False)
            video_title = re.sub(r'[\(\[].*?[\)\]]', '', video_info['title']).strip()
            video_artist = str(video_info["uploader"]).replace(" official", "").replace(" Official", "")
            artwork_url = video_info.get('thumbnail')

            output_file = download_audio(video_url, video_title, video_artist)
            add_metadata_to_mp3(output_file, {
                'title': video_title,
                'artist': video_artist,
                'artwork_url': artwork_url,
                'release_date': video_info.get('upload_date', None) if 'video_info' in locals() else video_info.get('upload_date', None)
            })
            print(json.dumps({"message": f"Download complete: {video_info['title']}"}))
            return
        
        
        video_results = search_video(keyword)
        if downloading == True:
            return
        if not video_results:
            print(json.dumps({"error": "No results found."}))
            return

        video_data = video_results
        async with dataLock:
            with open(TEMP_JSON_PATH, 'w+') as f:
                json.dump(video_data, f, indent=4)

        titles = [{"index": i, "title": video['title']} for i, video in enumerate(video_data)]
        print(json.dumps(titles))

    except Exception as e:
        print(json.dumps({"error": str(e)}))

async def download_video(title):
    global downloading
    downloading = True
    try:
        if not os.path.exists(TEMP_JSON_PATH):
            print(json.dumps({"error": "No search results found. Please search first."}))
            return
        
        async with dataLock:
            with open(TEMP_JSON_PATH, 'r') as f:
                video_data = json.load(f)

        if not isinstance(video_data, list):
            print(json.dumps({"error": "Unexpected JSON format; expected a list of videos."}))
            return

        selected_video = next((vid for vid in video_data if vid["title"] == title), None)
        
        if selected_video is None:
            print(json.dumps({"error": f"Video with title '{title}' not found in search results."}))
            return

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'http_chunk_size': 1024 * 1024,
            'concurrent_fragments': 10,
            'format': 'bestaudio/best',
            "logger": loggerOutputs,
            'noplaylist': True,
            'outtmpl': sanitize_filename(selected_video["title"]),
        }
        artist = str(selected_video["uploader"]).replace(" official", "").replace(" Official", "")
        output_file = download_audio(selected_video["url"], selected_video["title"], selected_video["uploader"])

        add_metadata_to_mp3(output_file, {
            'title': selected_video["title"],
            'artist': artist,
            'artwork_url': selected_video["thumbnail"],
            'release_date': selected_video.get('upload_date')
        })
        
        print(json.dumps({"message": f"Download complete: {selected_video['title']}"}))
        

    except Exception as e:
        print(json.dumps({"error": str(e)}))
    downloading = False


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "search":
        asyncio.run(search_and_save(" ".join(sys.argv[2:])))
    elif len(sys.argv) > 2 and sys.argv[1] == "download":
        asyncio.run(download_video(" ".join(sys.argv[2:])))
    else:
        print(json.dumps({"error": "Invalid arguments."}))