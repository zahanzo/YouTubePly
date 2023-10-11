url = "https://www.youtube.com/watch?v=Wj8--qbiGyw"

from urllib import request

# URL do vídeo
video_url = url

# Criar um cabeçalho simulando um navegador
headers = {'User-Agent': 'Mozilla/5.0'}

# Criar uma requisição com o cabeçalho
req = request.Request(video_url, headers=headers)

# Fazer a requisição
response = request.urlopen(req)

# Ler o conteúdo da resposta
html = response.read().decode()

# Encontrar o URL do vídeo
start = html.find('https://r')  # Início do URL
end = html.find('",', start)   # Fim do URL

video_direct_url = html[start:end]
response = request.urlopen(video_direct_url)

print("URL Direta do Vídeo:", video_direct_url)