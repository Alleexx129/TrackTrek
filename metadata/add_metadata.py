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
    track_title = re.sub(r'[^a-zA-Z0-9\s-]', '', track_title)
    search_url = str(f'https://genius.com/{artist_name.replace(" ", "-")}-{track_title.replace(" ", "-")}-lyrics').replace("--", "-").replace("--", "-")
    response = requests.get(search_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        album_tags = soup.find_all('a', class_="StyledLink-sc-15c685a-0 lnzQV")
        genresContainer = soup.find_all('div', class_='SongTags-sc-b55131f0-1 jJPHqT')
        genres = []

        for tag in genresContainer:
            genre_links = tag.find_all('a')
            for link in genre_links:
                genres.append(link.text.strip())

        album_names = []

        for tag in album_tags:
            album_names.append(tag.get_text(strip=True))
            
        if len(album_names) == 0:
            album_names.append("Youtube")
        if len(genres) == 0:
            genres.append("Unknown")
        album_name = album_names[0]
        genre = genres[0]

        lyrics_divs = soup.find_all('div', class_='Lyrics-sc-1bcc94c6-1 bzTABU')
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
                
                if img.format == 'WEBP':
                    img = img.convert('RGB')

                img_resized = resize_image(img)
                img_format = 'JPEG'

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
            else:
                print("Thumbnail download failed with status code:", artwork_response.status_code)
        except Exception as e:
            print(f"Error adding artwork: {e}")
    else:
        print("No thumbnail URL found; skipping artwork addition.")


    audio.save()