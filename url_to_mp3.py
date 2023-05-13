import pytube
import os

def url_to_stream(url):
    try:
        yt = pytube.YouTube(url)
    except Exception as e:
        print(e)
        return None
    stream = yt.streams.filter(only_audio=True).first()
    if stream == None:
        return None
    try:
        buff = open("aud", "wb")
    except Exception as e:
        print(e)
        return None
    stream.stream_to_buffer(buffer=buff)
    return "aud"

def search_for(keywords):
    s = pytube.Search(keywords)
    if s == None or len(s.results) == 0:
        return None
    return s.results[0].watch_url
