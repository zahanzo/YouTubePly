import sys
import yt_dlp
import re
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import requests
from PIL import Image
from io import BytesIO
import os

class YouTubeSearchApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Pesquisa no YouTube')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        label_logo = QLabel(self)
        pixmap = QPixmap('logo.png')
        label_logo.setPixmap(pixmap)
        label_logo.setAlignment(Qt.AlignLeft)
        layout.addWidget(label_logo)

        label = QLabel('Digite sua busca no YouTube:', self)
        layout.addWidget(label)

        self.entry = QLineEdit(self)
        self.entry.returnPressed.connect(self.showResults)
        layout.addWidget(self.entry)

        self.button_search = QPushButton('Buscar', self)
        self.button_search.clicked.connect(self.showResults)
        layout.addWidget(self.button_search)

        self.label_result = QLabel(self)
        layout.addWidget(self.label_result)

        self.widget_results = QWidget(self)
        layout.addWidget(self.widget_results)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def downloadThumbnail(self, url, filename):
        if not os.path.exists(filename):
            response = requests.get(url)
            if response.status_code == 200:
                img_data = BytesIO(response.content)
                image = Image.open(img_data)
                image.save(filename)
            else:
                print(f"Erro ao baixar a thumbnail: {response.status_code}")
        else:
            print(f"O arquivo {filename} já existe, pulando o download.")

    def showResults(self):
        query = self.entry.text()
        results = self.searchYouTube(query)

        if not results:
            self.label_result.setText("Nenhum resultado encontrado.")
        else:
            self.label_result.setText("Resultados:")

            self.widget_results.deleteLater()
            self.widget_results = QWidget(self)
            layout = QVBoxLayout()

            for i, result in enumerate(results, start=1):
                thumbnail_filename = f"thumbnail_{i}.jpg"
                self.downloadThumbnail(result['thumbnail_url'], thumbnail_filename)

                label_image = QLabel(self)
                pixmap = QPixmap(thumbnail_filename)
                label_image.setPixmap(pixmap)
                label_image.setAlignment(Qt.AlignLeft)
                layout.addWidget(label_image)

                label_title = QLabel(f"{i}. Título: {result['title']}", self)
                layout.addWidget(label_title)

            self.widget_results.setLayout(layout)
            self.setCentralWidget(self.widget_results)

    def searchYouTube(self, query):
        ydl_opts = {
        'format': 'best',
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
        'default_search': 'auto',
        'max_downloads': 50
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = YouTubeSearchApp()
    ex.show()
    sys.exit(app.exec_())