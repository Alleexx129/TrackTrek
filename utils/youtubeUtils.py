import re
import yt_dlp

class loggerOutputs:
    def error(msg):
        pass
    def warning(msg):
        pass
    def debug(msg):
        pass

def is_valid_youtube_url(url):
    return re.match(r'^https?://(www\.)?(youtube\.com|youtu\.?be)/.+$', url) is not None


def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def search_video(query):
    search_opts = {
        'quiet': True,
        'format': 'bestaudio/best',
        "logger": loggerOutputs,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(search_opts) as ydl:
        search_result = ydl.extract_info(f"ytsearch5:{query}", download=False)
        return search_result['entries'] if 'entries' in search_result else []