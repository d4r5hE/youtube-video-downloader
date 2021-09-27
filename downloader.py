import requests
import pandas as pd
from tqdm import tqdm
import ffmpeg
import os
import sys

#url = "https://www.youtube.com/watch?v=a3ICNMQW7Ok"
url = sys.argv[1]


def GET_VIDEO_ID(url):
    x = url.split("=")
    return x[-1]

def download(url: str, fname: str):
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get('content-length', 0))
    with open(fname, 'wb') as file, tqdm(
        desc=fname,
        total=total,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)


def merge_audio_video(video_file,audio_file,file_name):
    video = ffmpeg.input(video_file)
    audio = ffmpeg.input(audio_file)
    out = ffmpeg.output(video, audio, file_name, vcodec='copy')
    out.run()

r = requests.get(url)

x = r.content.decode("utf-8")

innertubeApiKey = (((x.split('"innertubeApiKey":"'))[1]).split('"'))[0]

#print(innertubeApiKey)



data = {
    "context": {
        "client": {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36,gzip(gfe)",
            "clientName": "WEB",
            "clientVersion": "2.20210924.00.00",
        }
    },
    "videoId": f"{GET_VIDEO_ID(url)}",
}


res = requests.post(f"https://www.youtube.com/youtubei/v1/player?key={innertubeApiKey}",data=str(data))
#print(res.json())

x = res.json()


best = x['streamingData']['formats']
all = x['streamingData']['adaptiveFormats']

title = x['videoDetails']['title']

print(title)


format_code = []
extensions = []
resolution = []
bitrate = []
quality = []
audio_rate = []
fps = []
size = []
download_urls = []
d_type = []

all = best + all

for i in all:
    TYPE = ((str(i['mimeType'])).split('/'))[0]
    I_TAG = str(i['itag'])
    EXTENTION = ((((str(i['mimeType'])).split("/"))[-1]).split(";"))[0]
    BITRATE = str(int((int(i['bitrate'])) / 1024)) + 'k'
    RESOLUATION = 'audio'
    if 'width' in i:
        RESOLUATION = str(i['width']) + 'x' + str(i['height'])
    QUALITY = ''
    if "qualityLabel" in i:
        QUALITY = i['qualityLabel']
    AUDIO_RATE = ''
    if "audioSampleRate" in i:
        AUDIO_RATE = f"{i['audioSampleRate']}{'Hz'}"
    SIZE = ''
    if 'contentLength' in i:
        SIZE = f"{int((int(i['contentLength'])) / 1024)}k"
    FPS = ''
    if 'fps' in i:
        FPS = str(i['fps']) + "fps"
    DOWNLOAD_URLS = ''
    if 'url' in i:
        DOWNLOAD_URLS = i['url']

    format_code.append(I_TAG)
    extensions.append(EXTENTION)
    resolution.append(RESOLUATION)
    bitrate.append(BITRATE)
    quality.append(QUALITY)
    audio_rate.append(AUDIO_RATE)
    fps.append(FPS)
    size.append(SIZE)
    download_urls.append(DOWNLOAD_URLS)
    d_type.append(TYPE)

d = {'resolution':resolution,'quality':quality,'format code': format_code, 'extensions': extensions,'bitrate':bitrate,'audio_rate':audio_rate,'size':size}
df = pd.DataFrame(data=d)
print(df)

x = int(input("Enter video format NO: "))
if d_type[x] == 'video':
    download_url_video = download_urls[x]
else:
    raise IndexError


y = int(input("Enter audio format NO: "))
if d_type[y] == 'audio':
    download_url_audio = download_urls[y]
else:
    raise IndexError



video_file = GET_VIDEO_ID(url) +"vid."+ extensions[x]
audio_file = GET_VIDEO_ID(url) +"aud."+ extensions[y]
file_name = title+'.mp4'

download(download_url_video,video_file)
download(download_url_audio,audio_file)

merge_audio_video(video_file,audio_file,file_name)

os.remove(audio_file)
os.remove(video_file)
