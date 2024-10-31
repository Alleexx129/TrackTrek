from utils.youtubeUtils import sanitize_filename, loggerOutputs
import yt_dlp

def download_audio(video_url, title, artist):
    sanitized_title = sanitize_filename(f"{title} - {artist}")
    output_template = f"./{sanitized_title}"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': output_template,
        'quiet': True,
        'http_chunk_size': 1024 * 1024,
        'concurrent_fragments': 10,
        'format': 'bestaudio/best',
        "logger": loggerOutputs,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
    except Exception as e:
        if "nsig extraction failed" in str(e):
            print("Warning suppressed: nsig extraction failed. You may experience throttling for some formats.")
        else:
            print(f"An error occurred: {e}")

    return output_template + ".mp3"