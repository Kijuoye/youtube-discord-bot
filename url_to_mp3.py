import pytube
import os

def url_to_mp3(url):
    try:
        yt = pytube.YouTube(url)
    except:
        return "Invalid URL"
    stream = yt.streams.filter(only_audio=True).first()
    try:
        if os.path.exists("audio.mp3"):
            os.remove("audio.mp3")
    except PermissionError:
        return "PermissionError"
    stream.download(filename="audio.mp3")
    return "audio.mp3"

def search_for(keywords):
    s = pytube.Search(keywords)
    return s.results[0].watch_url
