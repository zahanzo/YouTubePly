import yt_dlp
import requests
import re
import threading
from tkinter import *
from PIL import Image, ImageTk
from pytube import YouTube
from os import system

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
        label_result.config(text="Nenhum resultado encontrado.", fg="black", bg="#fbd904")
    else:
        label_result.config(text="Resultados:", fg="black", bg="#fbd904")

        download_all_thumbnails(results)

        for i, result in enumerate(results, start=1):
            thumbnail_filename = re.sub(r'[^\x00-\x7F]+', '', f"thumbnail_{i}.jpg")

            image = Image.open(thumbnail_filename)
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




def open_video(url):
    video_url = YouTube(url).streams.get_highest_resolution().url
    system(f'vlc "{video_url}"')  # Chamando o VLC usando os.system
    


def search_on_enter(event):
    show_results()


def on_canvas_configure(event):
    canvas.itemconfig(canvas_frame_id, width=event.width)  # Ajustando a largura do canvas_frame

def on_canvas_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
    canvas.itemconfig(canvas_frame_id, width=event.width)


if __name__ == "__main__":
    player = None  # Inicializando player como None
    window = Tk()
    window.title("YouTubePy ~ by 0xrobert")
    window.geometry("800x600")  # Definindo um tamanho fixo para a janela
    window.configure(bg="#fbd904")  # Configurando o fundo para preto

    search_frame = Frame(window, bg="#fbd904")
    search_frame.grid(row=0, column=0, sticky=W)  # Alinhando à esquerda

    label = Label(search_frame, text="Digite sua busca no YouTube:", fg="black", bg="#fbd904")
    label.grid(row=0, column=0, sticky=W)

    entry = Entry(search_frame, fg="black", bg="#fbd904")
    entry.grid(row=0, column=1)
    entry.focus()  # Definindo o foco na entrada
    entry.bind("<Return>", search_on_enter)  # Adicionando evento para a tecla Enter

    button_search = Button(search_frame, text="Buscar", command=show_results, fg="black", bg="#fbd904")
    button_search.grid(row=0, column=2, padx=(5,0))  # Adicionando algum espaço entre a entrada e o botão

    label_result = Label(window, text="", fg="black", bg="#fbd904")
    label_result.grid(row=1, column=0, sticky=W)

    # Centralizando a barra de pesquisa na horizontal
    window.grid_columnconfigure(1, weight=1)

    
     # Criando um frame com uma barra de rolagem
    canvas = Canvas(window, bg="#fbd904", width=600)  # Aumentando a largura para 1200
    canvas.grid(row=2, column=0, sticky=N+S+E+W)

    #scrollbar = Scrollbar(window, command=canvas.yview)
    #scrollbar.grid(row=2, column=1, sticky=N+S)
    scrollbar = Scrollbar(window, command=canvas.yview)
    scrollbar.grid(row=2, column=2, sticky=N+S, padx=(0,5))  # Colocando na coluna 2 e ajustando o padding

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
