import yt_dlp
import requests
import re
import threading
from tkinter import *
from PIL import Image, ImageTk
from pytube import YouTube
from os import system, path


def search_youtube(query):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
        'default_search': 'auto',
        'max_downloads': 50
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        results = ydl.extract_info(f'ytsearch{20}:{query}', download=False)

    video_list = []
    for entry in results['entries']:
        title = entry['title']
        video_url = entry['url']
        title = re.sub(r'[^\x00-\x7F]+', '', title)

        video_id = entry['id']
        thumbnail_url = f'https://img.youtube.com/vi/{video_id}/default.jpg'
        video_list.append({"title": title, "url": video_url, "thumbnail_url": thumbnail_url})

    return video_list


def download_thumbnail(url, filename):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(f"images/{filename}", 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
    else:
        print(f"Erro ao baixar a thumbnail, setando a padrão.")



def download_all_thumbnails(results):
    threads = []
    for i, result in enumerate(results, start=1):
        thumbnail_filename = re.sub(r'[^\x00-\x7F]+', '', f"thumbnail_{i}.jpg")
        thread = threading.Thread(target=download_thumbnail, args=(result['thumbnail_url'], thumbnail_filename))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def show_results():
    query = search_entry.get()
    results = search_youtube(query)

    if not results:
        label_result.config(text="Nenhum resultado encontrado.", fg="black", bg="#fbd904")
    else:
        label_result.config(text="Resultados:", fg="black", bg="#fbd904")
        download_all_thumbnails(results)

        for i, result in enumerate(results, start=1):
            thumbnail_filename = re.sub(r'[^\x00-\x7F]+', '', f"thumbnail_{i}.jpg")

            if not path.exists(f"images/{thumbnail_filename}"):
                image = Image.open("images/default_thumbnail.jpg")
            else:
                image = Image.open(f"images/{thumbnail_filename}")
                
            image.thumbnail((100, 100))
            photo = ImageTk.PhotoImage(image)

            frame_result = Frame(canvas_frame, bg="#fbd904")  
            frame_result.grid(row=i, column=0, sticky=W)

            label_image = Label(frame_result, image=photo, bg="#fbd904")  
            label_image.image = photo
            label_image.grid(row=0, column=0, sticky=W)

            label_title = Label(frame_result, text=f"{result['title']}", anchor="w", justify=LEFT,
                                fg="black", bg="#fbd904", font=("Arial", 12, "bold"))  
            label_title.grid(row=0, column=1, sticky=W)

            label_image.bind("<Button-1>", lambda event, url=result['url']: open_video(url))
            label_title.bind("<Button-1>", lambda event, url=result['url']: open_video(url))


def open_video(*args):
    if not args:
        url = url_entry.get()
    else:
        url = args[0]
    video_url = YouTube(url).streams.get_highest_resolution().url
    system(f'player\\vlc.exe "{video_url}"')


def video_on_enter(event):
    open_video()

def search_on_enter(event):
    show_results()


def on_canvas_configure(event):
    canvas.itemconfig(canvas_frame_id, width=event.width)


def on_canvas_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.itemconfig(canvas_frame_id, width=event.width)


if __name__ == "__main__":
    player = None
    window = Tk()
    window.title("YouTubePly ~ by 0xrobert")
    window.geometry("600x600")
    window.configure(bg="#fbd904")
    window.grid_columnconfigure(1, weight=1)

    search_frame = Frame(window, bg="#fbd904")
    search_frame.grid(row=0, column=0, sticky=W)

    logo_image = Image.open("images/logo.png")
    logo_image.thumbnail((120, 120))
    logo_photo = ImageTk.PhotoImage(logo_image)

    logo_label = Label(search_frame, image=logo_photo, bg="#fbd904")
    logo_label.grid(row=0, column=2, sticky=W, padx=(0, 240))

    search_entry = Entry(search_frame, fg="white", bg="#fbd904")
    search_entry.grid(row=0, column=2, padx=(0,0))
    search_entry.focus()
    search_entry.bind("<Return>", search_on_enter)

    button_search = Button(search_frame, text="Buscar", command=show_results, fg="black", bg="#fbd904")
    button_search.grid(row=0, column=2, padx=(180,0))

    #####
    url_entry = Entry(search_frame, fg="white", bg="#fbd904")
    url_entry.grid(row=0, column=3)
    url_entry.bind("<Return>", video_on_enter)

    button_url = Button(search_frame, text="Ir para url", command=open_video, fg="black", bg="#fbd904")
    button_url.grid(row=0, column=4, padx=(5, 0))

    label_result = Label(window, text="", fg="black", bg="#fbd904")
    label_result.grid(row=1, column=0, sticky=W)
    
    # Criando um frame com uma barra de rolagem
    canvas = Canvas(window, bg="#fbd904", width=600)
    canvas.grid(row=2, column=0, sticky=N+S+E+W)

    scrollbar = Scrollbar(window, command=canvas.yview)
    scrollbar.grid(row=2, column=2, sticky=N+S, padx=(0,5))

    canvas.config(yscrollcommand=scrollbar.set)
    canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))

    canvas_frame = Frame(canvas, bg="#fbd904")
    canvas_frame_id = canvas.create_window((0, 0), window=canvas_frame, anchor='nw')

    window.grid_rowconfigure(2, weight=1)
    window.grid_columnconfigure(0, weight=1)

    # Atualizar a configuração do canvas quando o tamanho do canvas_frame mudar
    canvas.bind("<Configure>", on_canvas_configure)
    canvas_frame.bind("<Configure>", on_canvas_frame_configure)

    window.mainloop()
