from mutagen.mp3 import MP3
from mutagen.id3 import ID3, ID3NoHeaderError, TIT2, TPE1, TALB, TCON, TDRC, COMM, APIC, USLT
from PIL import Image
import requests
from .resize import resize_image
from io import BytesIO
import re
from bs4 import BeautifulSoup
import requests
import re
from bs4 import BeautifulSoup

def getOtherInfos(track_title, artist_name):
    track_title = re.sub(r'[^a-zA-Z0-9\s]', '', track_title)
    # Format the Genius search URL with song title and artist
    search_url = str(f'https://genius.com/{artist_name.replace(" ", "-")}-{track_title.replace(" ", "-")}-lyrics').replace("--", "-")
    response = requests.get(search_url)
    
    if response.status_code == 200:
        # "collects" (or straight up webscraping) if you prefer
        soup = BeautifulSoup(response.text, 'html.parser')
        
        album_tags = soup.find_all('a', class_='StyledLink-sc-3ea0mt-0 ietQTa')
        genresContainer = soup.find_all('div', class_='SongTags__Container-xixwg3-1 bZsZHM')
        genres = []

        # Extract and print the text of each genre tag
        for tag in genresContainer:
            genre_links = tag.find_all('a')
            for link in genre_links:
                genres.append(link.text.strip())

        # Initialize an empty list to store album names
        album_names = []

        for tag in album_tags:
            href = tag.get('href', '')
            # Check if '#primary-album' is in href
            if '#primary-album' in href:
                album_names.append(tag.get_text(strip=True))
            
        if len(album_names) == 0:
            album_names.append("Youtube")
        if len(genres) == 0:
            genres.append("Unknown")
        album_name = album_names[0]
        genre = genres[0]

        # Extract lyrics by finding all relevant divs
        lyrics_divs = soup.find_all('div', class_='Lyrics__Container-sc-1ynbvzw-1')
        lyrics = "\n".join(div.get_text(strip=True) for div in lyrics_divs)
        lyrics = re.sub(r"(\w)([A-Z])", r"\1 \2", lyrics)
        lyrics = re.sub(r'\[', '\n\n[', lyrics)
        lyrics = re.sub(r'\]', '] ', lyrics)
        return [album_name, genre, lyrics if lyrics else ""]
    
    else:
        return "Youtube", "Unknown", ""


def add_metadata_to_mp3(file_path, info):
    try:
        audio = MP3(file_path, ID3=ID3)
    except ID3NoHeaderError:
        audio.add_tags()

    otherInfos = getOtherInfos(info['title'], info['artist'])

    audio['TIT2'] = TIT2(encoding=3, text=info['title'])
    audio['TPE1'] = TPE1(encoding=3, text=info['artist'])
    audio['TALB'] = TALB(encoding=3, text=otherInfos[0])
    audio['TCON'] = TCON(encoding=3, text=otherInfos[1])
    audio['USLT'] = USLT(encoding=3, text=otherInfos[2])

    if info.get('release_date'):
        audio['TDRC'] = TDRC(encoding=3, text=info['release_date'])

    artwork_url = info.get('artwork_url', None)
    if artwork_url:
        try:
            artwork_response = requests.get(artwork_url, stream=True)
            if artwork_response.status_code == 200:
                img = Image.open(BytesIO(artwork_response.content))
                img_resized = resize_image(img)
                img_format = 'JPEG' if img.format == 'WEBP' else img.format
                with BytesIO() as output:
                    img_resized.save(output, format=img_format)
                    output.seek(0)
                    audio['APIC'] = APIC(
                        encoding=3,
                        mime='image/jpeg',
                        type=3,
                        desc='Cover',
                        data=output.getvalue()
                    )
        except Exception as e:
            print(f"Error adding artwork: {e}")

    audio.save()