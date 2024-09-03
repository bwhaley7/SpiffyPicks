import requests
import yt_dlp as youtube_dl
import os
import re
import xml.etree.ElementTree as ET
from dotenv import load_dotenv, find_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv(find_dotenv())

def normalize_filename(filename):
    name, ext = os.path.splitext(filename)
    normalized = re.sub(r'[^\w\s-]', '', name)  
    normalized = normalized.replace(' ', '_').lower() 
    return f"{normalized}{ext}"  

def file_already_exists(download_folder, video_title):
    normalized_title = normalize_filename(video_title)
    for file in os.listdir(download_folder):
        #print(f"{normalize_filename(file)} not equal to: {normalized_title}.m4a")
        if normalize_filename(file) == f"{normalized_title}.m4a":
            return True
    return False

def download_youtube_audio(video_url, download_folder):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a', 
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
            'ffmpeg_location': 'D:/FFMPEG/bin',
            'quiet': True, 
            'noprogress': False 
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            video_title = info_dict.get('title', None)

        if video_title and file_already_exists(download_folder, video_title):
            print(f"File already exists, skipping download: {video_title}")
            return

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        print(f"Downloaded audio from {video_url}")
    except Exception as e:
        print(f"Failed to download audio from {video_url}: {e}")

def fetch_rss_feed(rss_url):
    response = requests.get(rss_url)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Failed to fetch RSS feed: {response.status_code}")
        return None

def parse_youtube_rss_feed(rss_content):
    root = ET.fromstring(rss_content)
    video_urls = []
    one_week_ago = datetime.now(timezone.utc) - timedelta(weeks=1)

    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        published_element = entry.find("{http://www.w3.org/2005/Atom}published")
        if published_element is not None:
            published_date = datetime.strptime(published_element.text, '%Y-%m-%dT%H:%M:%S%z')
            if published_date > one_week_ago:
                video_id_element = entry.find("{http://www.youtube.com/xml/schemas/2015}videoId")
                if video_id_element is not None:
                    video_id = video_id_element.text
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    video_urls.append(video_url)

    return video_urls

def parse_podcast_rss_feed(rss_content):
    root = ET.fromstring(rss_content)
    audio_urls = []
    one_week_ago = datetime.now(timezone.utc) - timedelta(weeks=1)

    for item in root.findall("channel/item"):
        pub_date = item.find("pubDate").text
        pub_date_dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
        
        if pub_date_dt > one_week_ago:
            enclosure = item.find("enclosure")
            title = item.find("title").text
            if enclosure is not None and enclosure.get("type") == "audio/mpeg":
                audio_url = enclosure.get("url")
                audio_urls.append((audio_url, title))

    return audio_urls

def download_podcast_audio(audio_url, download_folder, filename):
    try:
        normalized_filename = normalize_filename(filename) + ".m4a"
        file_path = os.path.join(download_folder, normalized_filename)

        if os.path.exists(file_path):
            print(f"File already exists, skipping download: {file_path}")
            return

        response = requests.get(audio_url, stream=True)
        if response.status_code == 200:
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            print(f"Downloaded: {filename}")
        else:
            print(f"Failed to download podcast audio from {audio_url}: {response.status_code}")
    except Exception as e:
        print(f"Failed to download podcast audio from {audio_url}: {e}")

def main():
    youtube_rss_urls = [
        "https://www.youtube.com/feeds/videos.xml?channel_id=UCiWLfSweyRNmLpgEHekhoAg",
        "https://www.youtube.com/feeds/videos.xml?playlist_id=PL1H2IyN18L0QLfHOno841xcWQu_Sma-CQ"
    ]
    podcast_rss_url = "https://lateround.libsyn.com/rss"
    download_folder = os.getenv('AUDIO_PATH')

    # Process YouTube RSS feeds
    for rss_url in youtube_rss_urls:
        rss_content = fetch_rss_feed(rss_url)
        if rss_content:
            video_urls = parse_youtube_rss_feed(rss_content)
            for video_url in video_urls:
                download_youtube_audio(video_url, download_folder)

    # Process Podcast RSS feed
    rss_content = fetch_rss_feed(podcast_rss_url)
    if rss_content:
        audio_entries = parse_podcast_rss_feed(rss_content)
        for audio_url, title in audio_entries:
            download_podcast_audio(audio_url, download_folder, title)

if __name__ == "__main__":
    main()