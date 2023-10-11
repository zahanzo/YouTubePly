import yt_dlp
import requests
import re
import threading

def search_youtube(query):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
        'default_search': 'auto',
        'max_downloads': 10
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        results = ydl.extract_info(f'ytsearch{10}:{query}', download=False)

    video_list = []
    for entry in results['entries']:
        title = entry['title']
        video_url = entry['url']

        title = re.sub(r'[^\x00-\x7F]+', '', title)

        video_id = entry['id']
        thumbnail_url = f'https://img.youtube.com/vi/{video_id}/mqdefault.jpg'

        video_list.append({"title": title, "url": video_url, "thumbnail_url": thumbnail_url})

    return video_list

def download_thumbnail(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as file:
        file.write(response.content)

def download_all_thumbnails(results):
    threads = []

    for i, result in enumerate(results, start=1):
        thumbnail_filename = re.sub(r'[^\x00-\x7F]+', '', f"thumbnail_{i}.jpg")

        thread = threading.Thread(target=download_thumbnail, args=(result['thumbnail_url'], thumbnail_filename))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    #query = input("Digite sua busca no YouTube: ")

    results = search_youtube("surene")

    if not results:
        print("Nenhum resultado encontrado.")
    else:
        for i, result in enumerate(results, start=1):
            print(f"{i}. Título: {result['title']}")
            print(f"   URL: {result['url']}")

        download_all_thumbnails(results)
        print("Thumbnails baixadas com sucesso.")