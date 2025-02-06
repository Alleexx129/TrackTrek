import yt_dlp
from metadata import add_metadata_to_mp3
from utils import is_valid_youtube_url, search_video, loggerOutputs
from download import download_audio
import re

def main():
    keyword = input("text: ")
    print("Loading...")

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
    else:
        video_results = search_video(keyword)
        if not video_results:
            print("No results found.")
            return

        print("\nTop 5 search results:")
        for i, video in enumerate(video_results[:5], start=1):
            print(f"{i}. {video['title']} by {video['uploader']} (Views: {video['view_count']})")

        selection = int(input("\nSelect a video (1-5): ")) - 1
        if selection < 0 or selection >= 5:
            print("Invalid selection.")
            return
        print("Loading...")

        selected_video = video_results[selection]
        video_url = selected_video['url']
        video_title = re.sub(r'[\(\[].*?[\)\]]', '', selected_video['title']).strip()
        video_artist = str(selected_video.get("uploader", "Error")).replace(" official", "").replace(" Official", "")
        artwork_url = selected_video.get('thumbnail', None)
    output_file = download_audio(video_url, video_title, video_artist)
    print(f"Download complete: {output_file}")
    print(artwork_url)
    add_metadata_to_mp3(output_file, {
        'title': video_title,
        'artist': video_artist,
        'artwork_url': artwork_url,
        'release_date': video_info.get('upload_date', None) if 'video_info' in locals() else selected_video.get('upload_date', None)
    })


if __name__ == "__main__":
    main()
