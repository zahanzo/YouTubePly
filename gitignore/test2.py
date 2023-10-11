import yt_dlp
import requests
import re
import threading
from tkinter import *
from PIL import Image, ImageTk
from pytube import YouTube
import vlc

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

def show_results():
    query = entry.get()
    results = search_youtube(query)

    if not results:
        label_result.config(text="Nenhum resultado encontrado.", fg="white")
    else:
        label_result.config(text="Resultados:", fg="white")

        for i, result in enumerate(results, start=1):
            thumbnail_filename = re.sub(r'[^\x00-\x7F]+', '', f"thumbnail_{i}.jpg")
            download_thumbnail(result['thumbnail_url'], thumbnail_filename)

            image = Image.open(thumbnail_filename)
            image.thumbnail((100, 100))
            photo = ImageTk.PhotoImage(image)

            frame_result = Frame(canvas_frame, bg="black")
            frame_result.grid(row=i, column=0, sticky=W)

            label_image = Label(frame_result, image=photo, bg="black")
            label_image.image = photo
            label_image.grid(row=0, column=0, sticky=W)

            label_title = Label(frame_result, text=f"{i}. Título: {result['title']}", anchor="w", justify=LEFT,
                                fg="white", bg="black", font=("Arial", 12, "bold"))
            label_title.grid(row=0, column=1, sticky=W)

            label_image.bind("<Button-1>", lambda event, url=result['url']: open_video(url))
            label_title.bind("<Button-1>", lambda event, url=result['url']: open_video(url))



def open_video(url):
    Instance = vlc.Instance()
    player = Instance.media_player_new()

    video_url = YouTube(url).streams.get_highest_resolution().url

    Media = Instance.media_new(video_url)
    Media.get_mrl()

    player.set_media(Media)
    player.play()

def search_on_enter(event):
    show_results()


if __name__ == "__main__":
    window = Tk()
    window.title("Pesquisa no YouTube")
    window.geometry("800x600")  # Definindo um tamanho fixo para a janela
    window.configure(bg="black")  # Configurando o fundo para preto

    search_frame = Frame(window, bg="black")
    search_frame.grid(row=0, column=0, sticky=W)  # Alinhando à esquerda

    label = Label(search_frame, text="Digite sua busca no YouTube:", fg="white", bg="black")
    label.grid(row=0, column=0, sticky=W)

    entry = Entry(search_frame, fg="white", bg="black")
    entry.grid(row=0, column=1)
    entry.focus()  # Definindo o foco na entrada
    entry.bind("<Return>", search_on_enter)  # Adicionando evento para a tecla Enter

    button_search = Button(search_frame, text="Buscar", command=show_results, fg="white", bg="black")
    button_search.grid(row=0, column=2, padx=(5,0))  # Adicionando algum espaço entre a entrada e o botão

    label_result = Label(window, text="", fg="white", bg="black")
    label_result.grid(row=1, column=0, sticky=W)

    # Centralizando a barra de pesquisa na horizontal
    window.grid_columnconfigure(1, weight=1)

    
    # Criando um frame com uma barra de rolagem
    canvas = Canvas(window, bg="black")
    canvas.grid(row=2, column=0, sticky=N+S+E+W)

    scrollbar = Scrollbar(window, command=canvas.yview)
    scrollbar.grid(row=2, column=1, sticky=N+S)

    canvas.config(yscrollcommand=scrollbar.set)
    
    # Adicionando evento de rolagem do mouse
    canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))

    canvas_frame = Frame(canvas, bg="black")
    canvas.create_window((0, 0), window=canvas_frame, anchor='nw')

    window.grid_rowconfigure(2, weight=1)
    window.grid_columnconfigure(0, weight=1)

    # Atualizar a configuração do canvas quando o tamanho do canvas_frame mudar
    def on_canvas_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    canvas_frame.bind("<Configure>", on_canvas_frame_configure)

    window.mainloop()